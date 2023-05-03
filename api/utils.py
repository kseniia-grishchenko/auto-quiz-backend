from typing import Type

from django.conf import settings
from rest_framework.exceptions import ValidationError
from core.models import Subject, Course


def invitation_token_verifications(
    invitation_token: str,
    user: settings.AUTH_USER_MODEL,
    model: Type[Subject] | Type[Course],
    field: str,
) -> Subject | Course:
    obj = model.objects.filter(invitation_token=invitation_token).first()

    if not obj:
        raise ValidationError("Invitation token is incorrect!")

    if user in getattr(obj, field).all():
        raise ValidationError(f"You already joined this {model.__name__.lower()}!")

    return obj
