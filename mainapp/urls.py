from django.urls import path, include
from . import views 


urlpatterns = [
    path('', views.landingpage, name='homepage'),
    path('/homepage', views.homepage, name='homepage')  
    
] 
