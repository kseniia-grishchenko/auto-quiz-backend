from __future__ import annotations

from typing import Type

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import Subject, Course


def invitation_token_verifications(
    request: Request,
    model: Type[Subject] | Type[Course],
    field: str,
    must_be_teacher: bool,
) -> Response | None:
    invitation_token = request.query_params.get("invitation_token", None)

    if not invitation_token:
        return Response(
            {"detail": "Provide invitation token!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    obj = model.objects.filter(invitation_token=invitation_token).first()

    if not obj:
        return Response(
            {"detail": "Invitation token is incorrect!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if must_be_teacher and not request.user.is_teacher:
        return Response(
            {"detail": "Only teachers can join!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if request.user in getattr(obj, field).all():
        return Response(
            {"detail": f"You already joined this {model.__name__.lower()}!"},
            status=status.HTTP_204_NO_CONTENT,
        )

    getattr(obj, field).add(request.user)
    return Response(
        {"detail": f"Successfully joined the {model.__name__.lower()}!"},
        status=status.HTTP_200_OK,
    )
