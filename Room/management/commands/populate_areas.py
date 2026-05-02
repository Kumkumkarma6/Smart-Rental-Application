from django.core.management.base import BaseCommand
from Room.models import District, Area

class Command(BaseCommand):
    help = 'Populate areas for Indian districts'

    def handle(self, *args, **options):
        # Dictionary of districts and their common areas
        areas_data = {
            'Mumbai City': ['Bandra', 'Kala Ghoda', 'Colaba', 'Fort', 'Marine Drive', 'Malabar Hill', 'Worli', 'Mahim', 'Girgaon', 'Parel'],
            'Mumbai Suburban': ['Andheri', 'Goregaon', 'Borivali', 'Powai', 'Vile Parle', 'Malad', 'Thane', 'Panvel', 'Dombivli', 'Navi Mumbai'],
            'Pune': ['Hinjewadi', 'Baner', 'Aundh', 'Koregaon Park', 'Camp', 'Shivajinagar', 'Hadapsar', 'Viman Nagar', 'Kalyani Nagar', 'Wakad'],
            'Bangalore Urban': ['Indiranagar', 'Whitefield', 'Koramangala', 'Bellandur', 'Sarjapur', 'Madiwala', 'BTM Layout', 'JP Nagar', 'Yelahanka', 'Marathahalli'],
            'Hyderabad': ['Banjara Hills', 'Jubilee Hills', 'Gachibowli', 'Hitech City', 'Kukatpally', 'Kondapur', 'Secunderabad', 'Mynampally', 'Uppal', 'Dilsukhnagar'],
            'Delhi': ['Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'South Delhi', 'West Delhi', 'Greater Kailash', 'Shalimar Bagh', 'Dwarka', 'Noida'],
            'Chennai': ['Anna Nagar', 'Kodambakkam', 'Mylapore', 'Besant Nagar', 'Nungambakkam', 'Thiruvanmiyur', 'Virugambakkam', 'Ashok Nagar', 'Villivakkam', 'Teynampet'],
            'Kolkata': ['Ballygunge', 'Alipore', 'Behala', 'Bangur Avenue', 'Gariahat', 'Park Circus', 'Baghajatin', 'Thakurpukur', 'Rabindra Sarovar', 'Tollygunj'],
            'Ahmedabad': ['Navrangpura', 'Paldi', 'Satellite', 'Bodakdev', 'Thaltej', 'New York Tower', 'Ambli', 'Gota', 'Rajendra Nagar', 'Urvashi'],
            'Jaipur': ['C-Scheme', 'MI Road', 'Malviya Nagar', 'Tonk Road', 'Raja Park', 'Bani Park', 'Nirmala Nagar', 'Krishna Nagar', 'Agarwal Farm', 'Indira Nagar'],
        }

        count = 0
        for district_name, areas in areas_data.items():
            try:
                district = District.objects.get(name=district_name)
                for area_name in areas:
                    area, created = Area.objects.get_or_create(
                        district=district,
                        name=area_name
                    )
                    if created:
                        count += 1
            except District.DoesNotExist:
                self.stdout.write(f"District '{district_name}' not found in database")

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} areas'))
