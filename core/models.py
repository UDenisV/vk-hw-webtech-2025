from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.text import slugify
from PIL import Image


class DefaultModel(models.Model):
    class Meta:
        abstract = True

    is_active = models.BooleanField(default=True, verbose_name="Активен?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания", editable=False, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время изменения", editable=False, null=True)


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar:
            img_path = self.avatar.path
            img = Image.open(img_path)

            max_size = (50, 50)
            img.thumbnail(max_size, Image.LANCZOS)

            if img.format == 'JPEG' or img.format == 'JPG':
                img.save(img_path, format='JPEG', quality=85)
            else:
                img.save(img_path)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# Описание таблиц в БД.
class Question(DefaultModel):
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    title = models.CharField(max_length=200)
    detailed = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        return super(Question, self).save(*args, **kwargs)


class Answer(DefaultModel):
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    answer_text = models.TextField()
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        return f"Ответ на вопрос ID = {str(self.question_id)}"


class AnswerVote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_CHOICES = [(UPVOTE, "Upvote"), (DOWNVOTE, "Downvote")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ("user", "answer")


class Tag(models.Model):
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    title = models.CharField(max_length=200, verbose_name="Название тега")

    def __str__(self):
        return str(self.title)


class Vote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1

    VOTE_CHOICES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} -> {self.question.title}: {self.value}"