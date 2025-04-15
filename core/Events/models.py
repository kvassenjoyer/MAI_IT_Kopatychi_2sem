from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator

User = settings.AUTH_USER_MODEL


class Status(models.Model):
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.status


class Interests(models.Model):
    interest = models.CharField(max_length=30)

    def __str__(self):
        return self.interest


class CustomUser(AbstractUser):
    username = models.CharField(verbose_name="Логин", max_length=30, unique=True, 
                                validators=[UnicodeUsernameValidator()])
    last_name = models.CharField(verbose_name="Фамилия", max_length=30)
    first_name = models.CharField(verbose_name="Имя", max_length=30)
    middle_name = models.CharField(verbose_name="Отчества", max_length=30, blank=True)
    email = models.EmailField(verbose_name="Почта", max_length=30, unique=True, blank=True)
    image = models.ImageField(upload_to="Events/static/user_images")
    image_qrid = models.ImageField(upload_to="Events/static/user_qr_images")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    interest = models.ManyToManyField(Interests, through="User_interest")
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class User_interest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    interest = models.ForeignKey(Interests, on_delete=models.CASCADE)
    power = models.IntegerField(default=5)


class Event(models.Model):
    image = models.ImageField(upload_to="Events/static/event_images")
    name = models.CharField(max_length=40)
    location = models.CharField(max_length=40)
    organizer = models.ForeignKey(
        CustomUser, related_name='organizer', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    date = models.DateTimeField()
    max_members = models.PositiveIntegerField()
    interests = models.ManyToManyField(Interests, related_name='interests', through="Event_interests")
    member = models.ManyToManyField(CustomUser, related_name='members',through="Members_event")

    def __str__(self):
        return self.name

    def add_member(self, user):
        if self.member.count() >= self.max_members:
            raise ValueError
        if self.member.prefetch_related('member').filter(pk=user.pk).exists():
            raise TypeError
        Members_event.objects.create(member=user, event=self)

    def remove_member(self, user):
        try:
            member = Members_event.objects.get(member=user, event=self)
        except Members_event.DoesNotExist:
            raise TypeError
        member.delete()


class Members_event(models.Model):
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Event_interests(models.Model):
    interest = models.ForeignKey(Interests, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    power = models.IntegerField(default=5)
