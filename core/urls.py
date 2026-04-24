from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
]
