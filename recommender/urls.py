from django.urls import path

from recommender import views

urlpatterns = [
    path("", views.rekomendasi, name="beranda"),
    path("peta/", views.peta, name="peta"),
    path("tentang/", views.tentang, name="tentang"),
]
