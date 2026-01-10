f = 'documents/views.py'
with open(f, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Remplacer complètement la ligne 494 (index 493)
if len(lines) > 493:
    # Nouvelle ligne correcte
    lines[493] = "    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"; filename*=UTF-8\\'\\'\\'{encoded_filename}'\n"
    print("Ligne 494 remplacée")

with open(f, 'w', encoding='utf-8') as file:
    file.writelines(lines)

print("Terminé!")
