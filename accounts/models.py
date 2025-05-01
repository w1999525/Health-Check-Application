from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    def __str__(self):
        return f"{self.name} ({self.team.name})"
    
    @property
    def team_department_id(self):
        return self.team.department.id


class HealthCard(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.title


class Profile(models.Model):
    ROLES = (
        ('Engineer', 'Engineer'),
        ('Team Leader', 'Team Leader'),
        ('Department Leader', 'Department Leader'),
        ('Senior Manager', 'Senior Manager'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='Engineer')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    @property
    def department_id(self):
        return self.department.id if self.department else None


class Votes(models.Model):
    VOTE_CHOICES = (
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
    )
    
    TREND_CHOICES = (
        ('improving', 'Improving'),
        ('steady', 'Steady'),
        ('worsening', 'Worsening'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    card = models.ForeignKey(HealthCard, on_delete=models.CASCADE)
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    trend = models.CharField(max_length=10, choices=TREND_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'session', 'card')
        verbose_name_plural = 'Votes'
    
    def __str__(self):
        return f"{self.user.username} - {self.session.name} - {self.card.title}: {self.vote}"
    
    @property
    def session_team_department_id(self):
        return self.session.team.department.id

# Signal functions moved to signals.py