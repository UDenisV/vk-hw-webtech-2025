from django.urls import path
from django.views.generic import DetailView
from core.views import IndexView, QuestionDetailView
from core.models import Question

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(
        'questions/<int:id>/',
        QuestionDetailView.as_view(),
        name='question_detail'
    ),
]