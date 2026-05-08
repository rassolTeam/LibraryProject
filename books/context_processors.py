from django.db.models import Count, Q
from .models import Book, Category, Author


def sidebar_data(request):
    categories = Category.objects.filter(is_active=True).annotate(
        books_count=Count('book', filter=Q(book__is_available=True, book__is_approved=True))
    )
    return {
        'categories': categories,
        'total_books': Book.objects.filter(is_available=True, is_approved=True).count(),
        'total_authors': Author.objects.count(),
        'total_categories': categories.count(),
    }
