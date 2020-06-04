from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='tv-home'),
    path('show/', views.show, name='tv-show'),
    path('show/<int:showid>/', views.show, name='tv-show'),
    path('search/', views.search, name='tv-search'),
    path('search/<str:query>/', views.search, name='tv-search')
]
