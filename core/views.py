import math
from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from core.models import Question, Tag, Answer, Vote, AnswerVote
from django.db import models
from django.db.models import Sum

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.get_page(page_number)
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)
    return page

def common_context():
    User = get_user_model()
    return {
        'tags': Tag.objects.all(),
        'best_users': User.objects.order_by('-id')[:5],
    }

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'core/login.html', {**common_context(), 'error': None, 'username': ''})

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'core/login.html', {**common_context(), 'error': 'Неверный логин или пароль', 'username': username})

class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'core/signup.html', {**common_context(), 'errors': {}, 'email': '', 'username': ''})

    def post(self, request):
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        avatar = request.FILES.get('avatar')

        errors = {}
        if not email:
            errors.setdefault('email', []).append('Email обязателен')
        if not username:
            errors.setdefault('username', []).append('Никнейм обязателен')
        if password != password2:
            errors.setdefault('password', []).append('Пароли не совпадают')

        if not errors:
            UserModel = get_user_model()
            user = UserModel.objects.create_user(username=username, email=email, password=password)
            if avatar:
                user.avatar = avatar
                user.save()
            return redirect('login')

        return render(request, 'core/signup.html', {**common_context(), 'errors': errors, 'email': email, 'username': username})

def logout_view(request):
    logout(request)
    return redirect('index')

class IndexView(TemplateView):
    template_name = 'core/index.html'
    http_method_names = ['get', 'post']
    QUESTIONS_PER_PAGE = 20

    def post(self, request, *args, **kwargs):

        question_id = request.POST.get("question_id")
        vote_value = request.POST.get("vote")
        if question_id and vote_value and request.user.is_authenticated:
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return redirect(request.path)

            vote_val = 1 if vote_value == "up" else -1

            vote, created = Vote.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={"value": vote_val}
            )
            if not created and vote.value != vote_val:
                vote.value = vote_val
                vote.save()

            total = Vote.objects.filter(question=question).aggregate(total=Sum('value'))['total'] or 0
            question.rating = total
            question.save()

        return redirect(request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort = self.request.GET.get('sort', 'date')
        tag_title = self.request.GET.get('tag')

        if tag_title:
            tag = get_object_or_404(Tag, title=tag_title)
            questions = Question.objects.filter(tags=tag)
        else:
            questions = Question.objects.all()

        if sort == 'rating':
            questions = questions.order_by('-rating')
        else:
            questions = questions.order_by('-created_at')

        page_obj = paginate(questions, self.request, self.QUESTIONS_PER_PAGE)
        context.update({
            'new_questions': page_obj,
            'pages': page_obj.paginator.page_range,
            'sort': sort,
            'tag': tag_title if tag_title else None,
            **common_context()
        })
        return context

class HotQuestionsView(TemplateView):
    template_name = 'core/index.html'
    QUESTIONS_PER_PAGE = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = Question.objects.order_by('-rating')
        page_obj = paginate(questions, self.request, self.QUESTIONS_PER_PAGE)
        context.update({
            'new_questions': page_obj,
            'pages': page_obj.paginator.page_range,
            'sort': 'rating',
            **common_context()
        })
        return context

class TagView(TemplateView):
    template_name = 'core/tag.html'
    QUESTIONS_PER_PAGE = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_title = self.kwargs.get('title')
        tag = get_object_or_404(Tag, title=tag_title)
        questions = Question.objects.filter(tags=tag).order_by('-created_at')
        page_obj = paginate(questions, self.request, self.QUESTIONS_PER_PAGE)
        context.update({
            'tag': tag,
            'questions': page_obj,
            'pages': page_obj.paginator.page_range,
            **common_context()
        })
        return context

    def post(self, request, *args, **kwargs):
        question_id = request.POST.get("question_id")
        vote_value = request.POST.get("vote")
        if question_id and vote_value and request.user.is_authenticated:
            question = Question.objects.get(id=question_id)
            vote_val = 1 if vote_value == "up" else -1
            vote, created = Vote.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={"value": vote_val}
            )
            if not created and vote.value != vote_val:
                vote.value = vote_val
                vote.save()
            question.rating = Vote.objects.filter(question=question).aggregate(total=models.Sum("value"))["total"] or 0
            question.save()
        return redirect(request.path)

class QuestionDetailView(DetailView):
    model = Question
    template_name = "core/question_detail.html"
    context_object_name = "question"
    pk_url_kwarg = "id"
    ANSWERS_PER_PAGE = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answers = self.object.answer_set.order_by('-rating', '-created_at')
        page_obj = paginate(answers, self.request, self.ANSWERS_PER_PAGE)
        context.update({
            'answers_page': page_obj,
            'pages': page_obj.paginator.page_range,
            **common_context()
        })
        return context

    def post(self, request, *args, **kwargs):
        question = self.get_object()

        vote_value = request.POST.get("vote_question")
        if vote_value and request.user.is_authenticated:
            val = 1 if vote_value == "up" else -1
            vote, created = Vote.objects.get_or_create(user=request.user, question=question, defaults={"value": val})
            if not created and vote.value != val:
                vote.value = val
                vote.save()
            question.rating = Vote.objects.filter(question=question).aggregate(total=models.Sum("value"))["total"] or 0
            question.save()
            return redirect(request.path)

        answer_id = request.POST.get("vote_answer")
        vote_val = request.POST.get("vote_value")
        if answer_id and vote_val and request.user.is_authenticated:
            answer = Answer.objects.get(id=answer_id)
            val = 1 if vote_val == "up" else -1
            vote, created = AnswerVote.objects.get_or_create(user=request.user, answer=answer, defaults={"value": val})
            if not created and vote.value != val:
                vote.value = val
                vote.save()
            answer.rating = AnswerVote.objects.filter(answer=answer).aggregate(total=models.Sum("value"))["total"] or 0
            answer.save()
            return redirect(request.path)

        correct_answer_id = request.POST.get("mark_correct")
        if correct_answer_id and request.user == question.author:
            Answer.objects.filter(question=question, is_correct=True).update(is_correct=False)
            correct_answer = Answer.objects.get(id=correct_answer_id)
            correct_answer.is_correct = True
            correct_answer.save()
            return redirect(request.path)

        answer_text = request.POST.get("answer_text", "").strip()
        if answer_text and request.user.is_authenticated:
            answer = Answer.objects.create(question=question, author=request.user, answer_text=answer_text)
        return redirect(request.path)

@method_decorator(login_required, name='dispatch')
class AskQuestionView(View):
    def get(self, request):
        context = {
            'title_input': '',
            'detailed_input': '',
            'tags_input': '',
            'form_errors_title': [],
            'form_errors_detailed': [],
            'form_errors_tags': [],
            **common_context()
        }
        return render(request, 'core/ask.html', context)

    def post(self, request):
        title = request.POST.get('title', '').strip()
        detailed = request.POST.get('detailed', '').strip()
        tags_input = request.POST.get('tags', '').strip()
        errors = {}

        if not title:
            errors['title'] = ["Заголовок обязателен"]
        elif len(title) > 200:
            errors['title'] = ["Заголовок слишком длинный"]
        if not detailed:
            errors['detailed'] = ["Текст вопроса обязателен"]

        tag_titles = [t.strip() for t in tags_input.split(',') if t.strip()]
        if len(tag_titles) > 3:
            errors['tags'] = ["Нельзя указать больше 3 тегов"]

        if errors:
            context = {
                'form_errors_title': errors.get('title'),
                'form_errors_detailed': errors.get('detailed'),
                'form_errors_tags': errors.get('tags'),
                'title_input': title,
                'detailed_input': detailed,
                'tags_input': tags_input,
                **common_context()
            }
            return render(request, 'core/ask.html', context)

        question = Question.objects.create(title=title, detailed=detailed, author=request.user)
        for tag_title in tag_titles[:3]:
            tag_obj, _ = Tag.objects.get_or_create(title=tag_title)
            question.tags.add(tag_obj)

        return redirect('question_detail', id=question.id)

@method_decorator(login_required, name='dispatch')
class UserSettingsView(View):
    def get(self, request):
        return render(request, 'core/settings.html', {**common_context(), 'user_obj': request.user, 'errors': {}})

    def post(self, request):
        user = request.user
        email = request.POST.get('email', '').strip()
        nick = request.POST.get('nick', '').strip()
        avatar = request.FILES.get('avatar')

        errors = {}
        if not email:
            errors['email'] = "Email обязателен"
        if not nick:
            errors['nick'] = "Nick обязателен"
        if errors:
            return render(request, 'core/settings.html', {**common_context(), 'user_obj': user, 'errors': errors})

        user.email = email
        user.username = nick
        if avatar:
            user.avatar = avatar
        user.save()
        return redirect('user_settings')
