from django.urls import path

from users import views

urlpatterns = [
    path('login/', views.login_user, name="users.login"),
    path('logout/', views.logout_user, name="users.logout"),
]
