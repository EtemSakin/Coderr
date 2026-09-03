from django.urls import path

from auth_app.api.views import (
    BusinessProfileListView,
    CustomerProfileListView,
    LoginView,
    ProfileView,
    RegistrationView,
)


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path(
        'profiles/business/',
        BusinessProfileListView.as_view(),
        name='business-profiles',
    ),
    path(
        'profiles/customer/',
        CustomerProfileListView.as_view(),
        name='customer-profiles',
    ),
]
