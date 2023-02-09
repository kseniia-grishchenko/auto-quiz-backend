from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets, mixins
from rest_framework.serializers import Serializer

from api.permissions import IsCourseTeacher
from api.serializers import TaskSessionSerializer, TaskSessionDetailSerializer
from core.models import TaskSession


class TaskSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsCourseTeacher,)

    def get_queryset(self) -> QuerySet:
        return TaskSession.objects.filter(
            task_id=self.kwargs["task_pk"]
        ).select_related("user")

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return TaskSessionDetailSerializer

        return TaskSessionSerializer
