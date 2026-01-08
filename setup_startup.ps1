# Script PowerShell pour configurer le démarrage automatique
# À exécuter EN TANT QU'ADMINISTRATEUR

$projectPath = "C:\Users\Social Media Manager\Documents\codes\school_management"
$scriptName = "launch_app_background.vbs"
$scriptPath = "$projectPath\$scriptName"

# Créer le fichier VBS pour lancer l'application en arrière-plan
$vbsContent = @"
Set objShell = CreateObject("WScript.Shell")
' Utiliser PUSHd pour supporter les chemins UNC (mappe un lecteur temporaire)
objShell.Run "cmd.exe /c pushd ""$projectPath"" && .venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000", 0, False
"@

# Sauvegarder le fichier VBS
$vbsContent | Out-File -FilePath $scriptPath -Encoding Default -Force
Write-Host "✓ Fichier de lancement créé: $scriptPath"

# Créer un raccourci au démarrage
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = "$startupFolder\Gestionnaire Ecole.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "C:\Windows\System32\wscript.exe"
$shortcut.Arguments = "`"$scriptPath`""
$shortcut.WorkingDirectory = $projectPath
$shortcut.Description = "Démarrage automatique - Gestionnaire d'Ecole"
$shortcut.WindowStyle = 7  # Fenêtre minimisée
$shortcut.Save()

Write-Host "✓ Raccourci de démarrage créé: $shortcutPath"
Write-Host ""
Write-Host "Configuration terminee! L'application demarre au prochain redemarrage Windows."
Write-Host "Pour tester maintenant: Double-cliquez sur le raccourci dans le dossier Startup"
