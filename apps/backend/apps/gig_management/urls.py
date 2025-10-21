"""
URL configuration for gig_management app.
"""
from django.urls import path
from . import views

app_name = 'gig_management'

urlpatterns = [
    # Categories
    path('categories/', views.GigCategoryListView.as_view(), name='category-list'),
    
    # Jobs
    path('jobs/', views.GigJobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', views.GigJobDetailView.as_view(), name='job-detail'),
    path('jobs/search/', views.search_jobs, name='job-search'),
    path('jobs/<int:job_id>/stats/', views.job_statistics, name='job-stats'),
    
    # Applications
    path('jobs/<int:job_id>/applications/', 
         views.GigApplicationView.as_view(), 
         name='job-applications'),
    path('jobs/<int:job_id>/applications/<int:pk>/', 
         views.GigApplicationDetailView.as_view(), 
         name='job-application-detail'),
    path('jobs/<int:job_id>/applications/<int:application_id>/assign/', 
         views.assign_freelancer, 
         name='assign-freelancer'),
    
    # Milestones
    path('jobs/<int:job_id>/milestones/', 
         views.JobMilestoneView.as_view(), 
         name='job-milestones'),
    path('jobs/<int:job_id>/milestones/<int:pk>/', 
         views.JobMilestoneDetailView.as_view(), 
         name='job-milestone-detail'),
    
    # Photos
    path('jobs/<int:job_id>/photos/', 
         views.JobPhotoView.as_view(), 
         name='job-photos'),
    
    # Messages
    path('jobs/<int:job_id>/messages/', 
         views.JobMessageView.as_view(), 
         name='job-messages'),
    
    # Reviews
    path('jobs/<int:job_id>/reviews/', 
         views.JobReviewView.as_view(), 
         name='job-reviews'),
]
