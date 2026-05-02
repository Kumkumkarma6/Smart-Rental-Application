# Refactored Models - Data Dictionary

## UserProfile Model
**Table Name:** `userprofile`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| user | OneToOneField(User) | ✗ | ✓ | - | - | Link to Django User |
| role | CharField(20) | ✗ | ✗ | 'tenant' | tenant/landlord | User role |
| phone | CharField(15) | ✓ | ✗ | NULL | 10 digits | Phone number |
| address | TextField(300) | ✓ | ✗ | NULL | - | User address |
| gender | CharField(1) | ✓ | ✗ | NULL | M/F/O | Gender |
| profile_picture | ImageField | ✓ | ✗ | NULL | - | Profile image |
| birth_date | DateField | ✓ | ✗ | NULL | - | Date of birth |
| bio | TextField(500) | ✓ | ✗ | '' | - | Short bio |
| created_at | DateTimeField | ✗ | ✗ | auto | - | Created timestamp |
| updated_at | DateTimeField | ✗ | ✗ | auto | - | Updated timestamp |

**Key:** `user_id (FK to auth_user)`  
**Indexes:** user_id, role

---

## Property Model
**Table Name:** `property`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| landlord | ForeignKey(User) | ✗ | ✗ | - | - | Property owner |
| title | CharField(200) | ✗ | ✗ | - | - | Property title |
| description | TextField(2000) | ✗ | ✗ | - | - | Detailed description |
| rent | PositiveIntegerField | ✗ | ✗ | - | > 0 | Monthly rent |
| address | TextField(500) | ✗ | ✗ | - | - | Complete address |
| state | ForeignKey(State) | ✓ | ✗ | NULL | - | State reference |
| district | ForeignKey(District) | ✓ | ✗ | NULL | - | District reference |
| area | ForeignKey(Area) | ✓ | ✗ | NULL | - | Area reference |
| latitude | FloatField | ✓ | ✗ | NULL | -90 to 90 | Latitude coordinate |
| longitude | FloatField | ✓ | ✗ | NULL | -180 to 180 | Longitude coordinate |
| featured_image | ImageField | ✗ | ✗ | - | - | Main property image |
| status | CharField(20) | ✗ | ✗ | 'pending' | pending/approved/rejected | Approval status |
| created_at | DateTimeField | ✗ | ✗ | auto | - | Created timestamp |
| updated_at | DateTimeField | ✗ | ✗ | auto | - | Updated timestamp |

**Keys:** `landlord_id (FK to auth_user)`, `state_id (FK)`, `district_id (FK)`, `area_id (FK)`  
**Indexes:** landlord_id, status, district_id, created_at (DESC)

---

## PropertyImage Model
**Table Name:** `propertyimage`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| property | ForeignKey(Property) | ✗ | ✗ | - | - | Property reference |
| title | CharField(100) | ✓ | ✗ | '' | - | Image title/label |
| image | ImageField | ✗ | ✗ | - | - | Image file |
| uploaded_at | DateTimeField | ✗ | ✗ | auto | - | Upload timestamp |

**Key:** `property_id (FK)`  
**Indexes:** property_id

---

## State Model
**Table Name:** `state`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| name | CharField(100) | ✗ | ✓ | - | - | State name |
| created_at | DateTimeField | ✗ | ✗ | auto | - | Created timestamp |

**Indexes:** name (UNIQUE, indexed)

---

## District Model
**Table Name:** `district`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| state | ForeignKey(State) | ✗ | ✗ | - | - | State reference |
| name | CharField(100) | ✗ | ✗ | - | - | District name |
| created_at | DateTimeField | ✗ | ✗ | auto | - | Created timestamp |

**Key:** `state_id (FK)`  
**Unique:** `(state_id, name)` — no duplicate districts per state  
**Indexes:** state_id

---

## Area Model
**Table Name:** `area`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| district | ForeignKey(District) | ✗ | ✗ | - | - | District reference |
| name | CharField(100) | ✗ | ✗ | - | - | Area name |
| created_at | DateTimeField | ✗ | ✗ | auto | - | Created timestamp |

**Key:** `district_id (FK)`  
**Unique:** `(district_id, name)` — no duplicate areas per district  
**Indexes:** district_id

---

## UserSearchHistory Model
**Table Name:** `usersearchhistory`

| Field | Type | Null | Unique | Default | Validation | Description |
|-------|------|------|--------|---------|-----------|-------------|
| id | AutoField | ✗ | ✓ | - | - | Primary Key |
| user | ForeignKey(User) | ✓ | ✗ | NULL | - | User who searched |
| search_query | CharField(300) | ✓ | ✗ | '' | - | Search text |
| state | ForeignKey(State) | ✓ | ✗ | NULL | - | State filter |
| district | ForeignKey(District) | ✓ | ✗ | NULL | - | District filter |
| area | ForeignKey(Area) | ✓ | ✗ | NULL | - | Area filter |
| min_rent | PositiveIntegerField | ✓ | ✗ | NULL | - | Min rent filter |
| max_rent | PositiveIntegerField | ✓ | ✗ | NULL | - | Max rent filter |
| viewed_property | ForeignKey(Property) | ✓ | ✗ | NULL | - | Property viewed |
| timestamp | DateTimeField | ✗ | ✗ | auto | - | Search timestamp |

**Keys:** `user_id (FK)`, `state_id (FK)`, `district_id (FK)`, `area_id (FK)`, `viewed_property_id (FK)`  
**Indexes:** (user_id, timestamp DESC), district_id, timestamp

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐
│   auth_user     │
│  (Django)       │
└────────┬────────┘
         │
         │ 1:1
         │
    ┌────▼────────────────┐
    │  UserProfile        │
    │  - user_id (PK,FK)  │
    │  - role             │
    │  - phone            │
    │  - address          │
    │  - gender           │
    │  - profile_pic      │
    │  - birth_date       │
    │  - bio              │
    └────────────────────┘

    ┌──────────────┐
    │   State      │
    │  - id (PK)   │
    │  - name      │
    └────┬─────────┘
         │ 1:M
         │
    ┌────▼──────────────┐
    │   District         │
    │  - id (PK)         │
    │  - state_id (FK)   │
    │  - name            │
    └────┬──────────────┘
         │ 1:M
         │
    ┌────▼──────────────┐
    │   Area             │
    │  - id (PK)         │
    │  - district_id(FK) │
    │  - name            │
    └────────────────────┘

    ┌──────────────────────────────┐
    │      Property                │
    │  - id (PK)                   │
    │  - landlord_id (FK→User)     │
    │  - title                     │
    │  - description               │
    │  - rent                      │
    │  - address                   │
    │  - state_id (FK)             │
    │  - district_id (FK)          │
    │  - area_id (FK)              │
    │  - latitude                  │
    │  - longitude                 │
    │  - featured_image            │
    │  - status                    │
    │  - created_at, updated_at    │
    └────┬─────────────────────────┘
         │ 1:M
         │
    ┌────▼────────────────┐
    │ PropertyImage        │
    │ - id (PK)            │
    │ - property_id (FK)   │
    │ - title              │
    │ - image              │
    │ - uploaded_at        │
    └──────────────────────┘

    ┌───────────────────────────────┐
    │  UserSearchHistory            │
    │ - id (PK)                     │
    │ - user_id (FK, nullable)      │
    │ - search_query                │
    │ - state_id (FK, nullable)     │
    │ - district_id (FK, nullable)  │
    │ - area_id (FK, nullable)      │
    │ - min_rent, max_rent          │
    │ - viewed_property_id (FK)     │
    │ - timestamp                   │
    └───────────────────────────────┘
```

---

## Comparison: Old vs New Models

| Aspect | Old | New |
|--------|-----|-----|
| User Profile | Register + UserProfile (2 models) | UserProfile (1 unified model) |
| Property | Owner_Detail | Property |
| Images | Image | PropertyImage |
| Approval Status | Status model (separate table) | Property.status (CharField choice) |
| Field Names | desc, local_add, dist, gen | description, address, district, gender |
| Validation | Minimal | Phone regex, lat/lng ranges, rent > 0 |
| Coordinates | FloatField only | FloatField + range validation |
| Relationships | Indirect (through Status) | Direct (landlord to User) |
| Timestamps | Missing | created_at, updated_at on all key models |
| Indexes | Minimal | Optimized for common queries |
| Documentation | Poor | Full help_text on all fields |

---

## Migration Commands

```bash
# Create migrations
python manage.py makemigrations Room

# Apply migrations
python manage.py migrate Room

# Check migration status
python manage.py showmigrations Room

# Reverse a migration (if needed)
python manage.py migrate Room 0001
```

---

## Testing Coordinates Validation

```python
from Room.models import Property, District, State

# Valid coordinates
property = Property.objects.create(
    landlord=user,
    title="Test Property",
    description="Test",
    rent=10000,
    address="123 Test St",
    district=district_obj,
    latitude=28.6139,
    longitude=77.2090,
    featured_image=image_file,
    status='approved'
)

# Invalid latitude (will raise ValidationError)
# property.latitude = 95  # OUT OF RANGE!

# Invalid longitude (will raise ValidationError)
# property.longitude = 185  # OUT OF RANGE!

# Invalid rent (will raise ValidationError)
# property.rent = 0  # MUST BE > 0!
```
