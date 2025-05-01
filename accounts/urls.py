from django.urls import path
from . import views

urlpatterns = [
    # Other account URLs would be here
    path('summary/', views.summary_view, name='summary_view'),
    path('summary/guide/', views.summary_guide, name='summary_guide'),
    path('ajax/get-teams/', views.ajax_get_teams, name='ajax_get_teams'),
    path('ajax/get-sessions/', views.ajax_get_sessions, name='ajax_get_sessions'),
    path('ajax/get-project/', views.ajax_get_project, name='ajax_get_project'),
]