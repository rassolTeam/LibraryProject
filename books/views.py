from django.shortcuts import render
from django.db import models
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect
from django.contrib import messages
from .models import Book, Author, Category

# هذا الـ view مسؤول عن عرض صفحة الرئيسية
def home(request):
    featured_books = Book.objects.filter(is_featured=True, is_available=True, is_approved=True)[:6]
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()
    categories = Category.objects.filter(is_active=True)
    return render(request, 'books/home.html', {
        'featured_books': featured_books,
        'total_books': total_books,
        'total_authors': total_authors,
        'categories': categories,
    })

# هذا الـ view مسؤول عن عرض قائمة الكتب
def book_list(request):
    return render(request, 'books/book_list.html')

# هذا الـ view مسؤول عن عرض تفاصيل كتاب معين
def book_detail(request, pk):
    return render(request, 'books/book_detail.html')

# هذا الـ view مسؤول عن عرض قائمة المؤلفين
def author_list(request):
    return render(request, 'books/author_list.html')

# هذا الـ view مسؤول عن عرض تفاصيل مؤلف معين
def author_detail(request, pk):
    return render(request, 'books/author_detail.html')

# هذا الـ view مسؤول عن عرض الكتب حسب الفئة
def books_by_category(request, pk):
    return render(request, 'books/books_by_category.html')

# هذا الـ view مسؤول عن عرض صفحة عن الموقع
def about(request):
    return render(request, 'books/about.html')

# هذا الـ view مسؤول عن عرض الكتب المفضلة
def favorite_books(request):
    return render(request, 'books/favorite_books.html')

# هذا الـ view مسؤول عن عرض كتب المستخدم
def my_books(request):
    return render(request, 'books/my_books.html')

# هذا الـ view مسؤول عن عرض صفحة البحث
def search(request):
    query = request.GET.get('q', '')
    books = []
    if query:
        books = Book.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(author__name__icontains=query) |
            models.Q(description__icontains=query)
        ).filter(is_available=True, is_approved=True)
    return render(request, 'books/search.html', {'books': books, 'query': query})

# هذا الـ view مسؤول عن رفع الكتاب
def upload_book(request):
    return render(request, 'books/upload_book.html')

# هذا الـ view مسؤول عن تنزيل كتاب
def download_book(request, pk):
    return render(request, 'books/download_book.html')

# هذا الـ view مسؤول عن إضافة أو إزالة كتاب من المفضلة
def toggle_favorite(request, pk):
    return render(request, 'books/toggle_favorite.html')

# هذا الـ view مسؤول عن تسجيل الخروج
def logout_view(request):
    logout(request)
    return redirect('home')

# هذا الـ view مسؤول عن تسجيل الدخول
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    return render(request, 'books/login.html')