import math

from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from core.models import Question, Tag, Answer, Vote, AnswerVote
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.urls import reverse


# Контроллеры приложения (обработчики запросов).

def index(request):
    print(request)
    return render(request, 'core/index.html')

class IndexView(TemplateView):
    http_method_names = ['get', 'post']
    template_name = 'core/index.html'
    QUESTIONS_PER_PAGE = 20

    def get_questions(self, tag=None, sort='date'):
        if tag:
            questions = Question.objects.filter(tags__title__in=[tag])
        else:
            questions = Question.objects.all()

        if sort == 'rating':
            return questions.order_by('-rating')
        return questions.order_by('-created_at')

    def get_tags(self):
        return Tag.objects.all()

    def post(self, request, *args, **kwargs):
        question_id = request.POST.get("question_id")
        vote_value = request.POST.get("vote")

        if question_id and vote_value and request.user.is_authenticated:
            question = get_object_or_404(Question, id=question_id)

            vote_val = 1 if vote_value == "up" else -1

            vote, created = Vote.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={"value": vote_val}
            )
            if not created:
                if vote.value != vote_val:
                    vote.value = vote_val
                    vote.save()

            total = Vote.objects.filter(question=question).aggregate(total=Sum('value'))['total'] or 0
            question.rating = total
            question.save()

        return redirect(request.path)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        tag = self.request.GET.get('tag', None)
        sort = self.request.GET.get('sort', 'date')
        context['page'] = page

        questions = self.get_questions(tag)
        context['sort'] = sort
        context['count_questions'] = questions.count()
        context['questions_per_page'] = self.QUESTIONS_PER_PAGE
        context['max_page'] = math.ceil(questions.count() / self.QUESTIONS_PER_PAGE)
        context['pages'] = [i for i in range(1, context['max_page'])]
        if page == 1:
            context['new_questions'] = questions[0:page * self.QUESTIONS_PER_PAGE]
        else:
            context['new_questions'] = questions[page * self.QUESTIONS_PER_PAGE:page * self.QUESTIONS_PER_PAGE + self.QUESTIONS_PER_PAGE]

        context['tags'] = Tag.objects.all()
        User = get_user_model()
        context['best_users'] = User.objects.order_by('-id')[:5]

        return context

    def dispatch(self, request, *args, **kwargs):
        print(request)
        return super(IndexView, self).dispatch(request, *args, **kwargs)




class QuestionDetailView(DetailView):
    model = Question
    template_name = "core/question_detail.html"
    context_object_name = "question"
    pk_url_kwarg = "id"
    ANSWERS_PER_PAGE = 30

    def post(self, request, *args, **kwargs):
        question = self.get_object()
        User = get_user_model()

        vote_value = request.POST.get("vote_question")
        if vote_value and request.user.is_authenticated:
            if vote_value == "up":
                val = 1
            else:
                val = -1
            vote, created = Vote.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={"value": val}
            )
            if not created:
                if vote.value != val:
                    vote.value = val
                    vote.save()

            question.rating = Vote.objects.filter(question=question).aggregate(total=Sum("value"))["total"] or 0
            question.save()
            return redirect(request.path)

        answer_id = request.POST.get("vote_answer")
        vote_val = request.POST.get("vote_value")
        if answer_id and vote_val and request.user.is_authenticated:
            answer = Answer.objects.get(id=answer_id)
            val = 1 if vote_val == "up" else -1
            vote, created = AnswerVote.objects.get_or_create(
                user=request.user,
                answer=answer,
                defaults={"value": val}
            )
            if not created:
                if vote.value != val:
                    vote.value = val
                    vote.save()
            answer.rating = AnswerVote.objects.filter(answer=answer).aggregate(total=Sum("value"))["total"] or 0
            answer.save()
            return redirect(request.path)

        if not request.user.is_authenticated:
            return redirect(request.path)
        answer_text = request.POST.get("answer_text", "").strip()
        if answer_text:
            answer = Answer.objects.create(
                question=question,
                author=request.user,
                answer_text=answer_text
            )

            if question.author.email:
                link = request.build_absolute_uri(reverse("question_detail", kwargs={"id": question.id}))
                send_mail(
                    subject=f"Новый ответ на ваш вопрос: {question.title}",
                    message=f"Появился новый ответ. Посмотреть: {link}",
                    from_email="no-reply@askpumpkin.com",
                    recipient_list=[question.author.email]
                )

        toggle_correct_id = request.POST.get("toggle_correct")
        if toggle_correct_id and request.user == question.author:
            answer = Answer.objects.get(id=toggle_correct_id, question=question)
            if answer.is_correct:
                answer.is_correct = False
            else:
                Answer.objects.filter(question=question, is_correct=True).update(is_correct=False)
                answer.is_correct = True
            answer.save()
            return redirect(request.path)

        return redirect(request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        answers = Answer.objects.filter(question=self.object).order_by("-rating", "-created_at")
        paginator = Paginator(answers, self.ANSWERS_PER_PAGE)
        page_number = self.request.GET.get("page", 1)
        context["answers_page"] = paginator.get_page(page_number)

        context["tags"] = Tag.objects.all()
        return context