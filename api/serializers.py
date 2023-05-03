from rest_framework import serializers

from account.serializers import UserSerializer
from core.models import (
    Subject,
    Course,
    Quiz,
    Question,
    Task,
    TaskSession,
    CourseMembership,
)


class SubjectNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name")
        read_only_fields = ("id",)


class SubjectSerializer(serializers.ModelSerializer):
    teachers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ("id", "name", "teachers", "invitation_token")
        read_only_fields = ("id", "teachers", "invitation_token")


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ("id", "name", "max_duration", "subject")
        read_only_fields = ("id", "subject")


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "title", "expected_answer", "value", "quiz")
        read_only_fields = ("id", "quiz")


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "subject", "users", "invitation_token")
        read_only_fields = ("id", "users", "invitation_token")

    def create(self, validated_data: dict) -> Course:
        subject = validated_data["subject"]
        if self.context["request"].user not in subject.teachers.all():
            raise serializers.ValidationError("You are not a teacher of this subject")

        course = super().create(validated_data)
        CourseMembership.objects.create(
            user=self.context["request"].user,
            course=course,
            permission=CourseMembership.UserPermission.OWNER,
        )
        return course


class CourseSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    subject = SubjectNestedSerializer(many=False, read_only=True)

    class Meta:
        model = Course
        fields = ("id", "name", "subject", "users", "invitation_token")
        read_only_fields = ("id", "users", "invitation_token")


class CourseMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = CourseMembership
        fields = ("id", "user", "permission")
        read_only_fields = ("id", "user", "permission")


class CourseDetailSerializer(CourseSerializer):
    users = CourseMembershipSerializer(
        source="coursemembership_set", many=True, read_only=True
    )


class TaskSerializer(serializers.ModelSerializer):
    quiz_name = serializers.CharField(source="quiz.name", read_only=True)

    class Meta:
        model = Task
        fields = ("id", "title", "deadline", "course", "quiz", "quiz_name")
        read_only_fields = ("id", "course")


class QuizNestedSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "name", "max_duration", "subject", "questions")


class TaskDetailSerializer(serializers.ModelSerializer):
    quiz = QuizNestedSerializer(many=False, read_only=True)

    class Meta:
        model = Task
        fields = ("id", "title", "deadline", "course", "quiz")
        read_only_fields = ("id", "course", "quiz")


class TaskSessionSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.get_full_name")

    class Meta:
        model = TaskSession
        fields = ("id", "started_at", "finished_at", "task", "user", "user_full_name")


class TaskSessionDetailSerializer(serializers.ModelSerializer):
    task = TaskDetailSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = TaskSession
        fields = ("id", "started_at", "finished_at", "task", "user")
        read_only_fields = ("id", "started_at", "finished_at", "task", "user")


class InvitationTokenSerializer(serializers.Serializer):
    invitation_token = serializers.CharField(max_length=255, required=True)


class ChangeCourseUserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMembership
        fields = ("permission", "user")
