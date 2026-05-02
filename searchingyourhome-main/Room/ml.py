import re
from collections import Counter
from django.db.models import Avg, Q
from .models import Owner_Detail, State, District, Status, UserSearchHistory
from django.contrib.auth.models import User
from PIL import Image as PILImage
import io


def estimate_rent(state_name=None, district_name=None, title=None, desc=None, local=None):
    """Estimate rent using simple historical averages by district or state."""
    qs = Owner_Detail.objects.filter(rent__isnull=False, status__status='accepted')

    if district_name:
        qs = qs.filter(dist__dist__iexact=district_name)
    elif state_name:
        qs = qs.filter(state__state__iexact=state_name)

    avg_rent = qs.aggregate(avg=Avg('rent'))['avg']
    if avg_rent:
        return int(avg_rent)

    overall = Owner_Detail.objects.filter(rent__isnull=False, status__status='accepted').aggregate(avg=Avg('rent'))['avg']
    return int(overall or 0)


def rank_rooms(query, rooms):
    """Rank a list of room objects by simple keyword relevance."""
    if not query:
        return rooms

    query = query.lower()
    scored = []
    for room in rooms:
        score = 0
        title = (room.title or '').lower()
        desc = (room.desc or '').lower()
        local = (room.local_add or '').lower()
        area = (room.area or '').lower()
        state = (room.state.state or '').lower() if room.state else ''
        dist = (room.dist.dist or '').lower() if room.dist else ''

        if query in title:
            score += 50
        if query in desc:
            score += 30
        if query in area:
            score += 35  # Area search is important
        if query in local:
            score += 20
        if query in state or query in dist:
            score += 40
        if 'cheap' in query or 'low' in query:
            score += max(0, 20 - (room.rent or 0) // 1000)
        scored.append((score, room))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [room for score, room in scored]


def parse_search_text(text):
    """Parse natural language search input for state, district, and rent range."""
    result = {'state': None, 'dist': None, 'min_rent': None, 'max_rent': None, 'query': text}
    if not text:
        return result

    text_lower = text.lower()
    rent_match = re.search(r'([0-9]+)\s*(?:-|to|se|tak)\s*([0-9]+)', text_lower)
    if rent_match:
        result['min_rent'] = int(rent_match.group(1))
        result['max_rent'] = int(rent_match.group(2))

    for state in State.objects.all():
        if state.state and state.state.lower() in text_lower:
            result['state'] = state.state
            break

    for dist in District.objects.all():
        if dist.dist and dist.dist.lower() in text_lower:
            result['dist'] = dist.dist
            break

    return result


def extract_keywords(text):
    words = re.findall(r"\w+", (text or '').lower())
    return [word for word in words if len(word) > 2]


def log_user_search(user, search_data, viewed_room=None):
    """Log user search history for personalization."""
    if not user or not user.is_authenticated:
        return

    UserSearchHistory.objects.create(
        user=user,
        search_query=search_data.get('query', ''),
        state=search_data.get('state_obj'),
        district=search_data.get('dist_obj'),
        min_rent=search_data.get('min_rent'),
        max_rent=search_data.get('max_rent'),
        viewed_room=viewed_room
    )

def get_user_preferences(user):
    """Get user preferences based on search history."""
    if not user or not user.is_authenticated:
        return {}

    history = UserSearchHistory.objects.filter(user=user).order_by('-timestamp')[:20]

    if not history:
        return {}

    # Analyze preferences
    states = [h.state for h in history if h.state]
    districts = [h.district for h in history if h.district]
    rents = [h.min_rent or 0 for h in history if h.min_rent] + [h.max_rent or 0 for h in history if h.max_rent]
    search_terms = []
    viewed_room_ids = []

    for h in history:
        if h.search_query:
            search_terms.extend(extract_keywords(h.search_query))
        if h.viewed_room_id:
            viewed_room_ids.append(h.viewed_room_id)

    preferred_state = max(set(states), key=states.count) if states else None
    preferred_district = max(set(districts), key=districts.count) if districts else None
    avg_rent = sum(rents) / len(rents) if rents else None
    keyword_counts = Counter(search_terms)
    top_keywords = [word for word, count in keyword_counts.most_common(10)]

    return {
        'preferred_state': preferred_state,
        'preferred_district': preferred_district,
        'avg_rent_preference': avg_rent,
        'search_keywords': top_keywords,
        'viewed_room_ids': viewed_room_ids,
        'total_searches': len(history)
    }

def recommend_rooms(user=None, top=6):
    """Return a small recommended set of rooms based on user location or recent data."""
    base = Owner_Detail.objects.filter(status__status='accepted')

    if not user or not getattr(user, 'is_authenticated', False):
        return base.order_by('-id')[:top]

    prefs = get_user_preferences(user)
    if not prefs:
        return base.order_by('-id')[:top]

    best_rooms = base
    if prefs.get('preferred_district'):
        best_rooms = best_rooms.filter(dist=prefs['preferred_district'])
    elif prefs.get('preferred_state'):
        best_rooms = best_rooms.filter(state=prefs['preferred_state'])

    if prefs.get('avg_rent_preference'):
        avg_rent = prefs['avg_rent_preference']
        best_rooms = best_rooms.filter(rent__gte=max(0, avg_rent * 0.7), rent__lte=avg_rent * 1.3)

    if not best_rooms.exists():
        best_rooms = base

    preference_keywords = prefs.get('search_keywords', [])
    viewed_room_ids = set(prefs.get('viewed_room_ids', []))

    scored = []
    for room in best_rooms:
        score = 0
        if prefs.get('preferred_district') and room.dist == prefs['preferred_district']:
            score += 70
        elif prefs.get('preferred_state') and room.state == prefs['preferred_state']:
            score += 40

        if room.rent and prefs.get('avg_rent_preference'):
            avg_rent = prefs['avg_rent_preference']
            diff = abs(room.rent - avg_rent)
            score += max(0, 30 - diff // 1000)

        room_text = ' '.join(filter(None, [room.title, room.desc, room.local_add, room.area or '', room.state.state if room.state else '', room.dist.dist if room.dist else ''])).lower()
        for keyword in preference_keywords:
            if keyword in room_text:
                score += 5

        if room.id in viewed_room_ids:
            score += 20

        # Favor recent listings as a tie-breaker
        score += room.id / 100000.0
        scored.append((score, room))

    scored.sort(key=lambda item: item[0], reverse=True)
    recommended = [room for score, room in scored][:top]
    if len(recommended) < top:
        remaining = [room for room in best_rooms if room not in recommended]
        recommended.extend(remaining[:top - len(recommended)])

    return recommended


def spam_score(title, desc):
    """Simple spam score for new listings."""
    text = ' '.join([str(title or ''), str(desc or '')]).lower()
    bad_words = ['free', 'urgent', 'call now', 'whatsapp', 'broker', 'contact', 'urgent', 'book now']
    return sum(word in text for word in bad_words)


def is_spam_listing(title, desc):
    return spam_score(title, desc) >= 2


def image_quality_note(file_field):
    """Placeholder image quality note based on file size."""
    if not file_field:
        return 'No image provided.'
    size = getattr(file_field, 'size', 0)
    if size < 20000:
        return 'Image file is very small; upload a higher quality photo.'
    return 'Image size looks good for a listing.'

def analyze_image_quality(file_field):
    """Analyze image quality using PIL - checks resolution, format, and basic quality."""
    if not file_field:
        return {'quality': 'poor', 'score': 0, 'notes': ['No image provided']}

    try:
        # Open image from file field
        image = PILImage.open(file_field)
        width, height = image.size
        file_size = getattr(file_field, 'size', 0)
        format_type = image.format

        score = 0
        notes = []

        # Resolution check
        if width >= 800 and height >= 600:
            score += 40
            notes.append('Good resolution')
        elif width >= 400 and height >= 300:
            score += 20
            notes.append('Acceptable resolution')
        else:
            notes.append('Low resolution - consider higher quality image')

        # File size check
        if file_size >= 50000:
            score += 30
            notes.append('Good file size')
        elif file_size >= 20000:
            score += 15
            notes.append('Acceptable file size')
        else:
            notes.append('Small file size - may appear blurry')

        # Format check
        if format_type in ['JPEG', 'PNG']:
            score += 20
            notes.append('Good format')
        else:
            notes.append('Consider JPEG or PNG format')

        # Brightness check (simple)
        if image.mode == 'RGB':
            pixels = list(image.getdata())
            avg_brightness = sum((r + g + b) / 3 for r, g, b in pixels) / len(pixels)
            if avg_brightness > 100:
                score += 10
                notes.append('Good brightness')
            elif avg_brightness > 50:
                notes.append('Average brightness')
            else:
                notes.append('Low brightness - may be too dark')

        quality = 'excellent' if score >= 90 else 'good' if score >= 70 else 'fair' if score >= 50 else 'poor'

        return {
            'quality': quality,
            'score': score,
            'resolution': f'{width}x{height}',
            'format': format_type,
            'size_kb': round(file_size / 1024, 1),
            'notes': notes
        }

    except Exception as e:
        return {'quality': 'error', 'score': 0, 'notes': [f'Error analyzing image: {str(e)}']}
