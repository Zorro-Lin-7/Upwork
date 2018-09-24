from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


from .views import (
        UserDetailView, UpdateProfileView,
        FreelancerSignUpView, OwnerSignUpView,
        ListFreelancersView,
        SignUpView,
        )

app_name = 'users'

urlpatterns = [
        path('accounts/', include(([
            path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
            path('logout/', auth_views.LogoutView.as_view(), name='logout'),
            path('signup/', SignUpView.as_view(), name='signup'),
            path('signup/freelancer/', FreelancerSignUpView.as_view(), name='freelancer_signup'),
            path('signup/project-owner/', OwnerSignUpView.as_view(), name='owner_signup'),
        ]))),
        path('freelancers/', include(([
            path('', ListFreelancersView.as_view(), name='list_freelancer'),
        ]))),
        path('user/', include(([
            path('<str:pk>/edit', UpdateProfileView.as_view(), name="update_profile"),
            path('<str:username>/', UserDetailView.as_view(), name='user_profile'),
        ]))),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
