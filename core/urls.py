from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('shop/', views.ShopHomeView.as_view(), name='shop_home'),
    path('shop/<slug:slug>/', views.ShopCategoryView.as_view(), name='shop_category'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
