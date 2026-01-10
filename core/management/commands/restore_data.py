import os
import shutil
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections


class Command(BaseCommand):
    help = "Restore database and media from a backup ZIP in BACKUP_DIR (OneDrive)."

    def add_arguments(self, parser):
        parser.add_argument(
            "backup_file",
            nargs="?",
            default=None,
            help="Path to backup ZIP file. If omitted, the latest school_backup_*.zip in BACKUP_DIR is used.",
        )
        parser.add_argument(
            "--file",
            dest="file",
            default=None,
            help="[DEPRECATED] Use positional argument instead. Path to backup ZIP file.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            help="Do not prompt for confirmation (dangerous)",
        )
        parser.add_argument(
            "--only-db",
            action="store_true",
            dest="only_db",
            help="Restore only the database file",
        )
        parser.add_argument(
            "--only-media",
            action="store_true",
            dest="only_media",
            help="Restore only the media directory",
        )
        parser.add_argument(
            "--psql",
            dest="psql_path",
            default=None,
            help="Path to psql executable (for PostgreSQL). If omitted, 'psql' on PATH is used.",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            dest="list_backups",
            help="List all available backups in BACKUP_DIR",
        )

    def handle(self, *args, **options):
        backup_dir = Path(settings.BACKUP_DIR)
        
        # --list: show all backups and exit
        if options.get("list_backups"):
            candidates = sorted(backup_dir.glob("school_backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not candidates:
                self.stdout.write(self.style.WARNING(f"No backups found in {backup_dir}"))
                return
            
            self.stdout.write(self.style.SUCCESS(f"\n📦 Available backups in {backup_dir}:\n"))
            for idx, backup_path in enumerate(candidates, 1):
                mtime = datetime.fromtimestamp(backup_path.stat().st_mtime)
                size_mb = backup_path.stat().st_size / (1024 * 1024)
                is_latest = " ← LATEST" if idx == 1 else ""
                self.stdout.write(f"  {idx}. {backup_path.name}")
                self.stdout.write(f"     Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}{is_latest}")
                self.stdout.write(f"     Size: {size_mb:.2f} MB\n")
            return
        
        # Utiliser le nouvel argument positionnel ou l'option --file (legacy)
        backup_file = options["backup_file"] or options["file"]
        only_db = options.get("only_db")
        only_media = options.get("only_media")
        if only_db and only_media:
            raise CommandError("--only-db and --only-media are mutually exclusive")

        if not backup_file:
            candidates = sorted(backup_dir.glob("school_backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not candidates:
                raise CommandError(f"No backups found in {backup_dir}")
            backup_path = candidates[0]
            self.stdout.write(self.style.NOTICE(f"Using latest backup: {backup_path.name}"))
        else:
            # Essayer le chemin comme donné (absolu ou relatif au cwd)
            backup_path = Path(backup_file).resolve()
            
            # Si le fichier n'existe pas et que le chemin est relatif, essayer depuis BASE_DIR
            if not backup_path.exists() and not Path(backup_file).is_absolute():
                alternative_path = Path(settings.BASE_DIR) / backup_file
                if alternative_path.exists():
                    backup_path = alternative_path
            
            if not backup_path.exists():
                raise CommandError(
                    f"Backup file not found: {backup_file}\n"
                    f"Essayé:\n"
                    f"  1. Comme chemin absolu/relatif: {Path(backup_file).resolve()}\n"
                    f"  2. Depuis BASE_DIR: {Path(settings.BASE_DIR) / backup_file}\n"
                    f"Utilisez un chemin absolu ou utilisez --list pour voir les backups disponibles"
                )

        # Confirm
        if not options.get("force"):
            self.stdout.write(self.style.WARNING("This will overwrite your current database and/or media."))
            self.stdout.write(self.style.WARNING(f"Backup: {backup_path}"))
            try:
                confirm = input("Type 'yes' to continue: ")
            except EOFError:
                confirm = ""
            if confirm.strip().lower() != "yes":
                self.stdout.write("Aborted.")
                return

        db_path = Path(settings.BASE_DIR) / "db.sqlite3"
        media_root = Path(settings.MEDIA_ROOT)
        default_db = settings.DATABASES.get("default", {})
        engine = default_db.get("ENGINE", "")
        is_sqlite = engine.endswith("sqlite3")
        is_postgres = "postgresql" in engine or "postgres" in engine

        # Close all DB connections before replacing sqlite file or running SQL
        try:
            connections.close_all()
        except Exception:
            pass

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            with ZipFile(backup_path, "r") as zf:
                zf.extractall(tmpdir)

            # Pre-restore local safety backup
            local_bak_dir = Path(settings.BASE_DIR) / "backups_local"
            local_bak_dir.mkdir(exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if not only_media:
                # For SQLite: backup the .sqlite3 file
                if is_sqlite and db_path.exists():
                    shutil.copy2(db_path, local_bak_dir / f"db_pre_restore_{stamp}.sqlite3")
                # For PostgreSQL: we'll just log; no file to copy

            if media_root.exists() and not only_db:
                # Save current media as pre-restore
                pre_media = local_bak_dir / f"media_pre_restore_{stamp}"
                try:
                    shutil.copytree(media_root, pre_media)
                except Exception:
                    pass

            # Restore DB
            if not only_media:
                if is_sqlite:
                    # SQLite: restore .sqlite3 file
                    extracted_db = tmpdir / "db.sqlite3"
                    if extracted_db.exists():
                        shutil.copy2(extracted_db, db_path)
                        self.stdout.write(self.style.SUCCESS(f"✓ Restored SQLite database to {db_path}"))
                    else:
                        self.stdout.write(self.style.WARNING("No db.sqlite3 found in backup (skipped)"))
                elif is_postgres:
                    # PostgreSQL: find the dump file and restore via psql
                    dump_candidates = list(tmpdir.glob("db_postgres_*.sql"))
                    if not dump_candidates:
                        self.stdout.write(self.style.WARNING("No PostgreSQL dump found in backup (skipped)"))
                    else:
                        dump_file = dump_candidates[0]
                        host = default_db.get("HOST") or "localhost"
                        port = str(default_db.get("PORT") or "5432")
                        user = default_db.get("USER") or "postgres"
                        name = default_db.get("NAME")
                        password = default_db.get("PASSWORD") or ""

                        if not name:
                            raise CommandError("PostgreSQL database NAME is not configured.")

                        psql_bin = options.get("psql_path") or settings.PSQL_PATH
                        env = os.environ.copy()
                        if password:
                            env["PGPASSWORD"] = password

                        # Restore using psql < dump.sql
                        cmd = [
                            psql_bin,
                            "-h", str(host),
                            "-p", str(port),
                            "-U", str(user),
                            "-d", str(name),
                        ]
                        try:
                            with dump_file.open("rb") as inf:
                                subprocess.run(cmd, stdin=inf, env=env, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                            self.stdout.write(self.style.SUCCESS(f"✓ Restored PostgreSQL database {name}"))
                        except FileNotFoundError:
                            raise CommandError("psql not found. Install PostgreSQL client tools or pass --psql to this command.")
                        except subprocess.CalledProcessError as e:
                            raise CommandError(f"psql restore failed: {e.stderr.decode(errors='ignore')}")

            # Restore media (replace with backup content)
            if not only_db:
                # Determine if backup contains media folder at root
                backup_media = tmpdir / "media"
                if backup_media.exists():
                    # Remove current media and replace fully
                    if media_root.exists():
                        shutil.rmtree(media_root)
                    shutil.copytree(backup_media, media_root)
                    self.stdout.write(self.style.SUCCESS(f"✓ Restored media to {media_root}"))
                else:
                    # Or files at various subpaths starting with 'media/' already extracted into tmpdir.
                    possible = list(tmpdir.glob("media/**/*"))
                    if possible:
                        if media_root.exists():
                            shutil.rmtree(media_root)
                        shutil.copytree(tmpdir / "media", media_root)
                        self.stdout.write(self.style.SUCCESS(f"✓ Restored media to {media_root}"))
                    else:
                        self.stdout.write(self.style.WARNING("No media directory found in backup (skipped)"))

        self.stdout.write(self.style.SUCCESS("Restore complete."))
