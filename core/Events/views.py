from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Event, CustomUser, Members_event, User_interest, Interests, Event_interests
from .forms import CustomUserCreationForm, EventCreationForm, CustomUserChangeForm
from django.utils import timezone
from qrcode import QRCode
import os

from .recommendations import similar_events, similar_users_events, hybrid


def render_home(request):
    if request.user.is_authenticated:
        future_events = Event.objects.exclude(
            organizer=request.user).filter(date__gte=timezone.now())
        future_events = future_events.order_by("date")
        data = Members_event.objects.filter(member=request.user)
        users_events = [i.event.name for i in data]
        sorted_events = hybrid(future_events, request.user, len(future_events))
        users = CustomUser.objects.order_by("-rating")
        return render(request, 'home.html', context={"events": sorted_events, "users_events": users_events, "users": users})
    else:
        future_events = Event.objects.filter(date__gte=timezone.now())
        future_events = future_events.order_by("date")
        users = CustomUser.objects.order_by("-rating")
        return render(request, 'home.html', context={"events": future_events, "users": users})


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        self.object = form.save()
        form.generate_and_set_qr_code(self.object)
        return super().form_valid(form)


class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('me')
    template_name = 'registration/password_change.html'


def render_account(request):
    if request.user.is_authenticated:
        is_interests_specified = len(
            User_interest.objects.filter(user=request.user))
        my_events = Event.objects.filter(
            organizer=request.user).order_by("date")
        member_events = Members_event.objects.filter(member=request.user)
        member_events = [Event.objects.filter(
            name=i.event)[:1].get() for i in member_events]
        member_events.sort(key=lambda x: x.date)
        future_events = [
            event for event in member_events if event.date > timezone.now()]
        past_events = [
            event for event in member_events if event.date < timezone.now()]
        generate_and_set_qr_code(request.user)
        args = {"user": request.user, "is_interests_specified": is_interests_specified,
                "my_events": my_events, "future_events": future_events, "past_events": past_events}
        return render(request, 'account.html', context=args)
    else:
        return redirect('login')


def create_event(request):
    if request.user.is_authenticated:
        form = EventCreationForm(request.POST, request.FILES)
        if request.method == 'POST' and form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            powers = form.cleaned_data['interest_powers']
            interests = form.cleaned_data['interests']
            for i in range(len(interests)):
                event_interest = Event_interests(
                    event=event, interest=interests[i], power=powers[i])
                event_interest.save()
            return redirect('me')
        else:
            interest_amount = len(Interests.objects.all())
            DEFAULT_INTEREST_VALUE = 0
            interest_powers = [
                DEFAULT_INTEREST_VALUE for _ in range(interest_amount)]

            interest_names = [i['interest']
                              for i in Interests.objects.values()]

            interest_dict = dict(zip(interest_names, interest_powers))
            args = {'form': form, 'interest_dict': interest_dict,
                    'tickmarks_range': range(11)}
            return render(request, 'event_create.html', context=args)
    else:
        return redirect('login')


def eventpage(request, id):
    data = Event.objects.filter(id=id).first()
    data.image = str(data.image).split('/')[-1]
    now = timezone.now()
    members = data.member.all()
    return render(request, 'eventpage.html', {"event": data, "now": now, "members": members})


def userpage(request, id):
    user = CustomUser.objects.filter(id=id).first()
    if user == request.user:
        return redirect('me')

    my_events = Event.objects.filter(organizer=user).order_by("date")
    member_events = Members_event.objects.filter(member=user)
    member_events = [Event.objects.filter(
        name=i.event)[:1].get() for i in member_events]
    member_events.sort(key=lambda x: x.date)
    future_events = [
        event for event in member_events if event.date > timezone.now()]
    past_events = [
        event for event in member_events if event.date < timezone.now()]
    generate_and_set_qr_code(user)
    args = {"user": request.user,"profile_user": user, "my_events": my_events, "past_events": past_events}
    return render(request, "user_profile.html", context=args)


def generate_and_set_qr_code(user):
    folder_path = "Events/static/user_qr_images/"
    os.makedirs(folder_path, exist_ok=True)
    file_path = folder_path + f"qr_code_{user.id}.png"
    if os.path.isfile(file_path):
        return HttpResponse(status=204)
    qr = QRCode()
    # СЮДА НУЖНО ВСТАВИТЬ АДРЕССС СЕРВЕРА В СЕТИ ДЛЯ ТОГО ЧТОБЫ КОД ПРАВИЛЬНО РИСОВАЛСЯ
    cur_machine_ip = "127.0.0.1:8000"
    qr.add_data(f"http://{cur_machine_ip}/users/id/{user.id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(folder_path + f"qr_code_{user.id}.png")
    user.image_qrid = f"core/Events/static/user_qr_images/qr_code_{user.id}.png"
    print(user.image_qrid)
    user.save()
    return HttpResponse(status=204)


def event_edit(request, id):
    event = Event.objects.get(id=id)

    if request.user == event.organizer:
        if request.method == 'POST':
            form = EventCreationForm(
                request.POST, request.FILES, instance=event)
            if form.is_valid():
                event_interests = Event_interests.objects.filter(event=event)
                event_interests.delete()
                form.save()
                powers = form.cleaned_data['interest_powers']
                interests = form.cleaned_data['interests']
                for i in range(len(interests)):
                    event_interest = Event_interests(
                        event=event, interest=interests[i], power=powers[i])
                    event_interest.save()
                return redirect('eventpage', id=id)
        else:
            form = EventCreationForm(instance=event)

        interest_amount = len(Interests.objects.all())
        DEFAULT_INTEREST_VALUE = 0
        interest_powers = [
            DEFAULT_INTEREST_VALUE for _ in range(interest_amount)]

        event_interests = Event_interests.objects.filter(event=event).values()
        temp_dict = {i['interest_id']: i['power'] for i in event_interests}
        for id, power in temp_dict.items():
            interest_powers[id-1] = power

        interest_names = [i['interest'] for i in Interests.objects.values()]

        interest_dict = dict(zip(interest_names, interest_powers))

        return render(request, 'event_edit.html', {'form': form, 'interest_dict': interest_dict, 'tickmarks_range': range(11)})
    else:
        return redirect('login')


def user_edit(request, id):
    user = CustomUser.objects.get(id=id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CustomUserChangeForm(
                request.POST, request.FILES, instance=user)
            if form.is_valid():
                user_interests = User_interest.objects.filter(user=user)
                user_interests.delete()
                form.save()
                powers = form.cleaned_data['interest_powers']
                interests = form.cleaned_data['interests']
                for i in range(len(interests)):
                    user_interest = User_interest(
                        user=user, interest=interests[i], power=powers[i])
                    user_interest.save()
                return redirect('userprofile', id=id)
        else:
            form = CustomUserChangeForm(instance=user)

        interest_amount = len(Interests.objects.all())
        DEFAULT_INTEREST_VALUE = 0
        interest_powers = [
            DEFAULT_INTEREST_VALUE for _ in range(interest_amount)]

        user_interests = User_interest.objects.filter(user=user).values()
        temp_dict = {i['interest_id']: i['power'] for i in user_interests}
        for id, power in temp_dict.items():
            interest_powers[id-1] = power

        interest_names = [i['interest'] for i in Interests.objects.values()]

        interest_dict = dict(zip(interest_names, interest_powers))

        return render(request, 'user_edit.html', {'form': form, 'interest_dict': interest_dict, 'tickmarks_range': range(11)})
    else:
        return redirect('login')


def reg_control(request):
    if request.method == 'POST' and request.user.is_authenticated:
        action = request.POST.get('action')
        event_id = request.POST.get('event_id')
        user = request.user
        event = Event.objects.get(id=event_id)
        if action == 'register':
            try:
                event.add_member(user)
            except ValueError:
                # Ошибка мест нет
                return redirect(f"event/{event_id}")
            except TypeError:
                # Ошибка чел уже зареган
                return redirect(f"event/{event_id}")
            return redirect('home')  # успешно загеган
        elif action == 'unregister':
            try:
                event.remove_member(user)
            except TypeError:
                # Ошибка чела нет среди зареганых
                return redirect(f"event/{event_id}")
            return redirect('home')  # успешно загеган
    else:
        return redirect('login')


def rate_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        username = request.POST.get('user')
        user = CustomUser.objects.get(username=username)
        event_id = request.POST.get('event_id')

        if action == 'praise':
            user.rating += 5
            user.save()

            return redirect(f"event/{event_id}")
        elif action == 'scold':
            if user.rating > 0:
                user.rating -= 5
                user.save()
                return redirect(f"event/{event_id}")

    return redirect(f"event/{event_id}")
