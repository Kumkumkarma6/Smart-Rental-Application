# Model Refactoring - Migration Steps

## CRITICAL: Fresh Migration Required

Since you've made major model structure changes, follow these steps in order:

### Step 1: Delete Old Migrations (Keep Clean Start)
```bash
# Delete all migration files except __init__.py
rm Room/migrations/0002_*.py
rm Room/migrations/0003_*.py
rm Room/migrations/0004_*.py
rm Room/migrations/0005_*.py
rm Room/migrations/0006_*.py
rm Room/migrations/0007_*.py
rm Room/migrations/0008_*.py
rm Room/migrations/0009_*.py
rm Room/migrations/0010_*.py

# Or on Windows PowerShell:
# Remove-Item Room/migrations/0002_*.py -Force
# Remove-Item Room/migrations/0003_*.py -Force
# etc.
```

### Step 2: Delete Old Database
```bash
# Delete SQLite database to start fresh
rm db.sqlite3

# Or on Windows:
# Remove-Item db.sqlite3 -Force
```

### Step 3: Create Fresh Migrations
```bash
python manage.py makemigrations Room
python manage.py migrate
```

### Step 4: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 5: Run Server
```bash
python manage.py runserver
```

---

## File Changes Made

### ✅ admin.py
- Replaced old model registrations with new ones
- Added inline PropertyImage in PropertyAdmin
- Added proper fieldsets and list_display
- Added query optimization with select_related()

### ⏳ views.py 
- NEEDS UPDATING: Replace all Register, Owner_Detail, Status, Image references
- NEEDS FIELD UPDATES: dist → district, desc → description, local_add → address, etc.

### ⏳ ml.py
- NEEDS UPDATING: Replace Owner_Detail with Property, Status with status field

### ⏳ forms.py
- May need updating depending on what's inside

---

## Complete List of Replacements in views.py

| Old | New |
|-----|-----|
| Register.objects | UserProfile.objects |
| Owner_Detail.objects | Property.objects |
| Image.objects | PropertyImage.objects |
| Status.objects | Not needed (use string choices) |
| register.user | user (direct access) |
| data.register → data.landlord | data.landlord |
| property.desc | property.description |
| property.local_add | property.address |
| property.dist | property.district |
| property.img | property.featured_image |
| status__status='' | status='' |
| register=re | landlord=user |
| room_name | title |

---

## Field Name Changes Summary

```python
# UserProfile (merged Register + UserProfile)
gen → gender
add → address
mobile → phone
image → profile_picture
birth → birth_date

# Property (replaces Owner_Detail)
register → landlord (direct User FK)
desc → description
local_add → address
dist → district
img → featured_image

# PropertyImage (replaces Image)
owner → property
room_name → title
img → image

# Relationships
status__status → status (string choice, no FK needed)
```

---

## Status Field Changes

**OLD:**
```python
status, _ = Status.objects.get_or_create(status="pending")
owner.status = status
```

**NEW:**
```python
# No need to create Status object - just use string
property.status = 'pending'  # pending, approved, or rejected
```

---

## Search History Changes

**OLD:**
```python
viewed_room = models.ForeignKey('Owner_Detail', ...)
```

**NEW:**
```python
viewed_property = models.ForeignKey(Property, ...)
```

