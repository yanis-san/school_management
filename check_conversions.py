from prospects.models import Prospect
from django.utils import timezone

converted = Prospect.objects.filter(converted=True)
print(f'Total convertis: {converted.count()}')

for p in converted:
    print(f'  - {p.first_name} {p.last_name}:')
    print(f'    created_at: {p.created_at}')
    print(f'    updated_at: {p.updated_at}')
    print(f'    Mois updated: {p.updated_at.strftime("%b %Y")}')
