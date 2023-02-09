from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.serializers import Serializer

from api.permissions import IsSubjectTeacher
from api.serializers import QuizSerializer
from core.models import Quiz


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = (IsSubjectTeacher,)

    def get_queryset(self) -> QuerySet:
        return Quiz.objects.filter(subject_id=self.kwargs["subject_pk"])

    def get_serializer_class(self) -> Type[Serializer]:
        return QuizSerializer

    def perform_create(self, serializer: QuizSerializer) -> Quiz:
        return serializer.save(subject_id=self.kwargs["subject_pk"])
