from django.urls import path, re_path
from django.views.generic.detail import DetailView

from core.views import IndexView

urlpatterns = [
    path('', IndexView.as_view()),
    path('/questions/<int:id>', DetailView.as_view()),
]