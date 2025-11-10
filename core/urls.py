from django.urls import path
from django.views.generic import DetailView
from core.views import IndexView
from core.models import Question

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(
        'questions/<int:id>/',
        DetailView.as_view(
            model=Question,
            template_name='core/index.html',
            context_object_name='question',
            pk_url_kwarg='id'
        ),
        name='question_detail'
    ),
]