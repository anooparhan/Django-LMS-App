from django.shortcuts import render
from django.shortcuts import render,redirect
from .models import Course
from django.views.generic import DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Course

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import CustomUser
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm 
from django.shortcuts import render, redirect
from .forms import CourseForm
from .forms import QuizForm, QuestionForm, AnswerForm
from .models import Quiz, Question, Answer, StudentAnswer
from .models import Enrollment
import requests
from django.shortcuts import render
# from .import get_trivia_questions, parse_trivia_response

API_ENDPOINT = 'https://opentdb.com/api.php?amount=10&category=9&difficulty=easy&type=multiple'



def get_trivia_questions():
    response = requests.get(API_ENDPOINT)
    return response.json()


def parse_trivia_response(response):
    questions = []
    for result in response['results']:
        question = {
            'question': result['question'],
            'answers': result['incorrect_answers'] + [result['correct_answer']],
            'correct_answer': result['correct_answer']
        }
        questions.append(question)
    return questions



def trivia_view(request):
    response = get_trivia_questions()
    questions = parse_trivia_response(response)
    return render(request, 'trivia.html', {'questions': questions})

def create_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.teacher = request.user
            quiz.save()
            return redirect('add_question', quiz_id=quiz.id)
    else:
        quiz_form = QuizForm()
    return render(request, 'create_quiz.html', {'quiz_form': quiz_form})

def add_question(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('add_answer', question_id=question.id)
    else:
        question_form = QuestionForm()
    return render(request, 'add_question.html', {'question_form': question_form, 'quiz': quiz})


def add_answer(request, question_id):
    question = Question.objects.get(id=question_id)
    current_answers = Answer.objects.filter(question=question)

    # Check if the question already has 4 answers
    if current_answers.count() >= 4:
        # If 4 answers are added, show "Done" button instead of the form
        return render(request, 'add_answer.html', {
            'question': question,
            'answers': current_answers,
            'done': True  # Pass a flag to indicate that 4 answers have been added
        })

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('add_answer', question_id=question.id)
    else:
        answer_form = AnswerForm()

    return render(request, 'add_answer.html', {
        'answer_form': answer_form, 
        'question': question,
        'answers': current_answers,
        'done': False  # No "Done" button until 4 answers are added
    })


def upload_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('course_list')  # Redirect after success
    else:
        form = CourseForm()
    return render(request, 'upload_course.html', {'form': form})



def course_list(request):
    return render(request, 'course_list.html') 


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == 'teacher':
                return redirect('teacher_dashboard')  # Update with your teacher dashboard URL
            elif user.user_type == 'student':
                return redirect('student_dashboard')  # Update with your student dashboard URL
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def student_dashboard(request):
    quizzes = Quiz.objects.all()  # Fetch all quizzes
    courses = Course.objects.all()  # Fetch all courses
    student_answers = StudentAnswer.objects.filter(student=request.user)

    return render(request, 'student_dashboard.html', {
        'quizzes': quizzes,
        'courses': courses,
        'student_answers': {answer.question.id: answer.answer.id for answer in student_answers},
        'username': request.user.username
    })

def submit_answers(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Clear previous answers for the current quiz
        StudentAnswer.objects.filter(student=request.user, quiz=quiz).delete()

        for question in quiz.questions.all():
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                # Store the student's answer
                StudentAnswer.objects.create(
                    student=request.user,
                    question=question,
                    answer_id=selected_answer_id,
                    quiz=quiz  # Set the quiz
                )

        return render(request, 'submission_success.html')


    return redirect('student_dashboard')
def teacher_dashboard(request):
    quizzes = Quiz.objects.prefetch_related('questions__answers', 'student_answers')
    
    return render(request, 'teacher_dashboard.html', {
        'quizzes': quizzes
    })

def assign_marks(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        for student_answer in quiz.student_answers.all():
            marks = request.POST.get(f'marks_{student_answer.id}', 0)
            if marks.isdigit():
                student_answer.marks = int(marks)
                student_answer.save()
        
        # Redirect to teacher dashboard after marks are submitted
        return redirect('teacher_dashboard')

    return redirect('teacher_dashboard')


def performance_report(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Filter student answers by the currently logged-in student
    student_answers = quiz.student_answers.filter(student=request.user)
    
    report_data = []
    
    for student_answer in student_answers:
        correct_answer = student_answer.question.answers.filter(is_correct=True).first()
        report_data.append({
            'student_answer': student_answer,
            'correct_answer': correct_answer
        })
    
    return render(request, 'performance_report.html', {
        'quiz': quiz,
        'report_data': report_data
    })
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


def student_marks(request):
    quizzes = Quiz.objects.all()
    student_answers = StudentAnswer.objects.filter(student=request.user)

    return render(request, 'student_marks.html', {
        'quizzes': quizzes,
        'student_answers': {answer.question.id: answer for answer in student_answers}
    })



def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)

    if created:
        messages.success(request, 'You have successfully enrolled in the course!')
    else:
        messages.info(request, 'You are already enrolled in this course.')

    return redirect('enrolled_courses')  # Redirect to the view that lists enrolled courses
def enrolled_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    courses = [enrollment.course for enrollment in enrollments]

    return render(request, 'enrolled_courses.html', {'courses': courses})
class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'  # Update with your actual template path
    context_object_name = 'course'


def quizzes(request):
    quizzes = Quiz.objects.all()  # Fetch all quizzes
    courses = Course.objects.all()  # Fetch all courses
    student_answers = StudentAnswer.objects.filter(student=request.user)

    return render(request, 'quizzes.html', {
        'quizzes': quizzes,
        'courses': courses,
        'student_answers': {answer.question.id: answer.answer.id for answer in student_answers},
        'username': request.user.username
    })
def submission_success(request):
    return render(request, 'submission_success.html')
