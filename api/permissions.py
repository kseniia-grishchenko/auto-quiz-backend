from typing import Any

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.models import Subject, CourseMembership


class IsSubjectTeacher(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return (
            request.user.is_authenticated
            and request.user
            in get_object_or_404(Subject, pk=view.kwargs["subject_pk"]).teachers.all()
        )


class IsCourseBasePermission(BasePermission):
    permissions = []

    def has_permission(self, request: Request, view: Any) -> bool:
        course_pk = view.kwargs.get("course_pk") or view.kwargs.get("pk")
        return (
            request.user.is_authenticated
            and get_object_or_404(
                CourseMembership,
                user=request.user,
                course_id=course_pk,
            ).permission
            in self.permissions
        )


class IsCourseOwner(IsCourseBasePermission):
    permissions = [CourseMembership.UserPermission.OWNER]


class IsCourseTeacher(IsCourseBasePermission):
    permissions = [
        CourseMembership.UserPermission.TEACHER,
        CourseMembership.UserPermission.OWNER,
    ]


class IsCourseStudent(IsCourseBasePermission):
    permissions = [
        CourseMembership.UserPermission.STUDENT,
        CourseMembership.UserPermission.TEACHER,
        CourseMembership.UserPermission.OWNER,
    ]
