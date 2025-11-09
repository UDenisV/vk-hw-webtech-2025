import typing as t
from django.core.management.base import BaseCommand, CommandError

from core.models import Question, User


FAKE__QUESTION_DETAILED = '''Это подробное описание вопроса. Оно может быть достаточно длинным и содержать много информации, чтобы помочь понять суть вопроса.'''

class Command(BaseCommand):
    help = 'Генерация сущностей по модели Вопроса'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100)

    def get_exist_user(self) -> t.Optional[User]:
        return User.objects.filter(is_superuser=True).first()

    def handle(self, *args, **options):
        count = options.get('count')
        count_exists_questions = Question.objects.all().count()
        questions_to_create = []
        for n in range(count):
            questions_to_create.append(Question(
                title=f'Вопрос №{count_exists_questions + n + 1}',
                detailed=FAKE__QUESTION_DETAILED,
                author=self.get_exist_user(),
            ))

        Question.objects.bulk_create(questions_to_create, batch_size=100)
        print("Было создано вопросов:", len(questions_to_create))