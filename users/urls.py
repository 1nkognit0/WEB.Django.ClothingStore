from django.contrib.auth.decorators import login_required
from django.urls import path

from users.views import (UserEmailVerification, UserLoginView, UserLogoutView,
                         UserProfileView, UserRegistrationView)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('profile/<int:pk>', login_required(UserProfileView.as_view()), name='profile'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('verify/<str:email>/<uuid:code>', UserEmailVerification.as_view(), name='email_verify'),
]
