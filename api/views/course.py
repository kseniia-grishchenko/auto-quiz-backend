from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api.permissions import IsTeacher
from api.serializers import CourseSerializer
from api.utils import invitation_token_verifications
from core.models import Course


class CourseViewSet(viewsets.ModelViewSet):
    def get_permissions(self) -> list:
        if self.action in ("list", "retrieve"):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsTeacher]

        return [permission() for permission in permission_classes]

    def get_queryset(self) -> QuerySet:
        return Course.objects.filter(users__in=[self.request.user])

    def get_serializer_class(self) -> Type[Serializer]:
        return CourseSerializer

    def perform_create(self, serializer: CourseSerializer) -> Course:
        course = serializer.save()
        course.users.add(self.request.user)
        return course

    @action(detail=False, methods=["GET"])
    def join(self, request: Request) -> Response:
        return invitation_token_verifications(
            request, Course, "users", must_be_teacher=False
        )
