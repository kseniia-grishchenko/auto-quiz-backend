from typing import Any

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.models import Subject, Course


class IsTeacher(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.is_teacher
        )


class IsSubjectTeacher(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_teacher
            and request.user
            in get_object_or_404(Subject, pk=view.kwargs["subject_pk"]).teachers.all()
        )


class IsCourseTeacher(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return (
            request.user.is_authenticated
            and request.user.is_teacher
            and request.user
            in get_object_or_404(Course, pk=view.kwargs["course_pk"]).users.all()
        )


class IsCourseUser(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return (
            request.user.is_authenticated
            and request.user
            in get_object_or_404(Course, pk=view.kwargs["course_pk"]).users.all()
        )
