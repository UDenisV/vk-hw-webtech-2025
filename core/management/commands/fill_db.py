from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Question, Answer, Tag, Vote, AnswerVote
import random

class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Multiplier for the number of entities')

    def handle(self, *args, **options):
        ratio = options['ratio']
        User = get_user_model()

        users = [User.objects.create_user(username=f'user{i}', email=f'user{i}@test.com', password='pass') for i in range(ratio)]
        tags = [Tag.objects.create(title=f'tag{i}') for i in range(ratio)]
        questions = []
        for i in range(ratio * 10):
            q = Question.objects.create(
                title=f'Question {i}',
                detailed=f'Detailed text {i}',
                author=random.choice(users)
            )
            q.tags.add(random.choice(tags))
            questions.append(q)
        answers = []
        for i in range(ratio * 100):
            a = Answer.objects.create(
                question=random.choice(questions),
                author=random.choice(users),
                answer_text=f'Answer text {i}'
            )
            answers.append(a)
        for i in range(ratio * 200):
            Vote.objects.create(
                user=random.choice(users),
                question=random.choice(questions),
                value=random.choice([1, -1])
            )
            AnswerVote.objects.create(
                user=random.choice(users),
                answer=random.choice(answers),
                value=random.choice([1, -1])
            )

        self.stdout.write(self.style.SUCCESS('Database filled successfully'))
