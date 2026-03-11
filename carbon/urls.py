from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("entries/", views.entry_list, name="entry-list"),
    path("entries/create/", views.entry_create, name="entry-create"),
    path("entries/<int:pk>/edit/", views.entry_update, name="entry-update"),
    path("entries/<int:pk>/delete/", views.entry_delete, name="entry-delete"),
    path("loyalty/connect/", views.loyalty_connect_view, name="loyalty-connect"),
    path("loyalty/disconnect/", views.loyalty_disconnect_view, name="loyalty-disconnect"),
    path("loyalty/dashboard/", views.loyalty_dashboard_view, name="loyalty-dashboard"),
]