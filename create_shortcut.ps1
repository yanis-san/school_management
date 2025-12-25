# Script pour créer un raccourci sur le bureau
# Exécutez ce script une fois pour créer le raccourci

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = "$DesktopPath\Gestionnaire d'Ecole.lnk"

# Chemin du projet
$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFile = "$ProjectPath\run_app.bat"

# Créer l'objet raccourci
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Configurer le raccourci
$Shortcut.TargetPath = $BatchFile
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.WindowStyle = 1  # Fenêtre normale
$Shortcut.Description = "Lance l'application Gestionnaire d'Ecole"

# Optionnel: Ajouter une icône (vous pouvez utiliser une icône personnalisée)
# $Shortcut.IconLocation = "$ProjectPath\icon.ico"

# Sauvegarder le raccourci
$Shortcut.Save()

Write-Host "✅ Raccourci créé avec succès sur le bureau!" -ForegroundColor Green
Write-Host "Chemin: $ShortcutPath" -ForegroundColor Cyan
