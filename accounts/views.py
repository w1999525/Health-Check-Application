from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from datetime import datetime
import json

from .models import Department, Team, Session, HealthCard, Votes, Profile, Project


@login_required
def summary_view(request):
    """
    View for visualizing votes and trends based on selected filters.
    Permissions and data access are restricted based on user role.
    """
    user_profile = request.user.profile
    role = user_profile.role

    all_departments = Department.objects.all()
    user_department_id = None

    # Set permissions and initial querysets based on user role
    if role == "Department Leader":
        user_department_id = user_profile.department.id
        selected_department = request.POST.get('department', str(user_department_id))
        departments = all_departments
        if selected_department and str(selected_department) != str(user_department_id):
            teams = Team.objects.filter(department_id=selected_department)
            sessions = Session.objects.filter(team__department_id=selected_department)
            teams_locked = True
            sessions_locked = True
        else:
            teams = Team.objects.filter(department_id=user_department_id)
            sessions = Session.objects.filter(team__department_id=user_department_id)
            teams_locked = False
            sessions_locked = False
        can_view_other_departments = True
    elif role == "Team Leader":
        user_department_id = user_profile.department.id
        departments = Department.objects.filter(id=user_department_id)
        teams = Team.objects.filter(department_id=user_department_id)
        sessions = Session.objects.filter(team__in=teams)
        all_departments = departments
        teams_locked = False
        sessions_locked = False
        can_view_other_departments = False
    elif role == "Senior Manager":
        departments = Department.objects.all()
        teams = Team.objects.all()
        sessions = Session.objects.all()
        all_departments = departments
        teams_locked = False
        sessions_locked = False
        can_view_other_departments = True
    else:  # Engineer or no role assigned yet
        return render(request, 'accounts/awaiting_team.html')

    # Get all health cards
    cards = HealthCard.objects.all()
    stats = []
    total_votes = 0
    selected = {}
    selected_project = None

    # Process form submission with filters
    if request.method == 'POST':
        selected_department = request.POST.get('department')
        selected_team = request.POST.get('team')
        selected_session = request.POST.get('session')
        selected_card = request.POST.get('card')
        time_period = request.POST.get('time_period')

        # Build query based on selected filters
        votes_qs = Votes.objects.all()
        if selected_department and selected_department != 'all':
            votes_qs = votes_qs.filter(session__team__department_id=selected_department)
        if selected_team and selected_team != 'all':
            votes_qs = votes_qs.filter(session__team_id=selected_team)
        if selected_session and selected_session != 'all':
            votes_qs = votes_qs.filter(session_id=selected_session)
            try:
                session_obj = Session.objects.get(id=selected_session)
                selected_project = session_obj.project
            except Session.DoesNotExist:
                selected_project = None
        if selected_card and selected_card != 'all':
            votes_qs = votes_qs.filter(card_id=selected_card)
        if time_period and '-' in time_period:
            try:
                date_from, date_to = [datetime.strptime(x.strip(), '%d/%m/%Y').date() for x in time_period.split('-')]
                votes_qs = votes_qs.filter(timestamp__date__gte=date_from, timestamp__date__lte=date_to)
            except Exception as e:
                print(f"Date parsing error: {e}")
                # Continue without date filtering if format is incorrect

        # Get vote statistics
        stats = list(votes_qs.values('vote').annotate(count=Count('id')).order_by('vote'))
        total_votes = votes_qs.count()

        # Process trend statistics
        base_trends = ['improving', 'steady', 'worsening']
        trend_stats_qs = votes_qs.values('trend').annotate(count=Count('id')).order_by('trend')
        trend_counts = {trend: 0 for trend in base_trends}
        
        for t in trend_stats_qs:
            trend = t['trend']
            if trend in trend_counts:
                trend_counts[trend] = t['count']
                
        # Format trend stats for template
        trend_stats = [{'trend': k, 'count': trend_counts[k]} for k in base_trends]

        # Determine majority trend
        max_count = max(trend_counts.values()) if trend_counts.values() else 0
        max_trends = [k for k, v in trend_counts.items() if v == max_count and max_count > 0]
        
        # Prefer 'steady' if tied
        if 'steady' in max_trends:
            final_trend = 'steady'
        elif max_trends:
            final_trend = max_trends[0]
        else:
            final_trend = 'steady'  # Default if no data

        # Store selected filters for template
        selected = {
            'department': selected_department,
            'team': selected_team,
            'session': selected_session,
            'card': selected_card,
            'time_period': time_period
        }
    else:
        # Default values for initial page load
        trend_stats = [{'trend': 'improving', 'count': 0}, {'trend': 'steady', 'count': 0}, {'trend': 'worsening', 'count': 0}]
        final_trend = 'steady'
        
        # Set initial selection based on user role
        if role == "Department Leader":
            selected = {'department': str(user_department_id), 'team': 'all', 'session': 'all', 'card': 'all', 'time_period': ''}
        else:
            selected = {'department': 'all', 'team': 'all', 'session': 'all', 'card': 'all', 'time_period': ''}

    # Prepare JSON data for charts
    stats_json = json.dumps(stats)
    trend_stats_json = json.dumps(trend_stats)

    # Context dictionary for template
    context = {
        'departments': departments,
        'all_departments': all_departments,
        'teams': teams,
        'sessions': sessions,
        'cards': cards,
        'selected': selected,
        'stats': stats,
        'total_votes': total_votes,
        'stats_json': stats_json,
        'trend_stats': trend_stats,
        'trend_stats_json': trend_stats_json,
        'final_trend': final_trend,
        'selected_project': selected_project,
        'can_view_other_departments': can_view_other_departments,
        'role': role,
        'user_department_id': user_department_id,
        'teams_locked': teams_locked if role == "Department Leader" else False,
        'sessions_locked': sessions_locked if role == "Department Leader" else False,
    }

    return render(request, 'accounts/summary.html', context)


@login_required
def summary_guide(request):
    """Simple view to render the summary guide page."""
    return render(request, 'accounts/summary_guide.html')


@login_required
def ajax_get_teams(request):
    """AJAX view to dynamically update team dropdown based on selected department."""
    dept_id = request.GET.get('department_id')
    teams = []
    
    if dept_id and dept_id != 'all':
        teams = list(Team.objects.filter(department_id=dept_id).values('id', 'name', 'department__name'))
    else:
        teams = list(Team.objects.all().values('id', 'name', 'department__name'))
        
    return JsonResponse({'teams': teams})


@login_required
def ajax_get_sessions(request):
    """AJAX view to dynamically update session dropdown based on selected team/department."""
    team_id = request.GET.get('team_id')
    dept_id = request.GET.get('department_id')
    
    qs = Session.objects.all()
    
    if dept_id and dept_id != 'all':
        qs = qs.filter(team__department_id=dept_id)
    if team_id and team_id != 'all':
        qs = qs.filter(team_id=team_id)
        
    sessions = list(qs.values('id', 'name', 'team__name'))
    return JsonResponse({'sessions': sessions})


@login_required
def ajax_get_project(request):
    """AJAX view to get project information for a selected session."""
    session_id = request.GET.get('session_id')
    project = None
    
    if session_id and session_id != 'all':
        try:
            session = Session.objects.get(id=session_id)
            if session.project:
                project = {'id': session.project.id, 'name': session.project.name}
        except Session.DoesNotExist:
            project = None
            
    return JsonResponse({'project': project})