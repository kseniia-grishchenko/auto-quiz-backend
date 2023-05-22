from typing import Type

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api.permissions import IsCourseOwner
from api.serializers import (
    CourseSerializer,
    InvitationTokenSerializer,
    CourseDetailSerializer,
    CourseCreateSerializer,
    ChangeCourseUserPermissionSerializer,
)
from api.utils import invitation_token_verifications
from core.models import Course, CourseMembership


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return (
            Course.objects.filter(users__in=[self.request.user])
            .select_related("subject")
            .prefetch_related("users")
            .prefetch_related("coursemembership_set")
        )

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "join":
            return InvitationTokenSerializer

        if self.action == "change_user_permission":
            return ChangeCourseUserPermissionSerializer

        if self.action == "retrieve":
            return CourseDetailSerializer

        if self.action == "create":
            return CourseCreateSerializer

        return CourseSerializer

    def get_serializer_context(self) -> dict:
        return {"request": self.request}

    @action(detail=False, methods=["POST"])
    def join(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation_token = serializer.validated_data["invitation_token"]

        course = invitation_token_verifications(
            invitation_token, request.user, Course, "users"
        )

        CourseMembership.objects.create(
            user=request.user,
            course=course,
            permission=CourseMembership.UserPermission.STUDENT,
        )
        return Response(
            {"detail": f"Successfully joined the subject!"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], permission_classes=[IsCourseOwner])
    def change_user_permission(self, request: Request, pk: int = None) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if user == request.user:
            return Response(
                {"detail": f"You can't change your own permission!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        permission = serializer.validated_data["permission"]
        with transaction.atomic():
            course = self.get_object()

        course = self.get_object()
        course_membership = get_object_or_404(
            CourseMembership, user=user, course=course
        )
        course_membership.permission = permission
        course_membership.save()
        # check if this teacher have access to the subject
        if permission == CourseMembership.UserPermission.TEACHER:
            if user not in course.subject.teachers.all():
                # add teacher to subjects teachers
                course.subject.teachers.add(user)
        course_membership = get_object_or_404(
            CourseMembership, user=user, course=course
        )
        course_membership.permission = permission
        course_membership.save()

        return Response(
            {"detail": f"Successfully changed user permission!"},
            status=status.HTTP_200_OK,
        )
