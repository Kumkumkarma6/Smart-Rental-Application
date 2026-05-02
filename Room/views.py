from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import UserProfile
from .models import *
from django.contrib.auth import authenticate, logout, login
from .ml import estimate_rent, parse_search_text, rank_rooms, recommend_rooms, log_user_search, analyze_image_quality, get_user_preferences, haversine_distance



# Create your views here.
def home(request):
    return render(request,'carousel.html')

@login_required
def user_profile(request):
    try:
        profile = UserProfile.objects.filter(user=request.user).first()
        user_listings = Property.objects.filter(landlord=request.user).select_related('district') if profile else Property.objects.none()
        user_prefs = get_user_preferences(request.user)
        context = {
            'user': request.user,
            'user_listings': user_listings,
            'user_prefs': user_prefs
        }
        return render(request, 'user_profile.html', context)
    except Exception as e:
        print(f"Error in user_profile view: {str(e)}")
        context = {
            'user': request.user,
            'user_listings': []
        }
        return render(request, 'user_profile.html', context)


def Listings(request):
    active_tab = request.GET.get('tab', 'recommended')
    page_number = request.GET.get('page')
    # Show approved listings plus user's own pending listings
    if request.user.is_authenticated:
        rooms = Property.objects.filter(
            models.Q(status='approved') |
            models.Q(status='pending', landlord=request.user)
        ).select_related('landlord__profile', 'state', 'district', 'area')
    else:
        rooms = Property.objects.filter(status='approved').select_related('landlord__profile', 'state', 'district', 'area')
    paginator = Paginator(rooms, 8)
    page_obj = paginator.get_page(page_number)

    recommended = []
    if active_tab == 'recommended':
        recommended = recommend_rooms(request.user, top=6)

    predict_state = request.GET.get('predict_state', '')
    predict_dist = request.GET.get('predict_dist', '')
    predict_title = request.GET.get('predict_title', '')
    predict_desc = request.GET.get('predict_desc', '')
    price_prediction = None
    if active_tab == 'prediction':
        price_prediction = estimate_rent(
            state_name=predict_state,
            district_name=predict_dist,
            title=predict_title,
            desc=predict_desc
        )

    context = {
        'page_obj': page_obj,
        'recommended': recommended,
        'active_tab': active_tab,
        'states': State.objects.all(),
        'districts': District.objects.all(),
        'predict_state': predict_state,
        'predict_dist': predict_dist,
        'predict_title': predict_title,
        'predict_desc': predict_desc,
        'price_prediction': price_prediction,
    }
    return render(request, 'listings.html', context)

@login_required
def edit_profile(request):
    # Get or create UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        try:
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            
            # Update profile fields
            profile.phone = request.POST.get('phone', '')
            profile.location = request.POST.get('location', '')
            profile.bio = request.POST.get('bio', '')
            
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            user.save()
            profile.save()
            return redirect('user_profile')
        except Exception as e:
            print(f"Error saving profile: {str(e)}")
            
    context = {
        'profile': profile
    }
    return render(request, 'edit_profile.html', context)
def About(request):
    return render(request,'about.html')

def signup_role(request):
    """Show role selection page"""
    return render(request, 'signup_role.html')

def signup_tenant(request):
    """Tenant signup - Direct to search page"""
    error = None
    if request.method == "POST":
        u = request.POST.get('uname', '').strip()
        p = request.POST.get('pwd', '')
        e = request.POST.get('email', '').strip()

        if User.objects.filter(username=u).exists():
            error = 'Username already exists. Please choose a different username.'
        else:
            try:
                user = User.objects.create_user(username=u, password=p, email=e)
                UserProfile.objects.create(user=user, role='tenant')
                error = 'success'
            except Exception as exc:
                error = 'Error creating account. Please try again.'
                print(f"Tenant signup error: {exc}")

    d = {'error': error}
    return render(request, 'signup_tenant.html', d)

def signup_landlord(request):
    """Landlord signup - Full registration"""
    error = None
    if request.method == "POST":
        f = request.POST.get('fname', '').strip()
        l = request.POST.get('lname', '').strip()
        u = request.POST.get('uname', '').strip()
        p = request.POST.get('pwd', '')
        p_confirm = request.POST.get('pwd_confirm', '')
        phone = request.POST.get('phone', '').strip()
        e = request.POST.get('email', '').strip()
        g = request.POST.get('gender', '').strip()
        ad = request.POST.get('address', '').strip()

        # Validations
        if len(p) < 6:
            error = 'Password must be at least 6 characters long.'
        elif p != p_confirm:
            error = 'Passwords do not match.'
        elif User.objects.filter(username=u).exists():
            error = 'Username already exists. Please choose a different username.'
        elif len(phone) != 10 or not phone.isdigit():
            error = 'Phone number must be 10 digits.'
        else:
            try:
                user = User.objects.create_user(first_name=f, last_name=l, username=u, password=p, email=e)
                UserProfile.objects.create(user=user, role='landlord', phone=phone, gender=g, address=ad)
                error = 'success'
            except Exception as exc:
                error = 'Error creating account. Please try again.'
                print(f"Landlord signup error: {exc}")

    d = {'error': error}
    return render(request, 'signup_landlord.html', d)

def signup(request):
    """Legacy signup - redirect to role selection"""
    return redirect('signup_role')

def signin_role(request):
    """Show role selection for signin"""
    return render(request, 'signin_role.html')

def signin(request):
    error = ""
    if request.method == "POST":
        u = request.POST.get('uname', '')
        p = request.POST.get('pwd', '')
        role = request.POST.get('role', 'tenant')
        
        user = authenticate(username=u, password=p)
        try:
            if user:
                # Check if user role matches selected role
                try:
                    profile = UserProfile.objects.get(user=user)
                    user_role = profile.role
                except UserProfile.DoesNotExist:
                    user_role = 'tenant'
                
                # Allow admin login regardless
                if user.is_staff:
                    login(request, user)
                    error = "admin"
                # Allow login with matching role
                elif user_role == role or role == 'any':
                    login(request, user)
                    # Redirect based on role
                    if user_role == 'landlord':
                        return redirect('user_profile')
                    else:
                        return redirect('search')
                else:
                    error = "role_mismatch"
            else:
                error = "yes"
        except Exception as e:
            print(f"Signin error: {e}")
            error = "yes"
    
    d = {'error': error}
    return render(request, 'signin.html', d)

def Logout(request):
    logout(request)
    return redirect('home')

def Search(request):
    rooms = Property.objects.filter(status='approved')
    state1 = State.objects.all()
    dist1 = District.objects.all()
    area1 = Area.objects.all()
    query = ''
    selected_state = None
    selected_dist = None
    selected_area = ''
    selected_min_rent = ''
    selected_max_rent = ''
    sort_order = ''
    selected_dist_id = None
    search_data = {}

    data = request.GET if request.method == 'GET' else request.POST
    query = data.get('query', '').strip()
    selected_state = data.get('state', '').strip()
    selected_dist = data.get('dist', '').strip()
    selected_area = data.get('area', '').strip()
    min_rent = data.get('min_rent', '').strip()
    max_rent = data.get('max_rent', '').strip()
    sort_order = data.get('sort', '').strip()

    if selected_state:
        try:
            state_id = int(selected_state)
            state_obj = State.objects.get(id=state_id)
            rooms = rooms.filter(state=state_obj)
            search_data['state'] = state_obj.name
            search_data['state_obj'] = state_obj
        except (ValueError, State.DoesNotExist):
            pass

    if selected_dist:
        try:
            dist_id = int(selected_dist)
            dist_obj = District.objects.get(id=dist_id)
            selected_dist_id = dist_obj.id
            rooms = rooms.filter(district=dist_obj)
            search_data['dist'] = dist_obj.name
            search_data['dist_obj'] = dist_obj
            area1 = Area.objects.filter(district=dist_obj)
        except (ValueError, District.DoesNotExist):
            pass

    if selected_area:
        rooms = rooms.filter(area__icontains=selected_area)
        search_data['area'] = selected_area

    if min_rent or max_rent:
        low = int(min_rent) if min_rent.isdigit() else 0
        high = int(max_rent) if max_rent.isdigit() else 9999999
        rooms = rooms.filter(rent__gte=low, rent__lte=high)
        search_data['min_rent'] = low
        search_data['max_rent'] = high
        selected_min_rent = min_rent
        selected_max_rent = max_rent

    if query:
        parsed = parse_search_text(query)
        if parsed['state']:
            state_obj = State.objects.filter(name__iexact=parsed['state']).first()
            if state_obj:
                rooms = rooms.filter(state=state_obj)
                search_data['state'] = parsed['state']
                search_data['state_obj'] = state_obj
                dist1 = District.objects.filter(state=state_obj)

        if parsed['dist']:
            dist_obj = District.objects.filter(name__iexact=parsed['dist']).first()
            if dist_obj:
                selected_dist_id = dist_obj.id
                rooms = rooms.filter(district=dist_obj)
                search_data['dist'] = parsed['dist']
                search_data['dist_obj'] = dist_obj
                area1 = Area.objects.filter(district=dist_obj)

        if parsed.get('area'):
            rooms = rooms.filter(area__icontains=parsed['area'])
            search_data['area'] = parsed['area']

        if parsed['min_rent'] or parsed['max_rent']:
            low = parsed['min_rent'] if parsed['min_rent'] else 0
            high = parsed['max_rent'] if parsed['max_rent'] else 9999999
            rooms = rooms.filter(rent__gte=low, rent__lte=high)
            search_data['min_rent'] = low
            search_data['max_rent'] = high

        rooms = rooms.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(area__icontains=query) |
            models.Q(address__icontains=query) |
            models.Q(state__name__icontains=query) |
            models.Q(district__name__icontains=query) |
            models.Q(landlord__first_name__icontains=query) |
            models.Q(landlord__last_name__icontains=query) |
            models.Q(landlord__username__icontains=query)
        )
        search_data['query'] = query

    if sort_order == 'rent_asc':
        rooms = rooms.order_by('rent')
    elif sort_order == 'rent_desc':
        rooms = rooms.order_by('-rent')

    log_user_search(request.user if request.user.is_authenticated else None, search_data)

    page_number = request.GET.get('page')
    paginator = Paginator(rooms, 12)
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    query_string = query_params.urlencode()

    d = {
        'state': state1,
        'dist': dist1,
        'area': area1,
        'page_obj': page_obj,
        'query_string': query_string,
        'query': query,
        'searched': bool(request.GET),
        'selected_state': selected_state,
        'selected_dist': selected_dist,
        'selected_dist_id': selected_dist_id,
        'selected_area': selected_area,
        'min_rent': selected_min_rent,
        'max_rent': selected_max_rent,
        'sort_order': sort_order
    }
    return render(request, 'serach.html', d)

def get_districts(request):
    state_id = request.GET.get('state_id')
    districts = District.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)

def get_areas(request):
    district_id = request.GET.get('district_id')
    if district_id:
        # Get unique areas from Area model that belong to this district
        try:
            areas = Area.objects.filter(district_id=district_id).values('id', 'name').order_by('name')
            return JsonResponse(list(areas), safe=False)
        except:
            return JsonResponse([], safe=False)
    return JsonResponse([], safe=False)

def dist(request,dist):
    state=State.objects.get(id=dist)
    room=Property.objects.filter(state=state).all()
    dist=District.objects.filter(state=dist)
    if request.method=='POST':
        s=request.POST['dist']
        dist1=District.objects.filter(dist=s).first()
        return redirect('room',dist1.id)
    d={'dist':dist,'state':state,'room':room}
    return render(request,'dist.html',d)

def room(request,dist):
    dist1 = District.objects.get(id=dist)
    room = Property.objects.filter(district=dist1, status='approved')
    area_list = Area.objects.filter(district=dist1)
    search_query = request.GET.get('q', '').strip()
    area_filter = request.GET.get('area', '').strip()
    
    if area_filter:
        room = room.filter(area__iexact=area_filter)
    
    if search_query:
        room = rank_rooms(search_query, room)
    
    d = {'room': room, 'dist': dist1, 'search_query': search_query, 'areas': area_list, 'selected_area': area_filter}
    return render(request, 'room.html', d)


def predict_rent(request):
    estimate = None
    selected_state = None
    selected_dist = None
    state_list = State.objects.all()
    dist_list = District.objects.all()
    if request.method == 'POST':
        selected_state = request.POST.get('state', '').strip()
        selected_dist = request.POST.get('dist', '').strip()
        title = request.POST.get('title', '').strip()
        desc = request.POST.get('desc', '').strip()
        estimate = estimate_rent(selected_state, selected_dist, title=title, desc=desc)
    d = {
        'estimate': estimate,
        'state_list': state_list,
        'dist_list': dist_list,
        'selected_state': selected_state,
        'selected_dist': selected_dist,
    }
    return render(request, 'rent_predict.html', d)


def recommendations(request):
    rooms = recommend_rooms(request.user, top=8)
    prefs = get_user_preferences(request.user) if request.user.is_authenticated else {}
    d = {
        'rooms': rooms,
        'prefs': prefs,
    }
    return render(request, 'recommendations.html', d)

def detail(request,dist):
    own=Property.objects.get(id=dist)
    img = PropertyImage.objects.filter(property=own)
    # Log room view
    log_user_search(request.user, {}, viewed_property=own)
    
    # Get nearby properties (same area, district, within 5000 rent range)
    nearby_candidates = Property.objects.filter(
        status='approved',
        district=own.district
    ).exclude(id=own.id)

    nearby = []
    if own.latitude is not None and own.longitude is not None:
        nearby_with_distance = []
        for prop in nearby_candidates:
            if prop.latitude is None or prop.longitude is None:
                continue
            distance_km = haversine_distance(own.latitude, own.longitude, prop.latitude, prop.longitude)
            if distance_km <= 10:
                nearby_with_distance.append((distance_km, prop))

        nearby_with_distance.sort(key=lambda item: item[0])
        nearby = [prop for _, prop in nearby_with_distance][:5]

    if len(nearby) < 5:
        existing_ids = [prop.id for prop in nearby]
        more = nearby_candidates.exclude(id__in=existing_ids)[:5 - len(nearby)]
        nearby.extend(list(more))

    d={'img':img,'dist':own, 'nearby': nearby}
    return render(request,'detail.html',d)

def detail1(request,dist):
    if not request.user.is_authenticated:
        return redirect('home')
    own=Property.objects.get(id=dist)
    img = PropertyImage.objects.filter(property=own)
    
    # Get nearby properties (same area, district, within 5000 rent range)
    nearby_candidates = Property.objects.filter(
        status='approved',
        district=own.district
    ).exclude(id=own.id)

    nearby = []
    if own.latitude is not None and own.longitude is not None:
        nearby_with_distance = []
        for prop in nearby_candidates:
            if prop.latitude is None or prop.longitude is None:
                continue
            distance_km = haversine_distance(own.latitude, own.longitude, prop.latitude, prop.longitude)
            if distance_km <= 10:
                nearby_with_distance.append((distance_km, prop))

        nearby_with_distance.sort(key=lambda item: item[0])
        nearby = [prop for _, prop in nearby_with_distance][:5]

    if len(nearby) < 5:
        existing_ids = [prop.id for prop in nearby]
        more = nearby_candidates.exclude(id__in=existing_ids)[:5 - len(nearby)]
        nearby.extend(list(more))

    d={'img':img,'dist':own, 'nearby': nearby}
    return render(request,'detail1.html',d)


def Contact(request):
    return render(request,'contact.html')

def rent1(request):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    st=State.objects.all()
    if request.method=="POST":
        try:
            s=request.POST['state']
            state=State.objects.filter(name=s).first()
            return redirect('rent',state.id)

        except:
            pass

    d={'state':st,'error':error}
    return render(request,'rent.html',d)

def rent(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    form_error = None
    st2=State.objects.all()
    st=State.objects.get(id=pid)
    # Always get a fresh list of districts for this state
    dist2=District.objects.filter(state=st).order_by('name')
    image_analysis = None
    if request.method=="POST":
        try:
            d=request.POST['dist']
            a=request.POST.get('area', '').strip()
            l=request.POST['local']
            t=request.POST['title']
            de=request.POST['desc']
            r=request.POST['rent']
            raw_lat=request.POST.get('latitude', '').strip()
            raw_lng=request.POST.get('longitude', '').strip()
            lat = None
            lng = None

            if raw_lat:
                try:
                    lat = float(raw_lat)
                except ValueError:
                    raise ValueError('Latitude must be a valid number.')

            if raw_lng:
                try:
                    lng = float(raw_lng)
                except ValueError:
                    raise ValueError('Longitude must be a valid number.')

            i=request.FILES.get('img')

            if not i:
                raise ValueError('Image is required to submit the listing.')

            dist1 = District.objects.filter(name=d, state=st).first()
            if not dist1:
                raise ValueError('Please select a valid district for the selected state.')

            # Get or create the Area
            area_obj = None
            if a:  # Only create area if provided
                area_obj, _ = Area.objects.get_or_create(
                    district=dist1,
                    name=a
                )

            # Analyze image quality
            image_analysis = analyze_image_quality(i)

            Property.objects.create(
                status='pending',
                landlord=request.user,
                state=st,
                district=dist1,
                area=area_obj,
                address=l,
                title=t,
                description=de,
                rent=r,
                latitude=lat,
                longitude=lng,
                featured_image=i
            )
            error=True
        except Exception as exc:
            print(f"Error creating listing: {exc}")
            form_error = str(exc) if str(exc) else 'Failed to submit listing. Please check the fields.'
    d={'dist':dist2,'state':st2,'st':st,'error':error, 'image_analysis': image_analysis, 'form_error': form_error}
    return render(request,'rent.html',d)

def Room_Img(request):
    if not request.user.is_authenticated:
        return redirect('home')
    user=User.objects.get(id=request.user.id)
    room=Property.objects.filter(landlord=user).select_related('landlord__profile', 'state', 'district', 'area').all()
    d={'room':room}
    return render(request,'room_image.html',d)

def Add_Room_Img(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    room=Property.objects.get(id=pid)
    if request.method=="POST":
        r=request.POST['name']
        i=request.FILES['img']
        PropertyImage.objects.create(property=room,title=r,image=i)
        error=True
    d={'error':error,'pid':pid}
    return render(request,'add_room_img.html',d)

def Owner_detail(request,pid):
    own=Property.objects.get(id=pid)
    d={'own':own}
    return render(request,'owner_detail.html',d)

def User_detail(request):
    if not request.user.is_authenticated:
        return redirect('home')
    user=User.objects.filter(id=request.user.id).first()
    profile=UserProfile.objects.filter(user=user).first()
    d={'profile':profile}
    return render(request,'user_detail.html',d)


def edit_detail1(request,data):
    if not request.user.is_authenticated:
        return redirect('home')
    error = False
    st = State.objects.all()
    if request.method == "POST":
        try:
            s = request.POST['state']
            state = State.objects.filter(name=s).first()
            return redirect('edit_detail', state.id,data)

        except:
            pass

    d = {'state': st, 'error': error}
    return render(request, 'edit_detail.html', d)


def Edit_detail(request,data1,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    data=Property.objects.get(id=pid)
    state=State.objects.all()
    st = State.objects.get(id=data1)
    dist2 = District.objects.filter(state=st).order_by('name')
    if request.method=="POST":
        try:
            s = request.POST['state']
        except:
            pass
        d = request.POST['dist']
        a = request.POST.get('area', '').strip()
        l = request.POST['local']
        t = request.POST['title']
        de = request.POST['desc']
        r = request.POST['rent']
        raw_lat = request.POST.get('latitude', '').strip()
        raw_lng = request.POST.get('longitude', '').strip()
        lat = None
        lng = None

        if raw_lat:
            try:
                lat = float(raw_lat)
            except ValueError:
                lat = None

        if raw_lng:
            try:
                lng = float(raw_lng)
            except ValueError:
                lng = None

        try:
            i = request.FILES['img']
            data.featured_image = i
            data.save()
        except:
            pass

        dist1 = District.objects.filter(name=d).first()
        if dist1:
            data.state = st
            data.district = dist1
            # Get or create the Area
            if a:
                area_obj, _ = Area.objects.get_or_create(
                    district=dist1,
                    name=a
                )
                data.area = area_obj
        data.description = de
        data.rent = r
        data.latitude = lat
        data.longitude = lng
        data.address = l
        data.title = t
        data.save()
        error=True
    d={'data':data,'dist':dist2,'state':state,'st':st,'error':error}
    return render(request,'edit_detail.html',d)

def delete_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    Own=Property.objects.get(id=pid)
    Own.delete()
    return redirect('img')


def delete_user(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    Own=UserProfile.objects.get(id=pid)
    Own.delete()
    return redirect('view_user')

def delete_dist(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    Own=District.objects.get(id=pid)
    Own.delete()
    return redirect('view_dist')

def delete_state(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    Own=State.objects.get(id=pid)
    Own.delete()
    return redirect('view_state')

def View_User(request):
    if not request.user.is_staff:
        return redirect('home')
    data=UserProfile.objects.all()
    d={'data':data}
    return render(request,'view_user.html',d)

def Edit_User(request,pid):
    if not request.user.is_staff:
        return redirect('home')
    error = False
    data=UserProfile.objects.get(id=pid)
    if request.method=="POST":
        u=request.POST['uname']
        f=request.POST['fname']
        l=request.POST['lname']
        e=request.POST['email']
        m=request.POST['mobile']
        a=request.POST['add']
        data.user.username=u
        data.user.first_name=f
        data.user.last_name=l
        data.user.email=e
        data.address=a
        data.phone=m
        data.save()
        error=True
    d={'data':data,'error':error}
    return render(request,'edit_user.html',d)

def Edit_State(request,pid):
    if not request.user.is_staff:
        return redirect('home')
    error = False
    data=State.objects.get(id=pid)
    if request.method=="POST":
        u=request.POST['state']
        data.name=u
        data.save()
        error=True
    d={'data':data,'error':error}
    return render(request,'edit_state.html',d)
def Add_State(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method=="POST":
        s=request.POST['state']
        State.objects.create(name=s)
        return redirect('view_state')
    return render(request,'add_state.html')
def Add_District(request):
    if not request.user.is_authenticated:
        return redirect('signin')
        
    state=State.objects.all()
    # allow pre-selecting state via query param ?state=<id>
    sel = request.GET.get('state')
    try:
        selected_state_id = int(sel) if sel else None
    except (ValueError, TypeError):
        selected_state_id = None
        
    if request.method=="POST":
        s=request.POST['state']
        d=request.POST['dist']
        st=State.objects.get(name=s)
        
        # Create district directly (we removed staff check)
        District.objects.create(state=st, name=d)
        
        # For all users, redirect to rent1 to force a fresh state selection
        # This ensures the new district appears in the dropdown
        return redirect('rent1')
    d={'state':state, 'selected_state_id': selected_state_id}
    return render(request,'add_dist.html',d)
def View_State(request):
    if not request.user.is_staff:
        return redirect('home')
    state=State.objects.all()
    d={'state':state}
    return render(request,'view_state.html',d)

def View_District(request):
    if not request.user.is_staff:
        return redirect('home')
    dist=District.objects.all()
    d={'dist':dist}
    return render(request,'view_dist.html',d)

def View_Request(request):
    if not request.user.is_staff:
        return redirect('home')
    error=True
    # Only show pending properties that need approval
    pending_properties = Property.objects.filter(status='pending').select_related('landlord', 'state', 'district', 'area')
    d={'data': pending_properties, 'pending_count': pending_properties.count()}
    return render(request,"request.html",d)

def Change(request,data,pid):
    if not request.user.is_staff:
        return redirect('home')
    own=Property.objects.get(id=pid)
    if int(data) == 1:
        own.status='approved'
        own.save()
    elif int(data) == 2:
        own.status='rejected'
        own.save()
    return redirect('request')

def All_Ads(request):
    if not request.user.is_staff:
        return redirect('home')
    data=Property.objects.all()
    d={'data':data}
    return render(request,'all_ads.html',d)

def Change_Img(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    img=Image.objects.get(id=pid)
    if request.method=="POST":
        i=request.FILES['img']
        n=request.POST['name']
        img.room_name=n
        img.img=i
        img.save()
        error=True
    d={'error':error,'img':img}
    return render(request,'changeimg.html',d)

