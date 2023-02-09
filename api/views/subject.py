from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api.permissions import IsTeacher
from api.serializers import SubjectSerializer
from api.utils import invitation_token_verifications
from core.models import Subject


class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTeacher,)

    def get_queryset(self) -> QuerySet:
        return Subject.objects.filter(teachers__in=[self.request.user])

    def get_serializer_class(self) -> Type[Serializer]:
        return SubjectSerializer

    def perform_create(self, serializer: SubjectSerializer) -> Subject:
        subject = serializer.save()
        subject.teachers.add(self.request.user)
        return subject

    @action(detail=False, methods=["GET"])
    def join(self, request: Request) -> Response:
        return invitation_token_verifications(
            request, Subject, "teachers", must_be_teacher=True
        )
