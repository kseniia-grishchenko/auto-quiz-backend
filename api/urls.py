from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from api.views.course import CourseViewSet
from api.views.question import QuestionViewSet
from api.views.subject import SubjectViewSet
from api.views.quiz import QuizViewSet
from api.views.task import TaskViewSet
from api.views.task_session import TaskSessionViewSet

router = DefaultRouter()
router.register("subjects", SubjectViewSet, basename="subject")
router.register("courses", CourseViewSet, basename="courses")

# subjects/<subject_pk>/quizzes/
subject_router = NestedSimpleRouter(router, "subjects", lookup="subject")
subject_router.register("quizzes", QuizViewSet, basename="quiz")

# subjects/<subject_pk>/quizzes/<quiz_pk>/questions/
quiz_router = NestedSimpleRouter(subject_router, "quizzes", lookup="quiz")
quiz_router.register("questions", QuestionViewSet, basename="question")

# courses/<course_pk>/tasks/
course_router = NestedSimpleRouter(router, "courses", lookup="course")
course_router.register("tasks", TaskViewSet, basename="task")

# courses/<course_pk>/tasks/<task_pk>/sessions/
task_router = NestedSimpleRouter(course_router, "tasks", lookup="task")
task_router.register("sessions", TaskSessionViewSet, basename="session")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(subject_router.urls)),
    path("", include(quiz_router.urls)),
    path("", include(course_router.urls)),
    path("", include(task_router.urls)),
]

app_name = "api"
