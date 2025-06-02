
from django.urls import path
from .obrada_odgovora import evaluacija_view

urlpatterns = [
    path("evaluacija/", evaluacija_view, name="evaluacija"),
]
