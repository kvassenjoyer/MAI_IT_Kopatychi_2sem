# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Event, Status, Interests, Event_interests, Members_event, User_interest


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]


admin.site.register(CustomUser)
admin.site.register(Event)
admin.site.register(Status)
admin.site.register(Interests)
admin.site.register(Event_interests)
admin.site.register(Members_event)
admin.site.register(User_interest)
