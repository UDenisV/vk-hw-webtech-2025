from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Question, Answer, Tag, Vote, AnswerVote
import random
from django.db import models

class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Multiplier for the number of entities')

    def handle(self, *args, **options):
        ratio = options['ratio']
        User = get_user_model()

        users = []
        for i in range(ratio):
            username = f'user{i}'
            email = f'user{i}@test.com'
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password('pass')
                user.save()
            users.append(user)

        tags = []
        for i in range(ratio):
            tag_title = f'tag{i}'
            tag, _ = Tag.objects.get_or_create(title=tag_title)
            tags.append(tag)

        questions = []
        for i in range(ratio * 10):
            title = f'Question {i}'
            detailed = f'Detailed text {i}'
            author = random.choice(users)
            question, _ = Question.objects.get_or_create(
                title=title,
                defaults={'detailed': detailed, 'author': author}
            )
            tag = random.choice(tags)
            if tag not in question.tags.all():
                question.tags.add(tag)
            questions.append(question)

        answers = []
        for i in range(ratio * 100):
            question = random.choice(questions)
            author = random.choice(users)
            answer_text = f'Answer text {i}'
            answer, _ = Answer.objects.get_or_create(
                question=question,
                author=author,
                answer_text=answer_text
            )
            answers.append(answer)

        existing_votes = set((v.user_id, v.question_id) for v in Vote.objects.all())
        for _ in range(ratio * 200):
            user = random.choice(users)
            question = random.choice(questions)
            key = (user.id, question.id)
            if key in existing_votes:
                continue
            existing_votes.add(key)
            Vote.objects.create(
                user=user,
                question=question,
                value=random.choice([1, -1])
            )

        existing_answer_votes = set((v.user_id, v.answer_id) for v in AnswerVote.objects.all())
        for _ in range(ratio * 200):
            user = random.choice(users)
            answer = random.choice(answers)
            key = (user.id, answer.id)
            if key in existing_answer_votes:
                continue
            existing_answer_votes.add(key)
            AnswerVote.objects.create(
                user=user,
                answer=answer,
                value=random.choice([1, -1])
            )

        for question in questions:
            total = Vote.objects.filter(question=question).aggregate(total=models.Sum('value'))['total'] or 0
            question.rating = total
            question.save()

        for answer in answers:
            total = AnswerVote.objects.filter(answer=answer).aggregate(total=models.Sum('value'))['total'] or 0
            answer.rating = total
            answer.save()

        self.stdout.write(self.style.SUCCESS('БД успешно заполнена!'))
