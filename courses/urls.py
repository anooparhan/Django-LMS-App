from django.urls import path

from django.urls import path
from .views import register, login_view, teacher_dashboard, student_dashboard, course_list, submit_answers, student_marks
from .views import upload_course
from . import views
from .views import enroll_course
from .views import enroll_course, enrolled_courses,CourseDetailView
from .api_views import QuizListAPI, QuizDetailAPI, QuestionListAPI, AnswerListAPI






urlpatterns = [
    path('', course_list, name='course_list'),
    path('upload/', upload_course, name='upload_course'),

    # path('<int:book_id>/', book_detail, name='book_detail'),
    # path('upload/', upload_book, name='upload_book'),
    # path('<int:book_id>/update/', update_book, name='update_book'),
    # path('<int:book_id>/delete/', delete_book, name='delete_book'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', student_dashboard, name='student_dashboard'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('add_question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('add_answer/<int:question_id>/', views.add_answer, name='add_answer'),
    path('submit_answers/<int:quiz_id>/', views.submit_answers, name='submit_answers'),
    path('assign_marks/<int:quiz_id>/', views.assign_marks, name='assign_marks'),
    path('performance_report/<int:quiz_id>/', views.performance_report, name='performance_report'),
    path('student/marks/', student_marks, name='student_marks'),
    path('enroll_course/<int:course_id>/', enroll_course, name='enroll_course'),
    path('enroll/<int:course_id>/', enroll_course, name='enroll_course'),
    path('enrolled_courses/', enrolled_courses, name='enrolled_courses'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),  # Add this line for course detail
    path('api/quizzes/', QuizListAPI.as_view(), name='quiz_list_api'),
    path('api/quizzes/<int:quiz_id>/', QuizDetailAPI.as_view(), name='quiz_detail_api'),
    path('api/quizzes/<int:quiz_id>/questions/', QuestionListAPI.as_view(), name='question_list_api'),
    path('api/questions/<int:question_id>/answers/', AnswerListAPI.as_view(), name='answer_list_api'),
    path('trivia/', views.trivia_view, name='trivia_view'), 
    path('quizzes/', views.quizzes, name='quizzes'),
    path('submission_success/', views.submission_success, name='submission_success'),
    # path('quiz_done/<int:quiz_id>/', views.quiz_done, name='quiz_done'),
]