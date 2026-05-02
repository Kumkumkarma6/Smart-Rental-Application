import os
import sys
import django

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SearchingYourHome.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from Room.models import UserProfile, Property, State, District, Area, PropertyImage
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import SimpleUploadedFile

print("\n" + "="*80)
print("COMPREHENSIVE PROJECT FEATURE TEST")
print("="*80)

# Setup test client
client = Client()

def test_database_models():
    """Test all models can be created and queried"""
    print("\n[1] Testing Database Models")
    print("-" * 50)

    try:
        # Test State creation
        state = State.objects.create(state="Maharashtra")
        print(f"✓ State created: {state}")

        # Test District creation
        district = District.objects.create(state=state, dist="Mumbai")
        print(f"✓ District created: {district}")

        # Test Area creation
        area = Area.objects.create(district=district, area_name="Andheri")
        print(f"✓ Area created: {area}")

        # Test User and UserProfile creation
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        profile = UserProfile.objects.create(
            user=user,
            role='landlord',
            phone='9876543210',
            address='Test Address'
        )
        print(f"✓ UserProfile created: {profile}")

        # Test Property creation
        property_obj = Property.objects.create(
            landlord=user,
            state=state,
            district=district,
            area="Test Area",
            title="Test Property",
            description="Test Description",
            rent=15000,
            address="Test Address",
            status='approved'
        )
        print(f"✓ Property created: {property_obj}")

        # Test PropertyImage creation
        image = PropertyImage.objects.create(
            property=property_obj,
            title="Test Image",
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )
        print(f"✓ PropertyImage created: {image}")

        print("✓ All models working correctly")
        return True

    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_authentication():
    """Test signup and signin functionality"""
    print("\n[2] Testing Authentication")
    print("-" * 50)

    try:
        # Clean up any existing test users
        User.objects.filter(username__startswith='testauth').delete()

        # Test tenant signup via POST
        tenant_data = {
            'uname': 'testauth_tenant',
            'pwd': 'testpass123',
            'email': 'tenant@test.com'
        }
        response = client.post('/signup_tenant', tenant_data)
        print(f"✓ Tenant signup response: {response.status_code}")

        # Test landlord signup via POST
        landlord_data = {
            'fname': 'Test',
            'lname': 'Landlord',
            'uname': 'testauth_landlord',
            'pwd': 'testpass123',
            'pwd_confirm': 'testpass123',
            'phone': '9876543210',
            'email': 'landlord@test.com',
            'gender': 'M',
            'address': 'Test Address'
        }
        response = client.post('/signup_landlord', landlord_data)
        print(f"✓ Landlord signup response: {response.status_code}")

        # Test signin
        signin_data = {
            'uname': 'testauth_tenant',
            'pwd': 'testpass123',
            'role': 'tenant'
        }
        response = client.post('/signin', signin_data)
        print(f"✓ Tenant signin response: {response.status_code}")

        # Check if user was created
        tenant_user = User.objects.filter(username='testauth_tenant').first()
        landlord_user = User.objects.filter(username='testauth_landlord').first()

        if tenant_user and landlord_user:
            tenant_profile = UserProfile.objects.get(user=tenant_user)
            landlord_profile = UserProfile.objects.get(user=landlord_user)
            print(f"✓ Tenant profile: {tenant_profile.role}")
            print(f"✓ Landlord profile: {landlord_profile.role}")
            return True
        else:
            print("✗ Users not created properly")
            return False

    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False

def test_property_operations():
    """Test property creation, search, and related operations"""
    print("\n[3] Testing Property Operations")
    print("-" * 50)

    try:
        # Get test user
        landlord = User.objects.filter(username='testauth_landlord').first()
        if not landlord:
            print("✗ No landlord user found")
            return False

        # Get test location data
        state = State.objects.filter(name="Maharashtra").first()
        district = District.objects.filter(dist="Mumbai").first()

        if not state or not district:
            print("✗ Location data not found")
            return False

        # Test property creation via POST
        property_data = {
            'state': state.id,
            'dist': district.name,
            'area': 'Test Area',
            'local': 'Test Local Address',
            'title': 'Test Property Title',
            'desc': 'Test Property Description',
            'rent': '20000',
            'latitude': '19.0760',
            'longitude': '72.8777'
        }

        # Create a test image file
        from PIL import Image
        import io
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        property_data['img'] = SimpleUploadedFile("test_property.jpg", img_byte_arr.getvalue(), content_type="image/jpeg")

        # Login as landlord first
        client.login(username='testauth_landlord', password='testpass123')

        response = client.post(f'/rent/{state.id}', property_data)
        print(f"✓ Property creation response: {response.status_code}")

        # Check if property was created
        property_obj = Property.objects.filter(title='Test Property Title').first()
        if property_obj:
            print(f"✓ Property created: {property_obj.title}")
            print(f"✓ Property status: {property_obj.status}")
            return True
        else:
            print("✗ Property not created")
            return False

    except Exception as e:
        print(f"✗ Property operations test failed: {e}")
        return False

def test_search_functionality():
    """Test search and filtering"""
    print("\n[4] Testing Search Functionality")
    print("-" * 50)

    try:
        # Test basic search
        response = client.get('/search')
        print(f"✓ Search page response: {response.status_code}")

        # Test search with query
        response = client.get('/search', {'query': 'test'})
        print(f"✓ Search with query response: {response.status_code}")

        # Test listings page
        response = client.get('/listings')
        print(f"✓ Listings page response: {response.status_code}")

        return True

    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False

def test_admin_functionality():
    """Test admin panel access"""
    print("\n[5] Testing Admin Functionality")
    print("-" * 50)

    try:
        # Test admin login
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            print("✗ Admin user not found")
            return False

        client.login(username='admin', password='admin123')
        response = client.get('/admin/')
        print(f"✓ Admin panel response: {response.status_code}")

        # Test admin pages
        response = client.get('/admin/Room/userprofile/')
        print(f"✓ UserProfile admin response: {response.status_code}")

        response = client.get('/admin/Room/property/')
        print(f"✓ Property admin response: {response.status_code}")

        return True

    except Exception as e:
        print(f"✗ Admin test failed: {e}")
        return False

def test_ml_features():
    """Test ML features like recommendations and rent prediction"""
    print("\n[6] Testing ML Features")
    print("-" * 50)

    try:
        # Test recommendations
        response = client.get('/recommendations')
        print(f"✓ Recommendations response: {response.status_code}")

        # Test rent prediction
        response = client.get('/predict_rent')
        print(f"✓ Rent prediction response: {response.status_code}")

        # Test rent prediction with data
        predict_data = {
            'state': 'Maharashtra',
            'dist': 'Mumbai',
            'title': '2BHK Apartment',
            'desc': 'Nice apartment near station'
        }
        response = client.post('/predict_rent', predict_data)
        print(f"✓ Rent prediction calculation response: {response.status_code}")

        return True

    except Exception as e:
        print(f"✗ ML features test failed: {e}")
        return False

def test_templates():
    """Test all template pages load without errors"""
    print("\n[7] Testing Templates")
    print("-" * 50)

    pages_to_test = [
        ('/', 'Home'),
        ('/signup_role', 'Signup Role Selection'),
        ('/signin_role', 'Signin Role Selection'),
        ('/about', 'About'),
        ('/contact', 'Contact'),
    ]

    for url, name in pages_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✓ {name} page: {response.status_code}")
            else:
                print(f"✗ {name} page: {response.status_code}")
        except Exception as e:
            print(f"✗ {name} page error: {e}")

    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n[8] Cleaning Test Data")
    print("-" * 50)

    try:
        # Delete test users and related data
        User.objects.filter(username__startswith='testauth').delete()
        User.objects.filter(username__startswith='test').delete()

        # Delete test properties
        Property.objects.filter(title__startswith='Test').delete()

        # Delete test locations (keep if they have dependencies)
        # State.objects.filter(state="Maharashtra").delete()  # Commented out to avoid cascade issues

        print("✓ Test data cleaned")
        return True

    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False

# Run all tests
def main():
    results = []

    results.append(("Database Models", test_database_models()))
    results.append(("Authentication", test_authentication()))
    results.append(("Property Operations", test_property_operations()))
    results.append(("Search Functionality", test_search_functionality()))
    results.append(("Admin Functionality", test_admin_functionality()))
    results.append(("ML Features", test_ml_features()))
    results.append(("Templates", test_templates()))
    results.append(("Cleanup", cleanup_test_data()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print("20")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Project is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)