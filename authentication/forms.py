from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RoleLoginForm(forms.Form):
    # Mengambil choices langsung dari Model Enum (PRAKTIKAN & ASISTEN)
    role = forms.ChoiceField(
        choices=User.Role.choices, 
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    identifier = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan NPM atau ID asisten'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan password'}),
    )


class AccountRegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.Role.choices, 
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    identifier = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan NPM atau ID asisten'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'identifier', 'kelas', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        kelas = (cleaned_data.get('kelas') or '').strip()

        if role == User.Role.PRAKTIKAN and not kelas:
            self.add_error('kelas', 'Kelas wajib diisi untuk akun praktikan.')

        return cleaned_data

    def clean_identifier(self):
        # Aman dari KeyError dengan mengunakan .get()
        identifier = self.cleaned_data.get('identifier', '').strip()
        role = self.cleaned_data.get('role')

        if role == User.Role.PRAKTIKAN and User.objects.filter(npm=identifier).exists():
            raise forms.ValidationError('NPM ini sudah terdaftar.')

        if role == User.Role.ASISTEN and User.objects.filter(assistant_id=identifier).exists():
            raise forms.ValidationError('ID asisten ini sudah terdaftar.')

        return identifier

    def save(self, commit=True):
        user = super().save(commit=False)
        identifier = self.cleaned_data['identifier'].strip()
        role = self.cleaned_data['role']
        kelas = (self.cleaned_data.get('kelas') or '').strip()

        user.role = role
        user.npm = identifier if role == User.Role.PRAKTIKAN else None
        user.assistant_id = identifier if role == User.Role.ASISTEN else None
        user.kelas = kelas if role == User.Role.PRAKTIKAN else ''

        base_username = f'{role}_{identifier}'
        username = base_username
        suffix = 2
        while User.objects.filter(username=username).exclude(pk=user.pk).exists():
            username = f'{base_username}_{suffix}'
            suffix += 1

        user.username = username

        if commit:
            user.save()

        return user