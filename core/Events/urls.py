from django.urls import path
from Events import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('me', views.render_account, name='me'),
    path('id/<str:id>', views.userpage, name='userprofile'),
    path('user/<str:id>/edit/', views.user_edit, name='user_edit'),
    path('user/<str:id>/edit/password/',
         views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('eventcreate', views.create_event, name='eventcreate'),
    path('event/<str:id>', views.eventpage, name='eventpage'),
    path('event/<str:id>/edit/', views.event_edit, name='event_edit'),
    path('reg_unreg', views.reg_control, name='reg_unreg_on_event'),
    path('rate_user', views.rate_action, name='rate_user'),
]
