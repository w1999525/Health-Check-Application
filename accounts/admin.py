from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile, Department, Team, Session, HealthCard, Votes, Project


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_team', 'get_department', 'is_staff')
    list_filter = ('profile__role', 'profile__team', 'profile__department', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__team__name', 'profile__department__name')
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'
    
    def get_team(self, obj):
        return obj.profile.team.name if hasattr(obj, 'profile') and obj.profile.team else '-'
    get_team.short_description = 'Team'
    get_team.admin_order_field = 'profile__team__name'
    
    def get_department(self, obj):
        return obj.profile.department.name if hasattr(obj, 'profile') and obj.profile.department else '-'
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'profile__department__name'


# Unregister the default User admin and register our custom version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', 'description')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'team', 'date', 'project')
    list_filter = ('team', 'team__department', 'date')
    search_fields = ('name', 'team__name', 'project__name')
    date_hierarchy = 'date'
    

@admin.register(HealthCard)
class HealthCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title', 'description')


@admin.register(Votes)
class VotesAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'card', 'vote', 'trend', 'timestamp')
    list_filter = ('vote', 'trend', 'session', 'card', 'timestamp')
    search_fields = ('user__username', 'session__name', 'card__title')
    date_hierarchy = 'timestamp'