from .models import Category


def faq_categories(request):

    objs = Category.objects.all()

    return {
        'faq_categories': objs
    }