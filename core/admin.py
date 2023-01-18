from django.contrib import admin

from core.models import Subject, Course, Quiz, Question, QuizSession, UserAnswer


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    pass
