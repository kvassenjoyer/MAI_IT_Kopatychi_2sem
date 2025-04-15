# users/forms.py
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Event, Interests
from qrcode import QRCode
import os


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'last_name', 'username', 'first_name', 'password1', 'middle_name', 'password2', 'image')
        labels = {
            'image': 'Фото профиля',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    def generate_and_set_qr_code(self, user):
        qr = QRCode()
        # СЮДА НУЖНО ВСТАВИТЬ АДРЕССС СЕРВЕРА В СЕТИ ДЛЯ ТОГО ЧТОБЫ КОД ПРАВИЛЬНО РИСОВАЛСЯ
        cur_machine_ip = "хост"
        qr.add_data(f"http://{cur_machine_ip}/users/id/{user.id}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        folder_path = "Events/static/user_qr_images/"
        os.makedirs(folder_path, exist_ok=True)
        img.save(folder_path + f"qr_code_{user.id}.png")
        user.image_qrid = f"core/Events/static/user_qr_images/qr_code_{user.id}.png"
        print(user.image_qrid)
        user.save()


class CustomUserChangeForm(UserChangeForm):
    interests = forms.ModelMultipleChoiceField(queryset=Interests.objects.all(
    ), widget=forms.widgets.CheckboxSelectMultiple, label="Интересы:")
    interest_powers = forms.CharField(label="Приоритет для каждого интереса",
                                      help_text="Введите приоритет от 1 до 10 для каждого интереса через запятую")

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'last_name',
                  'first_name', 'middle_name', 'image')
        labels = {'last_name': "Фамилия",
                  'first_name': 'Имя',
                  'middle_name': "Отчество",
                  'email': 'Почта',
                  'username': 'Логин',
                  'image': 'Загрузите новое фото',
                  }
        help_texts = {
            'username': '(Не более 30 символов. Только буквы, цифры и символы @ . + - _)',
        }

    def clean_interest_powers(self):

        data = self.cleaned_data['interest_powers']
        powers = [int(power) for power in data.split(',')]
        if len(powers) != len(self.cleaned_data['interests']):
            raise forms.ValidationError(
                "Количество введенных данных не соответствует количеству интересов")
        return powers


class EventCreationForm(ModelForm):
    interests = forms.ModelMultipleChoiceField(queryset=Interests.objects.all(
    ), widget=forms.CheckboxSelectMultiple, label="Интересы:")
    interest_powers = forms.CharField(label="Приоритет для каждого интереса",
                                      help_text="Введите приоритет от 1 до 10 для каждого интереса через запятую")

    class Meta:
        model = Event
        fields = ('name', 'location', 'date', 'max_members', 'image',
                  'description', 'interests', 'interest_powers')
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 6}),
        }
        labels = {
            'image': 'Фото',
            'name': 'Название',
            'location': 'Место проведения',
            'date': 'Дата',
            'max_members': "Лимит участников",
            'description': "Описание",
            'interests': "Интересы:"
        }
        help_texts = {
            'date': '(Формат: гггг-мм-дд чч:мм)'
        }

    def clean_interest_powers(self):
        data = self.cleaned_data['interest_powers']
        powers = [int(power) for power in data.split(',')]
        if len(powers) != len(self.cleaned_data['interests']):
            raise forms.ValidationError(
                "Количество введенных данных не соответствует количеству интересов")
        return powers
