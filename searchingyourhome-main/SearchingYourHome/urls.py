"""SearchingYourHome URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Room.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup', signup, name='signup'),
    path('signup_role', signup_role, name='signup_role'),
    path('signup_tenant', signup_tenant, name='signup_tenant'),
    path('signup_landlord', signup_landlord, name='signup_landlord'),
    path('signin', signin, name='signin'),
    path('signin_role', signin_role, name='signin_role'),
    path('logout', Logout, name='logout'),
    path('search', Search, name='search'),
    path('recommendations', recommendations, name='recommendations'),
    path('predict_rent', predict_rent, name='predict_rent'),
    path('contact', Contact, name='contact'),
    path('about', About, name='about'),
    path('view_user', View_User, name='view_user'),
    path('rent1', rent1, name='rent1'),
    path('img', Room_Img, name='img'),
    path('add_state', Add_State, name='add_state'),
    path('view_state', View_State, name='view_state'),
    path('view_dist', View_District, name='view_dist'),
    path('add_dist', Add_District, name='add_dist'),
    path('request', View_Request, name='request'),
    path('user_detail', User_detail, name='user_detail'),
    path('all_ads', All_Ads, name='all_ads'),
    path('owner/<int:pid>', Owner_detail, name='owner'),
    path('edit_detail/<int:data1>/<int:pid>', Edit_detail, name='edit_detail'),
    path('change/<int:data>/<int:pid>/', Change, name='change'),
    path('delete_detail/<int:pid>', delete_detail, name='delete'),
    path('edit_detail1/<int:data>', edit_detail1, name='edit_detail1'),
    path('edit_state/<int:pid>', Edit_State, name='edit_state'),
    path('room_img/<int:pid>', Add_Room_Img, name='room_img'),
    path('dist/<int:dist>', dist, name='dist'),
    path('rent/<int:pid>', rent, name='rent'),
    path('room/<int:dist>', room, name='room'),
    path('edit_user/<int:pid>', Edit_User, name='edit_user'),
    path('delete_user/<int:pid>', delete_user, name='delete_user'),
    path('delete_dist/<int:pid>', delete_dist, name='delete_dist'),
    path('delete_state/<int:pid>', delete_state, name='delete_state'),
    path('change_img/<int:pid>', Change_Img, name='change_img'),
    path('detail/<int:dist>', detail, name='detail'),
    path('detail1/<int:dist>', detail1, name='detail1'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
