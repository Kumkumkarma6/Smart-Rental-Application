from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q
from .models import UserProfile
from .models import *
from django.contrib.auth import authenticate, logout, login
from .ml import estimate_rent, parse_search_text, rank_rooms, recommend_rooms, log_user_search, analyze_image_quality, get_user_preferences



# Create your views here.
def home(request):
    return render(request,'carousel.html')

@login_required
def user_profile(request):
    try:
        user_listings = Owner_Detail.objects.filter(register=request.user.username).select_related('dist')
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
                Register.objects.create(user=user, role='tenant')
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
                Register.objects.create(user=user, role='landlord', mobile=phone, gen=g, add=ad)
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
                    register = Register.objects.get(user=user)
                    user_role = register.role
                except Register.DoesNotExist:
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
    room = Owner_Detail.objects.filter(status__status='accepted')
    state1 = State.objects.all()
    dist1 = District.objects.all()
    area1 = Area.objects.all()
    query = ''
    selected_state = None
    selected_dist = None
    selected_dist_id = None
    selected_area = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        selected_state = request.POST.get('state', '').strip()
        selected_dist = request.POST.get('dist', '').strip()
        selected_area = request.POST.get('area', '').strip()
        min_rent = request.POST.get('min_rent', '').strip()
        max_rent = request.POST.get('max_rent', '').strip()
        
        search_data = {}
        
        # Filter by area if selected
        if selected_area:
            room = room.filter(area__iexact=selected_area)
            search_data['area'] = selected_area
        
        # Filter by district if selected
        if selected_dist:
            dist_obj = District.objects.filter(dist__iexact=selected_dist).first()
            if dist_obj:
                selected_dist_id = dist_obj.id
                room = room.filter(dist=dist_obj)
                search_data['dist'] = selected_dist
                search_data['dist_obj'] = dist_obj
        
        # Filter by state if selected
        if selected_state:
            state_obj = State.objects.filter(state__iexact=selected_state).first()
            if state_obj:
                room = room.filter(state=state_obj)
                search_data['state'] = selected_state
                search_data['state_obj'] = state_obj
        
        # Filter by rent range
        if min_rent or max_rent:
            low = int(min_rent) if min_rent else 0
            high = int(max_rent) if max_rent else 9999999
            room = room.filter(rent__gte=low, rent__lte=high)
            search_data['min_rent'] = low
            search_data['max_rent'] = high
        
        # Text query search
        if query:
            room = room.filter(
                models.Q(title__icontains=query) |
                models.Q(desc__icontains=query) |
                models.Q(area__icontains=query) |
                models.Q(local_add__icontains=query)
            )
            search_data['query'] = query
        
        # Log user search
        log_user_search(request.user, search_data)
    else:
        # If no POST, check if there's a state parameter in GET
        selected_state = request.GET.get('state', '').strip()
        if selected_state:
            state_obj = State.objects.filter(state__iexact=selected_state).first()
            if state_obj:
                district_list = District.objects.filter(state=state_obj)
                dist1 = district_list

    d = {
        'state': state1, 
        'dist': dist1, 
        'area': area1, 
        'room': room, 
        'query': query, 
        'searched': request.method == 'POST',
        'selected_state': selected_state,
        'selected_dist': selected_dist,
        'selected_dist_id': selected_dist_id,
        'selected_area': selected_area
    }
    return render(request, 'serach.html', d)
def dist(request,dist):
    state=State.objects.get(id=dist)
    room=Owner_Detail.objects.filter(state=state).all()
    dist=District.objects.filter(state=dist)
    if request.method=='POST':
        s=request.POST['dist']
        dist1=District.objects.filter(dist=s).first()
        return redirect('room',dist1.id)
    d={'dist':dist,'state':state,'room':room}
    return render(request,'dist.html',d)

def room(request,dist):
    dist1 = District.objects.get(id=dist)
    room = Owner_Detail.objects.filter(dist=dist1, status__status='accepted')
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
    own=Owner_Detail.objects.get(id=dist)
    img = Image.objects.filter(owner=own)
    # Log room view
    log_user_search(request.user, {}, viewed_room=own)
    
    # Get nearby properties (same area, district, within 5000 rent range)
    nearby = Owner_Detail.objects.filter(
        status__status='accepted',
        area=own.area,
        dist=own.dist
    ).exclude(id=own.id)[:5]
    
    d={'img':img,'dist':own, 'nearby': nearby}
    return render(request,'detail.html',d)

def detail1(request,dist):
    if not request.user.is_authenticated:
        return redirect('home')
    own=Owner_Detail.objects.get(id=dist)
    img = Image.objects.filter(owner=own)
    
    # Get nearby properties (same area, district, within 5000 rent range)
    nearby = Owner_Detail.objects.filter(
        status__status='accepted',
        area=own.area,
        dist=own.dist
    ).exclude(id=own.id)[:5]
    
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
            state=State.objects.filter(state=s).first()
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
    dist2=District.objects.filter(state=st).order_by('dist')
    image_analysis = None
    if request.method=="POST":
        try:
            d=request.POST['dist']
            a=request.POST.get('area', '').strip()
            l=request.POST['local']
            t=request.POST['title']
            de=request.POST['desc']
            r=request.POST['rent']
            lat=request.POST.get('latitude', None)
            lng=request.POST.get('longitude', None)
            i=request.FILES.get('img')

            if not i:
                raise ValueError('Image is required to submit the listing.')

            dist1 = District.objects.filter(dist=d, state=st).first()
            if not dist1:
                raise ValueError('Please select a valid district for the selected state.')

            req = User.objects.filter(username=request.user.username).first()
            re = Register.objects.filter(user=req).first()
            status, _ = Status.objects.get_or_create(status="pending")

            # Analyze image quality
            image_analysis = analyze_image_quality(i)

            Owner_Detail.objects.create(
                status=status,
                register=re,
                state=st,
                dist=dist1,
                area=a,
                local_add=l,
                title=t,
                desc=de,
                rent=r,
                latitude=lat if lat else None,
                longitude=lng if lng else None,
                img=i
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
    reg=Register.objects.filter(user=user).first()
    room=Owner_Detail.objects.filter(register=reg).all()
    d={'room':room}
    return render(request,'room_image.html',d)

def Add_Room_Img(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    room=Owner_Detail.objects.get(id=pid)
    if request.method=="POST":
        r=request.POST['name']
        i=request.FILES['img']
        Image.objects.create(owner=room,room_name=r,img=i)
        error=True
    d={'error':error,'pid':pid}
    return render(request,'add_room_img.html',d)

def Owner_detail(request,pid):
    own=Owner_Detail.objects.get(id=pid)
    d={'own':own}
    return render(request,'owner_detail.html',d)

def User_detail(request):
    if not request.user.is_authenticated:
        return redirect('home')
    user=User.objects.filter(id=request.user.id).first()
    register=Register.objects.filter(user=user).first()
    d={'register':register}
    return render(request,'user_detail.html',d)


def edit_detail1(request,data):
    if not request.user.is_authenticated:
        return redirect('home')
    error = False
    st = State.objects.all()
    if request.method == "POST":
        try:
            s = request.POST['state']
            state = State.objects.filter(state=s).first()
            return redirect('edit_detail', state.id,data)

        except:
            pass

    d = {'state': st, 'error': error}
    return render(request, 'edit_detail.html', d)


def Edit_detail(request,data1,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    error=False
    data=Owner_Detail.objects.get(id=pid)
    state=State.objects.all()
    st = State.objects.get(id=data1)
    dist2 = District.objects.filter(state=st)
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
        lat = request.POST.get('latitude', None)
        lng = request.POST.get('longitude', None)
        try:
            i = request.FILES['img']
            data.img = i
            data.save()
        except:
            pass

        dist1 = District.objects.filter(dist=d).first()
        data.state = st
        data.dist = dist1
        data.area = a
        data.desc = de
        data.rent = r
        data.latitude = lat if lat else None
        data.longitude = lng if lng else None
        data.local_add = l
        data.title = t
        data.save()
        error=True
    d={'data':data,'dist':dist2,'state':state,'st':st,'error':error}
    return render(request,'edit_detail.html',d)

def delete_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    Own=Owner_Detail.objects.get(id=pid)
    Own.delete()
    return redirect('img')


def delete_user(request,pid):
    if not request.user.is_authenticated:
        return redirect('home')
    Own=Register.objects.get(id=pid)
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
    data=Register.objects.all()
    d={'data':data}
    return render(request,'view_user.html',d)

def Edit_User(request,pid):
    if not request.user.is_staff:
        return redirect('home')
    error = False
    data=Register.objects.get(id=pid)
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
        data.add=a
        data.mobile=m
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
        data.state=u
        data.save()
        error=True
    d={'data':data,'error':error}
    return render(request,'edit_state.html',d)
def Add_State(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method=="POST":
        s=request.POST['state']
        State.objects.create(state=s)
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
        st=State.objects.get(state=s)
        
        # Create district directly (we removed staff check)
        District.objects.create(state=st,dist=d)
        
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
    own=Owner_Detail.objects.all()
    d={'data':own}
    return render(request,"request.html",d)

def Change(request,data,pid):
    if not request.user.is_staff:
        return redirect('home')
    own=Owner_Detail.objects.get(id=pid)
    if int(data) == 1:
        st1=Status.objects.get(status="accepted")
        own.status=st1
        own.save()
    elif int(data) == 2:
        st2 = Status.objects.get(status="rejected")
        own.status = st2
        own.save()
    return redirect('request')

def All_Ads(request):
    if not request.user.is_staff:
        return redirect('home')
    data=Owner_Detail.objects.all()
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

