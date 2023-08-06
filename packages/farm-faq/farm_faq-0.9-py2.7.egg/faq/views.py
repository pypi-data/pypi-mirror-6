from django.shortcuts import render

from .models import Category, Question

def index(request):
    """
    This displays the FAQ page.
    """

    categories = Category.objects.all()
    questions = Question.objects.filter(active=True)

    return render(request, 'faq/index.html', {'categories': categories, 'questions': questions})
