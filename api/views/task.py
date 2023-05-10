import datetime
from typing import Type

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api.permissions import IsCourseTeacher, IsCourseStudent
from api.serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    TaskSessionDetailSerializer,
    TaskSessionResultSerializer,
    TaskSessionFinishSerializer,
)
from core.models import Task, Course, TaskSession, UserAnswer
from openai_client.main import get_assistant_answer

MAX_SENDING_DELAY_MIN = 3


class TaskViewSet(viewsets.ModelViewSet):
    def get_permissions(self) -> list:
        if self.action in ("list", "start", "finish", None):
            permission_classes = [IsCourseStudent]
        else:
            permission_classes = [IsCourseTeacher]

        return [permission() for permission in permission_classes]

    def get_queryset(self) -> QuerySet:
        return Task.objects.filter(course_id=self.kwargs["course_pk"]).prefetch_related(
            "quiz__questions"
        )

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("retrieve", "update", "partial_update"):
            return TaskDetailSerializer

        if self.action == "finish":
            return TaskSessionFinishSerializer

        if self.action == "start":
            return Serializer

        return TaskSerializer

    def perform_create(self, serializer: TaskSerializer) -> Task:
        quiz = serializer.validated_data["quiz"]
        course = Course.objects.get(id=self.kwargs["course_pk"])

        if quiz.subject != course.subject:
            raise ValidationError(
                {"quiz": "You cannot use quiz from different subject!"}
            )

        return serializer.save(course=course)

    @action(detail=True, methods=["POST"], name="start")
    def start(self, request: Request, pk: int = None, **kwargs) -> Response:
        task = self.get_object()

        if datetime.datetime.now() > task.deadline:
            return Response(
                {"detail": "You've missed deadline for the task!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task_session, is_created = TaskSession.objects.get_or_create(
            task=task, user=request.user
        )

        serializer = TaskSessionDetailSerializer(task_session)

        if not is_created:
            return Response(
                {
                    "detail": "You already have started session for this task!",
                    "task_session": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], name="finish")
    def finish(self, request: Request, pk: int = None, **kwargs) -> Response:
        task = self.get_object()

        if datetime.datetime.now() > task.deadline + datetime.timedelta(
            minutes=MAX_SENDING_DELAY_MIN
        ):
            return Response(
                {"detail": "You've missed deadline for the task!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task_session = TaskSession.objects.filter(task=task, user=request.user).first()

        if task_session is None:
            return Response(
                {"detail": "You have not started session for this task!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if task_session.finished_at is not None:
            return Response(
                {"detail": "You have already finished this task!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # answers format: [{"question_id": 1, "answer": "some answer"}, ...]

        serializer_class = self.get_serializer_class()

        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for answer in serializer.validated_data["answers"]:
                question_id = answer["question_id"]
                question = task.quiz.questions.filter(id=question_id).first()

                if question is None:
                    raise ValidationError(
                        {
                            "answers": f"Question with id {question_id} does not exist for this task!"
                        }
                    )

                answer = answer["answer"]

                score, explanation = get_assistant_answer(
                    question.title, question.expected_answer, answer
                )

                UserAnswer.objects.create(
                    question=question,
                    text=answer,
                    score=score,
                    comment=explanation,
                    task_session=task_session,
                )

            task_session.finished_at = datetime.datetime.now()
            task_session.save()

        task_session.refresh_from_db()

        serializer = TaskSessionResultSerializer(task_session)

        return Response(serializer.data, status=status.HTTP_200_OK)
