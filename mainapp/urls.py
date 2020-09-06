from django.urls import path, include
from . import views 


urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('homepage', views.homepage, name='homepage'),  
    path('signup/', views.signup, name='signup'),
    path('playground/', views.playground, name='playground'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('risk/',views.risk, name='risk'),
    path('register/',views.register, name='register')
]
