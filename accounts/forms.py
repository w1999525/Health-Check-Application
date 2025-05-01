from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Profile, Department, Team


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Profile
        fields = ('role', 'department', 'team')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter teams based on selected department if department is set
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['team'].queryset = Team.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.department:
            self.fields['team'].queryset = Team.objects.filter(department=self.instance.department)


class SummaryFilterForm(forms.Form):
    """Form for filtering summary data"""
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        empty_label="All Teams",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    time_period = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 01/01/2024-31/12/2024',
            'readonly': True,
            'style': 'background:#f7fafc;cursor:pointer;'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter options based on user role
        if user and user.is_authenticated and hasattr(user, 'profile'):
            role = user.profile.role
            
            if role == 'Team Leader':
                # Team leaders can only see their department
                self.fields['department'].queryset = Department.objects.filter(id=user.profile.department.id)
                self.fields['department'].disabled = True
                self.fields['department'].empty_label = None
                
                # Team leaders can only see teams in their department
                self.fields['team'].queryset = Team.objects.filter(department=user.profile.department)
            
            elif role == 'Department Leader':
                # Department leaders see all departments but can only select teams from their department
                if 'department' in self.data:
                    try:
                        department_id = int(self.data.get('department'))
                        user_department_id = user.profile.department.id
                        
                        if department_id == user_department_id:
                            self.fields['team'].queryset = Team.objects.filter(department_id=department_id)
                        else:
                            self.fields['team'].disabled = True
                    except (ValueError, TypeError):
                        pass
                else:
                    self.fields['team'].queryset = Team.objects.filter(department=user.profile.department)