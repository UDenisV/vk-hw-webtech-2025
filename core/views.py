import math

from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from core.models import Question, Tag, Answer
from django.contrib.auth import get_user_model


# Контроллеры приложения (обработчики запросов).

def index(request):
    print(request)
    return render(request, 'core/index.html')

class IndexView(TemplateView):
    http_method_names = ['get',]
    template_name = 'core/index.html'
    QUESTIONS_PER_PAGE = 5

    def get_questions(self, tag=None):
        if tag is None:
            return Question.objects.all()

        return Question.objects.filter(tags__title__in=[tag])

    def get_tags(self):
        return Tag.objects.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        tag = self.request.GET.get('tag', None)
        context['page'] = page
        questions = self.get_questions(tag)
        context['count_questions'] = questions.count()
        context['questions_per_page'] = self.QUESTIONS_PER_PAGE
        context['max_page'] = math.ceil(questions.count() / self.QUESTIONS_PER_PAGE)
        context['pages'] = [i for i in range(1, context['max_page'])]
        if page == 1:
            context['new_questions'] = questions[0:page * self.QUESTIONS_PER_PAGE]
        else:
            context['new_questions'] = questions[page * self.QUESTIONS_PER_PAGE:page * self.QUESTIONS_PER_PAGE + self.QUESTIONS_PER_PAGE]

        context['tags'] = Tag.objects.all()

        return context

    def dispatch(self, request, *args, **kwargs):
        print(request)
        return super(IndexView, self).dispatch(request, *args, **kwargs)


class QuestionDetailView(DetailView):
    model = Question
    template_name = "core/question_detail.html"
    context_object_name = "question"
    pk_url_kwarg = "id"

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        question = self.get_object()
        answer_text = request.POST.get("answer_text", "").strip()
        guest_name = request.POST.get("guest_name", "").strip()

        if not answer_text:
            return redirect(request.path)

        if request.user.is_authenticated:
            author = request.user
        else:
            author, _ = User.objects.get_or_create(
                username="Anonymous",
                defaults={"password": "!"}
            )
            if guest_name:
                answer_text = f"{guest_name} (гость): {answer_text}"
            else:
                answer_text = f"Гость: {answer_text}"

        Answer.objects.create(
            question=question,
            author=author,
            answer_text=answer_text
        )

        return redirect(request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = Answer.objects.filter(question=self.object)
        context['tags'] = Tag.objects.all()
        return context