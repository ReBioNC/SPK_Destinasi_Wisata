from django.urls import path

from recommender import views

urlpatterns = [
    path("", views.rekomendasi, name="beranda"),
]
