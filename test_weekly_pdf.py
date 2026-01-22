#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.schedule_generator import generate_weekly_schedule_pdf

try:
    pdf = generate_weekly_schedule_pdf()
    if pdf:
        print('✓ PDF GÉNÉRÉE AVEC SUCCÈS!')
    else:
        print('✗ Aucune séance trouvée')
except Exception as e:
    print(f'✗ ERREUR: {e}')
    import traceback
    traceback.print_exc()
