from django import template

register = template.Library()

@register.filter
def get_item(student_answers, question_id):
    for answer in student_answers:
        if answer.question.id == question_id:
            return answer.answer.id  # Return the ID of the answer selected by the student
    return None

@register.filter
def get_marks(student_answers, answer_id):
    for answer in student_answers:
        if answer.answer.id == answer_id:
            return answer.marks  # Return the marks for the specific answer
    return 0
