from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleLoginForm(forms.Form):
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


class AccountRegisterForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=User.Role.choices, 
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    identifier = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan NPM atau ID asisten'}),
    )
    # Nama field disesuaikan dengan {{ form.password1 }} & {{ form.password2 }} di register.html
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan password'}),
    )
    password2 = forms.CharField(
        label='Ulangi Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Ulangi password'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'kelas')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cara 2: Iterasi semua field dan suntikkan class 'form-input' otomatis
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-input'.strip()
            
            # Opsional: Beri placeholder otomatis jika belum ada
            if 'placeholder' not in field.widget.attrs and field.label:
                field.widget.attrs['placeholder'] = f'Masukkan {field.label.lower()}'

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier', '').strip()
        role = self.cleaned_data.get('role', '')

        if role == User.Role.PRAKTIKAN and User.objects.filter(npm=identifier).exists():
            raise forms.ValidationError('NPM ini sudah terdaftar.')

        if role == User.Role.ASISTEN and User.objects.filter(assistant_id=identifier).exists():
            raise forms.ValidationError('ID asisten ini sudah terdaftar.')

        return identifier

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        
        # 1. Validasi Kelas + Normalisasi UPPERCASE
        kelas = (cleaned_data.get('kelas') or '').strip().upper()
        if role == User.Role.PRAKTIKAN and not kelas:
            self.add_error('kelas', 'Kelas wajib diisi untuk akun praktikan.')
        
        cleaned_data['kelas'] = kelas

        # 2. Validasi Kesamaan Password
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Kedua password tidak cocok.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        identifier = self.cleaned_data['identifier']
        role = self.cleaned_data['role']
        kelas = self.cleaned_data['kelas']

        user.role = role
        user.npm = identifier if role == User.Role.PRAKTIKAN else None
        user.assistant_id = identifier if role == User.Role.ASISTEN else None
        user.kelas = kelas if role == User.Role.PRAKTIKAN else ''

        # Hash password menggunakan nilai dari password1
        user.set_password(self.cleaned_data['password1'])

        # Generate unique username
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