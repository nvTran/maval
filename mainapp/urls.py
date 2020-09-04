from django.urls import path, include
from . import views 


urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('homepage', views.homepage, name='homepage'),  
    path('signup/', views.signup, name='signup')
] 
