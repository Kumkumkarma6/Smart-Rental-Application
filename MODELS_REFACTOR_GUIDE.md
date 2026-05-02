# Models Refactoring Guide

## Overview
The `Room/models.py` has been professionally refactored with improved structure, naming conventions, validation, and database optimization.

---

## Major Changes

### 1. **UserProfile Model (Merged Register + UserProfile)**
**Old:** Separate `Register` and `UserProfile` models
**New:** Single unified `UserProfile` model with all user information

**Fields:**
```python
- user (OneToOneField to User)
- role (tenant/landlord choice)
- phone (10-digit validation)
- address (TextField)
- gender (M/F/Other)
- profile_picture (ImageField)
- birth_date (DateField)
- bio (TextField)
- created_at, updated_at (timestamps)
```

**Benefits:**
- Single source of truth for user data
- Cleaner relationships
- Built-in validation for phone

---

### 2. **Property Model (Replaces Owner_Detail)**
**Old:** `Owner_Detail` with inconsistent field names
**New:** `Property` with professional naming and validation

**Key Changes:**
- `Owner_Detail` → `Property`
- `register` → `landlord` (direct User FK)
- `desc` → `description` (TextField)
- `local_add` → `address` (TextField)
- `dist` → `district` (clearer naming)
- `img` → `featured_image` (ImageField)
- `status` (removed FK to Status model, now choices)
- Added: `latitude`/`longitude` validation (-90 to 90, -180 to 180)
- Added: `rent` validation (must be > 0)
- Added: `created_at`, `updated_at` timestamps
- Added: Helper methods (`is_approved()`, `is_pending()`, `is_rejected()`)

**Status Choices:**
```python
- pending: Pending Approval
- approved: Approved
- rejected: Rejected
```

**Benefits:**
- No separate Status table needed
- Direct landlord reference (faster queries)
- Built-in coordinate validation
- Better timestamps for sorting/filtering

---

### 3. **Area Model (Improved)**
**Old:** Area had both State and District ForeignKeys (redundant)
**New:** Area only references District (removes redundancy)

**Changes:**
- Removed: `state` ForeignKey
- Kept: `district` ForeignKey
- Renamed: `area_name` → `name`
- Added: `unique_together` constraint on (district, name)

**Benefits:**
- No data redundancy
- Faster queries
- Cleaner relationships

---

### 4. **District Model (Minor Improvements)**
**Changes:**
- Renamed: `dist` → `name`
- Added: `unique_together` constraint on (state, name)
- Added: Database index on state
- Improved `__str__` method

---

### 5. **State Model (Minor Improvements)**
**Changes:**
- Renamed: `state` → `name`
- Added: `unique=True` constraint
- Added: `created_at` timestamp

---

### 6. **PropertyImage Model (Replaces Image)**
**Old:** Generic `Image` model with poor naming
**New:** `PropertyImage` with clarity and better structure

**Changes:**
- `Image` → `PropertyImage`
- `owner` → `property` (clearer FK reference)
- `img` → `image` (standard field name)
- `room_name` → `title` (more flexible naming)
- Added: `uploaded_at` timestamp
- Improved: `__str__` method

---

### 7. **Removed Models**
- **Status model:** Replaced with CharField choices in Property model

---

### 8. **UserSearchHistory Model (Enhanced)**
**Changes:**
- Added: `area` ForeignKey field
- Renamed: `viewed_room` → `viewed_property`
- Added: Database indexes for faster queries
- Improved: `__str__` method
- Added: `related_name` for reverse relationships

---

## Database Migrations Required

After updating `models.py`, run:

```bash
python manage.py makemigrations Room
python manage.py migrate
```

---

## Code Updates Required in Views

### If you used old model names, update them:

**Old → New Mapping:**

```python
# User Profile
Register → UserProfile
instance.user → instance.user (same)
instance.gen → instance.gender
instance.add → instance.address
instance.mobile → instance.phone
instance.image → instance.profile_picture

# Properties
Owner_Detail → Property
property.register → property.landlord
property.desc → property.description
property.local_add → property.address
property.dist → property.district
property.img → property.featured_image
property.status (FK to Status) → property.status (string choice)

# Images
Image → PropertyImage
image.owner → image.property
image.room_name → image.title
image.img → image.image

# Search History
viewed_room → viewed_property
```

### Example View Updates:

**Before:**
```python
from Room.models import Owner_Detail, Register, Image, Status

listings = Owner_Detail.objects.filter(status__status='accepted')
register = Register.objects.get(user=user)
owner_detail = Owner_Detail.objects.create(
    register=register,
    desc='...',
    local_add='...'
)
```

**After:**
```python
from Room.models import Property, UserProfile, PropertyImage

listings = Property.objects.filter(status='approved')
profile = UserProfile.objects.get(user=user)
property_obj = Property.objects.create(
    landlord=user,
    description='...',
    address='...'
)
```

---

## Validation Features Added

- **Phone:** 10-digit regex validation
- **Latitude:** `-90` to `90` range validation
- **Longitude:** `-180` to `180` range validation
- **Rent:** Must be greater than 0
- **Area uniqueness:** Cannot have duplicate area names in same district
- **District uniqueness:** Cannot have duplicate district names in same state

---

## Database Indexes Added

For better query performance:

```python
Property:
- landlord (ForeignKey)
- status (filter by approval status)
- district (location-based queries)
- created_at (recent listings)

UserSearchHistory:
- user + timestamp (user's recent searches)
- district (analytics)

District:
- state

Area:
- district
```

---

## Helper Methods Added

- `UserProfile.is_landlord()` — Check if user is landlord
- `UserProfile.is_tenant()` — Check if user is tenant
- `Property.is_approved()` — Check approval status
- `Property.is_pending()` — Check pending status
- `Property.is_rejected()` — Check rejection status

---

## Migration Checklist

- [ ] Update `Room/views.py` with new model names
- [ ] Update `Room/forms.py` (if exists) with new field names
- [ ] Update all template references (old model names)
- [ ] Run `makemigrations` and `migrate`
- [ ] Test all functionality
- [ ] Update admin.py for new models
- [ ] Check API/serializers if used

---

## Important Notes

1. **Signal Handlers:** Auto-creation of UserProfile still works with signals
2. **Backward Compatibility:** This is a breaking change; all old code referencing old models will need updates
3. **Migration Data:** You may need data migration scripts if you have existing data
4. **Related Names:** Use `property.images.all()` instead of separate Image queries

---

## Benefits of Refactoring

✅ **Cleaner Code:** Consistent naming convention  
✅ **Better Performance:** Database indexes and optimized relationships  
✅ **Built-in Validation:** Prevents invalid data at model level  
✅ **Less Redundancy:** Removed unnecessary fields and models  
✅ **Production-Ready:** Timestamps, metadata, helper methods  
✅ **Easier Maintenance:** Clear field definitions with help_text  
✅ **Better Queries:** Optimized ForeignKey relationships  
✅ **Scalability:** Proper Meta classes for performance  
