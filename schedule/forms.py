from django import forms
from django.utils import timezone
from .models import Schedule


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title', 'room', 'target_class', 'start_time', 'end_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: Praktikum Basis Data'}),
            'room': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: Lab A'}),
            'target_class': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: 2IA06'}),
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-input'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-input'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Menegaskan format input agar widget datetime-local HTML5 merender nilai dengan benar saat edit
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        room = cleaned_data.get('room')

        if start_time and end_time:
            # 1. Validasi Waktu Selesai harus > Waktu Mulai
            if end_time <= start_time:
                self.add_error('end_time', 'Waktu selesai harus lebih lambat dari waktu mulai.')

            # 2. Validasi Waktu Mulai tidak boleh di masa lalu (hanya saat create jadwal baru)
            if not self.instance.pk and start_time < timezone.now():
                self.add_error('start_time', 'Waktu mulai tidak boleh berada di masa lalu.')

            # 3. Validasi Bentrok Ruangan & Waktu (Overlapping Check)
            if room:
                overlapping_schedules = Schedule.objects.filter(
                    room__iexact=room.strip(),
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                
                # Exclude jadwal yang sedang di-edit agar tidak memvalidasi dirinya sendiri
                if self.instance.pk:
                    overlapping_schedules = overlapping_schedules.exclude(pk=self.instance.pk)

                if overlapping_schedules.exists():
                    self.add_error('room', f'Ruangan "{room}" sudah digunakan pada rentang waktu tersebut.')

        return cleaned_data