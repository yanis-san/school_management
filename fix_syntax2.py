f = 'documents/views.py'
with open(f, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Corriger la ligne 494 (index 493)
if len(lines) > 493:
    line = lines[493]
    # Remplacer UTF-8\'\'\' par UTF-8\'\'
    if "UTF-8\\'\\'\\'" in line:
        lines[493] = line.replace("UTF-8\\'\\'\\'", "UTF-8\\'\\'")
        print(f"Ligne 494 corrigée")
    else:
        print(f"Pattern non trouvé dans la ligne 494: {repr(line)}")

with open(f, 'w', encoding='utf-8') as file:
    file.writelines(lines)

print("Fichier mis à jour")
