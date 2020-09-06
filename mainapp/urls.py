from django.urls import path, include
from . import views 


urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('homepage', views.homepage, name='homepage'),  
<<<<<<< Updated upstream
    path('signup/', views.signup, name='signup'),
    path('playground/', views.playground, name='playground'),
    path('dashboard/', views.dashboard, name='dashboard'),
<<<<<<< HEAD
    path('news/',views.news, name='news')
=======
    path('signup', views.signup, name='signup'),
    path('playground', views.playground, name='playground'),
    path('dashboard', views.dashboard, name='dashboard'),
>>>>>>> Stashed changes
=======
    path('news/',views.news, name='news'),
    path('risk',views.risk, name='risk'),
    path('register/',views.register, name='register')
>>>>>>> master
] 
