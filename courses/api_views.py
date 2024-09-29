from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer

class QuizListAPI(APIView):
    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

class QuizDetailAPI(APIView):
    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

class QuestionListAPI(APIView):
    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

class AnswerListAPI(APIView):
    def get(self, request, question_id):
        question = Question.objects.get(id=question_id)
        answers = question.answers.all()
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)