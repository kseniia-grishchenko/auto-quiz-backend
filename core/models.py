import secrets

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q


def generate_invitation_token() -> str:
    return secrets.token_urlsafe(50)[:50]


class Subject(models.Model):
    name = models.CharField(max_length=255)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="subjects")
    invitation_token = models.CharField(
        max_length=50, default=generate_invitation_token, unique=True
    )

    def __str__(self) -> str:
        return self.name


class Quiz(models.Model):
    name = models.CharField(max_length=255)
    max_duration = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "quizzes"


class Question(models.Model):
    title = models.CharField(max_length=511)
    expected_answer = models.TextField()
    value = models.PositiveIntegerField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")

    def __str__(self) -> str:
        return self.title


class Course(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="courses")
    invitation_token = models.CharField(
        max_length=50, default=generate_invitation_token, unique=True
    )

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    deadline = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title


class TaskSession(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.task.title + " " + self.user.email

    class Meta:
        unique_together = ("user", "task")
        constraints = [
            CheckConstraint(
                check=Q(
                    Q(started_at__isnull=True)
                    | Q(finished_at__isnull=True)
                    | Q(started_at__lt=models.F("finished_at"))
                ),
                name="started_at_finished_at_check",
            ),
        ]


class UserAnswer(models.Model):
    STR_TEXT_LIMIT = 50

    text = models.TextField()
    correctness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    comment = models.TextField()
    is_adjusted = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    task_session = models.ForeignKey(TaskSession, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return (
            self.text
            if len(self.text) <= UserAnswer.STR_TEXT_LIMIT
            else self.text[: UserAnswer.STR_TEXT_LIMIT] + "..."
        )

    class Meta:
        unique_together = ("question", "task_session")
