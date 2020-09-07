from django.urls import path, include
from . import views 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('homepage', views.homepage, name='homepage'),  
    path('signup/', views.signup, name='signup'),
    path('playground/', views.playground, name='playground'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('risk/',views.risk, name='risk'),
    path('register/',views.register, name='register'),
    path('performance/',views.performance, name='performance')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)