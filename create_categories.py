"""
Script pour créer des catégories d'exemple pour le système de tâches
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tasks.models import Category

# Catégories d'exemple avec leurs couleurs
categories_data = [
    {
        'name': 'Urgent',
        'color': '#EF4444',  # Rouge
        'description': 'Tâches urgentes nécessitant une attention immédiate'
    },
    {
        'name': 'Suivi Étudiant',
        'color': '#3B82F6',  # Bleu
        'description': 'Tâches liées au suivi des étudiants'
    },
    {
        'name': 'Prospect',
        'color': '#10B981',  # Vert
        'description': 'Tâches de suivi des prospects et inscriptions'
    },
    {
        'name': 'Finance',
        'color': '#F59E0B',  # Orange
        'description': 'Tâches liées aux paiements et finances'
    },
    {
        'name': 'Administratif',
        'color': '#6366F1',  # Indigo
        'description': 'Tâches administratives générales'
    },
    {
        'name': 'Inventaire',
        'color': '#8B5CF6',  # Violet
        'description': 'Tâches liées à la gestion de l\'inventaire'
    },
    {
        'name': 'Communication',
        'color': '#EC4899',  # Rose
        'description': 'Tâches de communication interne et externe'
    },
    {
        'name': 'Réunion',
        'color': '#14B8A6',  # Teal
        'description': 'Préparation et suivi de réunions'
    },
]

print("🎨 Création des catégories...\n")

created_count = 0
updated_count = 0

for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'color': cat_data['color'],
            'description': cat_data['description']
        }
    )
    
    if created:
        created_count += 1
        print(f"✅ Créé: {category.name} (couleur: {category.color})")
    else:
        # Mettre à jour si elle existe déjà
        category.color = cat_data['color']
        category.description = cat_data['description']
        category.save()
        updated_count += 1
        print(f"🔄 Mis à jour: {category.name} (couleur: {category.color})")

print(f"\n📊 Résumé:")
print(f"   - {created_count} catégorie(s) créée(s)")
print(f"   - {updated_count} catégorie(s) mise(s) à jour")
print(f"   - Total: {Category.objects.count()} catégorie(s) dans la base")
print("\n✨ Catégories prêtes à utiliser!")
