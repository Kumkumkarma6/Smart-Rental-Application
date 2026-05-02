import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SearchingYourHome.settings')
django.setup()

from Room.models import Property

prop = Property.objects.filter(status='approved').first()
if prop:
    print(f'Property: {prop.title}')
    print(f'Landlord: {prop.landlord.username}')
    print(f'Has profile: {hasattr(prop.landlord, "profile")}')
    if hasattr(prop.landlord, 'profile'):
        print(f'Profile phone: {prop.landlord.profile.phone}')
    print(f'Featured image: {prop.featured_image}')
    print(f'Address: {prop.address}')
    print(f'Area: {prop.area.name if prop.area else "None"}')
else:
    print('No approved properties found')