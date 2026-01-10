f = 'documents/views.py'
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

# Remplacer les 3 guillemets simples par 2
content = content.replace("UTF-8'''", "UTF-8''")

with open(f, 'w', encoding='utf-8') as file:
    file.write(content)

print("Correction appliquée avec succès")
