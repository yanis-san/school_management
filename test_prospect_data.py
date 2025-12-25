from prospects.models import Prospect
from django.db.models import Count
import json

print("=== DONNÉES PROSPECTS ===")
print(f"Total prospects: {Prospect.objects.count()}")

# Top cours
print("\n=== TOP 5 COURS ===")
top_courses = Prospect.objects.exclude(specific_course='').values('specific_course').annotate(count=Count('id')).order_by('-count')[:5]
for item in top_courses:
    print(f"  {item['specific_course']}: {item['count']}")

courses_dict = {item['specific_course']: item['count'] for item in top_courses}
print(f"\nJSON courses: {json.dumps(courses_dict)}")

# Top activités
print("\n=== TOP 5 ACTIVITÉS ===")
top_activities = Prospect.objects.exclude(activity_type='').values('activity_type').annotate(count=Count('id')).order_by('-count')[:5]
for item in top_activities:
    print(f"  {item['activity_type']}: {item['count']}")

activities_dict = {item['activity_type']: item['count'] for item in top_activities}
print(f"\nJSON activities: {json.dumps(activities_dict)}")

# Sources
print("\n=== SOURCES ===")
sources = Prospect.objects.exclude(source='').values('source').annotate(count=Count('id')).order_by('-count')
for item in sources:
    print(f"  {item['source']}: {item['count']}")

sources_dict = {item['source']: item['count'] for item in sources}
print(f"\nJSON sources: {json.dumps(sources_dict)}")
