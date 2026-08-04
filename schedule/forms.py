from django import forms

from .models import Schedule


class ScheduleForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Schedule
        fields = ['title', 'room', 'target_class', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: Praktikum Basis Data'}),
            'room': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: Lab A'}),
            'target_class': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: 2IA06'}),
        }