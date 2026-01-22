#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.schedule_generator import generate_schedule_pdf

try:
    pdf_bytes = generate_schedule_pdf()
    print('✅ PDF généré avec succès')
    print(f'✅ Taille du PDF: {len(pdf_bytes)} bytes')
except Exception as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
