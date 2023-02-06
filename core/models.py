from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q


class Subject(models.Model):
    name = models.CharField(max_length=255)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="subjects")

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="courses")

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
    value = models.IntegerField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title


class QuizSession(models.Model):
    deadline = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.quiz.name + " " + self.user.email

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(
                    Q(started_at__isnull=True)
                    | Q(finished_at__isnull=True)
                    | Q(started_at__lt=models.F("finished_at"))
                ),
                name="started_at_finished_at_check",
            ),
            CheckConstraint(
                check=Q(
                    Q(started_at__isnull=True) | Q(started_at__lte=models.F("deadline"))
                ),
                name="started_at_deadline_check",
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
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return (
            self.text
            if len(self.text) <= UserAnswer.STR_TEXT_LIMIT
            else self.text[: UserAnswer.STR_TEXT_LIMIT] + "..."
        )

    class Meta:
        unique_together = ("question", "quiz_session")