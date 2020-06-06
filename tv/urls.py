from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='tv-home'),
    path('about/', views.about, name='tv-about'),
    path('show/', views.show, name='tv-show'),
    path('show/<int:showid>/', views.show, name='tv-show'),
    path('list/', views.showlist, name='tv-showlist'),
    path('list/<str:username>/', views.showlist, name='tv-showlist'),
    path('search/', views.search, name='tv-search'),
    path('search/<str:query>/', views.search, name='tv-search')
]
