from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),

    # API endpoints
    path("api/requests/", views.requests_api, name="requests_api"),
    path("api/requests/create/", views.create_request_api, name="create_request_api"),
    path("api/requests/accept/<int:req_id>/", views.accept_request_api, name="accept_request_api"),
    path("api/requests/cancel/<int:req_id>/", views.cancel_request_api, name="cancel_request_api"),
]
