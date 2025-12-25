import os
import io
import json
import shutil
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a timestamped backup of the database and media into BACKUP_DIR (OneDrive)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dest",
            dest="dest",
            default=None,
            help="Destination directory for the backup (defaults to settings.BACKUP_DIR)",
        )
        parser.add_argument(
            "--only-db",
            action="store_true",
            dest="only_db",
            help="Backup only the database file",
        )
        parser.add_argument(
            "--only-media",
            action="store_true",
            dest="only_media",
            help="Backup only the media directory",
        )
        parser.add_argument(
            "--pg-dump",
            dest="pg_dump_path",
            default=None,
            help="Path to pg_dump executable (for PostgreSQL). If omitted, 'pg_dump' on PATH is used.",
        )

    def handle(self, *args, **options):
        dest_dir = Path(options["dest"]) if options["dest"] else Path(settings.BACKUP_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"school_backup_{timestamp}.zip"
        backup_path = dest_dir / backup_name

        default_db = settings.DATABASES.get("default", {})
        engine = default_db.get("ENGINE", "")
        is_sqlite = engine.endswith("sqlite3")
        is_postgres = "postgresql" in engine or "postgres" in engine

        db_path = Path(settings.BASE_DIR) / "db.sqlite3"
        media_root = Path(settings.MEDIA_ROOT)

        only_db = options.get("only_db")
        only_media = options.get("only_media")
        if only_db and only_media:
            self.stderr.write(self.style.ERROR("--only-db and --only-media are mutually exclusive"))
            return

        if not only_media:
            if is_sqlite:
                if not db_path.exists():
                    self.stderr.write(self.style.ERROR(f"SQLite database file not found: {db_path}"))
                    return
            elif is_postgres:
                # We'll use pg_dump; validation happens at execution time
                pass
            else:
                self.stderr.write(self.style.ERROR(f"Unsupported DB engine: {engine}"))
                return

        if not media_root.exists() and not only_db:
            self.stdout.write(self.style.WARNING(f"Media directory not found: {media_root} (skipping)"))

        manifest = {
            "project": "school_management",
            "created_at": timestamp,
            "django_version": settings.VERSION if hasattr(settings, "VERSION") else None,
            "paths": {
                "db": str(db_path),
                "media": str(media_root),
            },
        }

        with ZipFile(backup_path, mode="w", compression=ZIP_DEFLATED) as zf:
            # Add manifest
            manifest["db_engine"] = engine
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))

            # Add DB
            if not only_media:
                if is_sqlite and db_path.exists():
                    zf.write(db_path, arcname="db.sqlite3")
                    self.stdout.write(self.style.SUCCESS("✓ Added SQLite database: db.sqlite3"))
                elif is_postgres:
                    # Run pg_dump to capture the DB into a SQL file
                    host = default_db.get("HOST") or "localhost"
                    port = str(default_db.get("PORT") or "5432")
                    user = default_db.get("USER") or "postgres"
                    name = default_db.get("NAME")
                    password = default_db.get("PASSWORD") or ""

                    if not name:
                        self.stderr.write(self.style.ERROR("PostgreSQL database NAME is not configured."))
                        return

                    dump_sql_name = f"db_postgres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                    with tempfile.TemporaryDirectory() as tdir:
                        tdirp = Path(tdir)
                        dump_path = tdirp / dump_sql_name

                        env = os.environ.copy()
                        if password:
                            env["PGPASSWORD"] = password

                        pg_dump_bin = options.get("pg_dump_path") or settings.PG_DUMP_PATH
                        cmd = [
                            pg_dump_bin,
                            "-h", str(host),
                            "-p", str(port),
                            "-U", str(user),
                            "-F", "p",  # plain SQL
                            "-d", str(name),
                        ]
                        try:
                            with dump_path.open("wb") as out:
                                proc = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.PIPE, check=True)
                        except FileNotFoundError:
                            self.stderr.write(self.style.ERROR("pg_dump not found. Install PostgreSQL client tools or pass --pg-dump to this command."))
                            return
                        except subprocess.CalledProcessError as e:
                            self.stderr.write(self.style.ERROR("pg_dump failed"))
                            self.stderr.write(e.stderr.decode(errors="ignore"))
                            return

                        # Add dump to ZIP
                        zf.write(dump_path, arcname=dump_sql_name)
                        self.stdout.write(self.style.SUCCESS(f"✓ Added PostgreSQL dump: {dump_sql_name}"))

            # Add media directory
            if not only_db and media_root.exists():
                base_len = len(str(media_root.parent)) + 1
                for root, dirs, files in os.walk(media_root):
                    for f in files:
                        abs_fp = Path(root) / f
                        rel = str(abs_fp)[base_len:]
                        zf.write(abs_fp, arcname=rel.replace("\\", "/"))
                self.stdout.write(self.style.SUCCESS("✓ Added media directory"))

        size_mb = backup_path.stat().st_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(f"Backup created: {backup_path} ({size_mb:.2f} MB)"))
        self.stdout.write(self.style.NOTICE("If OneDrive is running, the file will sync automatically."))
