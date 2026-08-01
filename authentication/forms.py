from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RoleLoginForm(forms.Form):
    ROLE_CHOICES = (
        ('praktikan', 'Praktikan'),
        ('asisten', 'Asisten'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    identifier = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan NPM atau ID asisten'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan password'}),
    )


class AccountRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('praktikan', 'Praktikan'),
        ('asisten', 'Asisten'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    identifier = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan NPM atau ID asisten'}),
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama depan'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama belakang'}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email aktif'}),
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'role', 'identifier', 'password1', 'password2')

    def clean_identifier(self):
        identifier = self.cleaned_data['identifier'].strip()
        role = self.cleaned_data.get('role')

        if role == 'praktikan' and CustomUser.objects.filter(npm=identifier).exists():
            raise forms.ValidationError('NPM ini sudah terdaftar.')

        if role == 'asisten' and CustomUser.objects.filter(assistant_id=identifier).exists():
            raise forms.ValidationError('ID asisten ini sudah terdaftar.')

        return identifier

    def save(self, commit=True):
        user = super().save(commit=False)
        identifier = self.cleaned_data['identifier']
        role = self.cleaned_data['role']

        user.role = role
        user.npm = identifier if role == 'praktikan' else None
        user.assistant_id = identifier if role == 'asisten' else None

        base_username = f'{role}_{identifier}'
        username = base_username
        suffix = 2
        while CustomUser.objects.filter(username=username).exclude(pk=user.pk).exists():
            username = f'{base_username}_{suffix}'
            suffix += 1

        user.username = username

        if commit:
            user.save()

        return user