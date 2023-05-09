from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets, mixins
from rest_framework.serializers import Serializer

from api.permissions import IsCourseStudent, IsCourseTeacher
from api.serializers import TaskSessionSerializer, TaskSessionResultSerializer
from core.models import TaskSession


class TaskSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsCourseStudent,)

    def get_queryset(self) -> QuerySet:
        queryset = TaskSession.objects.filter(task_id=self.kwargs["task_pk"])

        if not IsCourseTeacher().has_permission(self.request, self):
            queryset = queryset.filter(user=self.request.user)

        return queryset.select_related("user").prefetch_related(
            "useranswer_set__question"
        )

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return TaskSessionResultSerializer

        return TaskSessionSerializer
