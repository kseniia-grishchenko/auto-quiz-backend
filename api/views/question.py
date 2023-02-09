from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import Serializer

from api.permissions import IsSubjectTeacher
from api.serializers import QuestionSerializer
from core.models import Question


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSubjectTeacher,)

    def get_queryset(self) -> QuerySet:
        return Question.objects.filter(quiz__id=self.kwargs["quiz_pk"])

    def get_serializer_class(self) -> Type[Serializer]:
        return QuestionSerializer

    def perform_create(self, serializer: QuestionSerializer) -> Question:
        return serializer.save(quiz_id=self.kwargs["quiz_pk"])
