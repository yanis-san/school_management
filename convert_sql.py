import re

# Lire le fichier
with open('db_postgres_20260115_155345.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer les COPY par INSERT
def convert_copy_to_insert(content):
    # Pattern pour trouver les blocs COPY
    copy_pattern = r'COPY public\.(\w+) \((.*?)\) FROM stdin;(.*?)\\\.'
    
    def replace_copy(match):
        table_name = match.group(1)
        columns = match.group(2)
        data = match.group(3)
        
        # Traiter chaque ligne de données
        lines = data.strip().split('\n')
        inserts = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Diviser les valeurs (séparées par des tabs)
            values = line.split('\t')
            
            # Convertir les valeurs
            converted_values = []
            for val in values:
                if val == '\\N':
                    converted_values.append('NULL')
                elif val == 't':
                    converted_values.append('true')
                elif val == 'f':
                    converted_values.append('false')
                else:
                    # Échapper les guillemets
                    val = val.replace("'", "''")
                    converted_values.append(f"'{val}'")
            
            insert_sql = f"INSERT INTO public.{table_name} ({columns}) VALUES ({', '.join(converted_values)});"
            inserts.append(insert_sql)
        
        return '\n'.join(inserts)
    
    # Appliquer la conversion
    result = re.sub(copy_pattern, replace_copy, content, flags=re.DOTALL | re.MULTILINE)
    return result

# Convertir
new_content = convert_copy_to_insert(content)

# Sauvegarder
with open('db_postgres_20260115_155345_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ Conversion terminée : db_postgres_20260115_155345_fixed.sql')
