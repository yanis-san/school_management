f = 'documents/views.py'
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

# Le problème est \'\'\' au lieu de \'\'
# On remplace filename*=UTF-8\'\'\'{encoded par filename*=UTF-8''{encoded
old = "filename*=UTF-8\\'\\'\\'{"
new = "filename*=UTF-8''{"
content = content.replace(old, new)

with open(f, 'w', encoding='utf-8') as file:
    file.write(content)

print("Correction appliquée!")
