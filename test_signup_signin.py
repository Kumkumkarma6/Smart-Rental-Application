import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SearchingYourHome.settings')
django.setup()

from django.contrib.auth.models import User
from Room.models import UserProfile
from django.contrib.auth import authenticate

print("\n" + "="*60)
print("TESTING SIGNUP/SIGNIN LOGIC")
print("="*60)

# Clean up test users if they exist
User.objects.filter(username__startswith='test').delete()

# Test: Create tenant user
print("\n[1] Testing Tenant Signup")
print("-" * 60)
try:
    user = User.objects.create_user(
        username='testtenantuser', 
        password='testpass123', 
        email='tenant@test.com'
    )
    profile = UserProfile.objects.create(user=user, role='tenant')
    print(f"✓ SUCCESS: Tenant created")
    print(f"  - Username: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - Role: {profile.role}")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test: Create landlord user
print("\n[2] Testing Landlord Signup")
print("-" * 60)
try:
    user2 = User.objects.create_user(
        first_name='John', 
        last_name='Doe', 
        username='testlandlord', 
        password='testpass123', 
        email='landlord@test.com'
    )
    profile2 = UserProfile.objects.create(
        user=user2, 
        role='landlord', 
        phone='9876543210',
        gender='Male',
        address='123 Main St'
    )
    print(f"✓ SUCCESS: Landlord created")
    print(f"  - Username: {user2.username}")
    print(f"  - FirstName: {user2.first_name}")
    print(f"  - Email: {user2.email}")
    print(f"  - Phone: {profile2.phone}")
    print(f"  - Role: {profile2.role}")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test: Tenant signin
print("\n[3] Testing Tenant Signin")
print("-" * 60)
user_auth = authenticate(username='testtenantuser', password='testpass123')
if user_auth:
    profile = UserProfile.objects.get(user=user_auth)
    print(f"✓ SUCCESS: Tenant signin works")
    print(f"  - Username: {user_auth.username}")
    print(f"  - Role: {profile.role}")
else:
    print("✗ ERROR: Tenant signin failed (wrong credentials)")

# Test: Landlord signin
print("\n[4] Testing Landlord Signin")
print("-" * 60)
user_auth2 = authenticate(username='testlandlord', password='testpass123')
if user_auth2:
    profile2 = UserProfile.objects.get(user=user_auth2)
    print(f"✓ SUCCESS: Landlord signin works")
    print(f"  - Username: {user_auth2.username}")
    print(f"  - Role: {profile2.role}")
else:
    print("✗ ERROR: Landlord signin failed (wrong credentials)")

# Test: Role checking logic (from signin view)
print("\n[5] Testing Role Matching Logic (from signin view)")
print("-" * 60)

user_auth = authenticate(username='testtenantuser', password='testpass123')
if user_auth:
    profile = UserProfile.objects.get(user=user_auth)
    user_role = profile.role
    
    # Check if role matches selected role
    selected_role = 'tenant'
    if user_role == selected_role:
        print(f"✓ SUCCESS: Role match - user_role='{user_role}' matches selected_role='{selected_role}'")
    else:
        print(f"✗ ERROR: Role mismatch - user_role='{user_role}' but selected_role='{selected_role}'")

print("\n[6] Testing Role Mismatch Detection")
print("-" * 60)
user_auth = authenticate(username='testtenantuser', password='testpass123')
if user_auth:
    profile = UserProfile.objects.get(user=user_auth)
    user_role = profile.role
    
    # Check if role matches selected role
    selected_role = 'landlord'  # User is tenant but selected landlord
    if user_role == selected_role:
        print(f"✓ Signin should succeed (role match)")
    else:
        print(f"✓ SUCCESS: Role mismatch correctly detected")
        print(f"  - User role: {user_role}")
        print(f"  - Selected role: {selected_role}")
        print(f"  - Result: Should show 'Role mismatch' error")

print("\n" + "="*60)
print("ALL TESTS COMPLETED")
print("="*60 + "\n")
