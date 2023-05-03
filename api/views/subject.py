from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api.serializers import SubjectSerializer, InvitationTokenSerializer
from api.utils import invitation_token_verifications
from core.models import Subject


class SubjectViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        return Subject.objects.filter(
            teachers__in=[self.request.user]
        ).prefetch_related("teachers")

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "join":
            return InvitationTokenSerializer

        return SubjectSerializer

    def perform_create(self, serializer: SubjectSerializer) -> Subject:
        subject = serializer.save()
        subject.teachers.add(self.request.user)
        return subject

    @action(detail=False, methods=["POST"])
    def join(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation_token = serializer.validated_data["invitation_token"]

        subject = invitation_token_verifications(
            invitation_token, request.user, Subject, "teachers"
        )

        subject.teachers.add(request.user)
        return Response(
            {"detail": f"Successfully joined the subject!"},
            status=status.HTTP_200_OK,
        )
