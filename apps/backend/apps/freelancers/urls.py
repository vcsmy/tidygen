"""
URL configuration for freelancers app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'freelancers'

urlpatterns = [
    # Freelancer management
    path('', views.FreelancerListCreateView.as_view(), name='freelancer-list-create'),
    path('<int:pk>/', views.FreelancerDetailView.as_view(), name='freelancer-detail'),
    path('me/', views.FreelancerDetailView.as_view(), {'pk': 'me'}, name='freelancer-me'),
    path('search/', views.search_freelancers, name='freelancer-search'),
    
    # Freelancer availability
    path('<int:freelancer_id>/availability/', 
         views.FreelancerAvailabilityView.as_view(), 
         name='freelancer-availability'),
    path('<int:freelancer_id>/availability/<int:pk>/', 
         views.FreelancerAvailabilityUpdateView.as_view(), 
         name='freelancer-availability-detail'),
    
    # Freelancer documents
    path('<int:freelancer_id>/documents/', 
         views.FreelancerDocumentView.as_view(), 
         name='freelancer-documents'),
    path('<int:freelancer_id>/documents/<int:pk>/', 
         views.FreelancerDocumentDetailView.as_view(), 
         name='freelancer-document-detail'),
    path('<int:freelancer_id>/documents/<int:document_id>/verify/', 
         views.verify_document, 
         name='freelancer-document-verify'),
    
    # Freelancer skills
    path('<int:freelancer_id>/skills/', 
         views.FreelancerSkillsView.as_view(), 
         name='freelancer-skills'),
    path('<int:freelancer_id>/skills/<int:pk>/', 
         views.FreelancerSkillDetailView.as_view(), 
         name='freelancer-skill-detail'),
    path('skills/', views.FreelancerSkillsView.as_view(), name='skill-list'),
    
    # Freelancer reviews
    path('<int:freelancer_id>/reviews/', 
         views.FreelancerReviewsView.as_view(), 
         name='freelancer-reviews'),
    
    # Freelancer statistics
    path('<int:freelancer_id>/stats/', 
         views.freelancer_stats, 
         name='freelancer-stats'),
]
