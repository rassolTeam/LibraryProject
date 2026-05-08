
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.contrib import messages
from django.db.models import Q, Count, Prefetch, Sum
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from .models import Book, Category, Author, BookReview, FavoriteBook
from .forms import (
    BookUploadForm,
    LogoutConfirmationForm,
    UserRegistrationForm,
    UserLoginForm,
    BookSearchForm,
    BookReviewForm,
)

def register(request):
    """تسجيل مستخدم جديد"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم تسجيل حسابك بنجاح!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'تم تسجيل الدخول بنجاح.')
            return redirect('home')
    else:
        form = UserLoginForm()

    return render(request, 'books/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج مع تأكيد كلمة المرور"""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = LogoutConfirmationForm(request.POST, user=request.user)
        if form.is_valid():
            logout(request)
            messages.success(request, 'تم تسجيل الخروج بنجاح.')
            return redirect('home')
    else:
        form = LogoutConfirmationForm(user=request.user)

    return render(request, 'books/logout_confirm.html', {'form': form})

def home(request):
    """الصفحة الرئيسية"""
    featured_books = Book.objects.filter(is_featured=True, is_available=True, is_approved=True)[:6]
    is_approved = Book.objects.filter(is_approved=True)
    categories = Category.objects.filter(is_active=True)

    # إحصائيات
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()

    context = {
        'featured_books': featured_books,
        'categories': categories,
        'total_books': total_books,
        'is_approved':  is_approved,
        'total_authors': total_authors,
    }
    return render(request, 'books/home.html', context)

def about(request):
    """صفحة عن المكتبة"""
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.filter(is_active=True).count()

    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
    }
    return render(request, 'books/about.html', context)

@login_required
def upload_book(request):
    """رفع كتاب جديد"""
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES, uploaded_by=request.user)
        if form.is_valid():
            book = form.save(commit=False)
            # كتب الأدمن تعتمد تلقائيا، وبقيت الكتب تحتاج موافقة
            if request.user.is_staff or request.user.is_superuser:
                book.is_approved = True
                success_msg = 'تم رفع الكتاب بنجاح وتم اعتماده تلقائياً.'
            else:
                book.is_approved = False
                success_msg = 'تم رفع الكتاب بنجاح! سيتم مراجعته من قبل الإدمن قبل النشر.'
            book.save()
            messages.success(request, success_msg)
            return redirect('my_books')
    else:
        form = BookUploadForm(uploaded_by=request.user)
    return render(request, 'books/upload_book.html', {'form': form})

@login_required
def my_books(request):
    """الكتب التي رفعها المستخدم"""
    books = Book.objects.filter(user=request.user).select_related('author', 'category')
    categories = Category.objects.filter(is_active=True)
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()
    context = {'books': books, 'categories': categories, 'total_books': total_books, 'total_authors': total_authors}
    return render(request, 'books/my_books.html', context)

def about(request):
    """صفحة عن المكتبة"""
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.filter(is_active=True).count()

    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
    }
    return render(request, 'books/about.html', context)

def book_list(request):
    """قائمة جميع الكتب"""
    categories = Category.objects.filter(is_active=True).annotate(
        books_count=Count('book', filter=Q(book__is_available=True, book__is_approved=True))
    ).prefetch_related(
        Prefetch('book_set', queryset=Book.objects.filter(is_available=True, is_approved=True).select_related('author'))
    )
    
    # إحصائيات
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.filter(is_active=True).count()
    
    context = {
        'categories': categories,
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, pk):
    """تفاصيل الكتاب"""
    book = get_object_or_404(Book.objects.select_related('author', 'category', 'user'), pk=pk, is_available=True)
    
    # التحقق من الموافقة أو أن المستخدم هو صاحب الكتاب
    if not book.is_approved and (not request.user.is_authenticated or request.user != book.user):
        raise Http404("الكتاب غير متوفر حالياً.")
    
    # زيادة عدد المشاهدات
    book.views_count += 1
    book.save()

    # الكتب ذات الصلة
    related_books = Book.objects.filter(
        category=book.category,
        is_available=True,
        is_approved=True
    ).exclude(pk=pk).select_related('author')[:4]

    # التحقق إذا كان الكتاب في المفضلة
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteBook.objects.filter(
            user=request.user,
            book=book
        ).exists()

    # المراجعات
    reviews = book.reviews.select_related('user').all()

    review_form = None
    if request.user.is_authenticated:
        review_form = BookReviewForm(
            instance=BookReview.objects.filter(book=book, user=request.user).first(),
            book=book,
            review_user=request.user
        )

    context = {
        'book': book,
        'related_books': related_books,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'books/book_detail.html', context)

def books_by_category(request, category_id):
    """الكتب حسب التصنيف"""
    category = get_object_or_404(Category, id=category_id, is_active=True)
    books = Book.objects.filter(category=category, is_available=True, is_approved=True).select_related('author')
    
    # إحصائيات التصنيف
    total_books = books.count()
    total_views = books.aggregate(total_views=Sum('views_count'))['total_views'] or 0
    total_downloads = books.aggregate(total_downloads=Sum('downloads_count'))['total_downloads'] or 0
    total_reads = books.aggregate(total_reads=Sum('reads_count'))['total_reads'] or 0

    context = {
        'category': category,
        'books': books,
        'total_books': total_books,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'total_reads': total_reads,
    }
    return render(request, 'books/books_by_category.html', context)

def author_list(request):
    """قائمة المؤلفين"""
    authors = Author.objects.annotate(books_count=Count('book')).filter(books_count__gt=0)
    categories = Category.objects.filter(is_active=True)
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()
    context = {'authors': authors, 'categories': categories, 'total_books': total_books, 'total_authors': total_authors}
    return render(request, 'books/author_list.html', context)

def author_detail(request, pk):
    """تفاصيل المؤلف"""
    author = get_object_or_404(Author, pk=pk)
    books = Book.objects.filter(author=author, is_available=True, is_approved=True).select_related('category')
    
    # إحصائيات المؤلف
    total_books = books.count()
    total_views = books.aggregate(total_views=Sum('views_count'))['total_views'] or 0
    total_downloads = books.aggregate(total_downloads=Sum('downloads_count'))['total_downloads'] or 0
    total_reads = books.aggregate(total_reads=Sum('reads_count'))['total_reads'] or 0

    context = {
        'author': author,
        'books': books,
        'total_books': total_books,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'total_reads': total_reads,
    }
    return render(request, 'books/author_detail.html', context)

def search_books(request):
    """بحث الكتب"""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.filter(is_available=True, is_approved=True).select_related('author', 'category')
    search_query = ''

    if form.is_valid():
        search_query = form.cleaned_data.get('query', '')
        category = form.cleaned_data.get('category')
        year_from = form.cleaned_data.get('year_from')
        year_to = form.cleaned_data.get('year_to')

        if search_query:
            books = books.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        if category:
            books = books.filter(category=category)
        if year_from:
            books = books.filter(published_year__gte=year_from)
        if year_to:
            books = books.filter(published_year__lte=year_to)

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()

    context = {
        'books': books,
        'form': form,
        'search_query': search_query,
        'categories': categories,
        'total_books': total_books,
        'total_authors': total_authors,
    }
    return render(request, 'books/search.html', context)

@login_required
def favorite_books(request):
    """قائمة الكتب المفضلة"""
    favorites = FavoriteBook.objects.filter(user=request.user).select_related('book__author', 'book__category')
    categories = Category.objects.filter(is_active=True)
    total_books = Book.objects.filter(is_available=True, is_approved=True).count()
    total_authors = Author.objects.count()

    context = {
        'favorites': favorites,
        'categories': categories,
        'total_books': total_books,
        'total_authors': total_authors,
    }
    return render(request, 'books/favorite_books.html', context)

@login_required
def toggle_favorite(request, book_id):
    """إضافة/إزالة الكتاب من المفضلة"""
    book = get_object_or_404(Book, id=book_id, is_available=True)

    favorite, created = FavoriteBook.objects.get_or_create(
        user=request.user,
        book=book
    )

    if not created:
        # إذا كان موجوداً بالفعل، قم بحذفه
        favorite.delete()
        messages.success(request, 'تم إزالة الكتاب من المفضلة.')
    else:
        messages.success(request, 'تم إضافة الكتاب إلى المفضلة.')

    return redirect('book_detail', pk=book.id)

@login_required
def add_review(request, book_id):
    """إضافة مراجعة للكتاب"""
    book = get_object_or_404(Book, id=book_id, is_available=True)
    existing_review = BookReview.objects.filter(book=book, user=request.user).first()

    if request.method == 'POST':
        if existing_review:
            form = BookReviewForm(request.POST, instance=existing_review, book=book, review_user=request.user)
        else:
            form = BookReviewForm(request.POST, book=book, review_user=request.user)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'تم حفظ تقييمك للكتاب بنجاح.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return redirect('book_detail', pk=book.id)

def download_book(request, book_id):
    """تحميل الكتاب"""
    book = get_object_or_404(Book, id=book_id, is_available=True)

    if book.pdf_file:
        # زيادة عدد التحميلات
        book.downloads_count += 1
        book.save()

        book.pdf_file.open('rb')
        response = FileResponse(book.pdf_file, as_attachment=True, filename=f'{book.title}.pdf')
        return response
    else:
        messages.error(request, 'عذراً، ملف الكتاب غير متوفر للتحميل.')
        return redirect('book_detail', pk=book.id)

def read_online(request, book_id):
    """قراءة الكتاب online"""
    book = get_object_or_404(Book, id=book_id, is_available=True)

    if book.read_online_url:
        # زيادة عدد مرات القراءة
        book.reads_count += 1
        book.save()
        return redirect(book.read_online_url)
    else:
        messages.error(request, 'عذراً، القراءة الإلكترونية غير متوفرة لهذا الكتاب.')
        return redirect('book_detail', pk=book.id)

# API Views
@login_required
def api_toggle_favorite(request, book_id):
    """API لإضافة/إزالة المفضلة"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        book = get_object_or_404(Book, id=book_id, is_available=True)

        favorite, created = FavoriteBook.objects.get_or_create(
            user=request.user,
            book=book
        )

        if not created:
            favorite.delete()

        favorites_count = FavoriteBook.objects.filter(user=request.user).count()

        return JsonResponse({
            'success': True,
            'is_favorite': created,
            'favorites_count': favorites_count
        })

    return JsonResponse({'success': False}, status=400)

def api_search_suggestions(request):
    """API لاقتراحات البحث"""
    query = request.GET.get('q', '')

    if len(query) >= 2:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query),
            is_available=True
        )[:10]

        suggestions = []
        for book in books:
            suggestions.append({
                'id': book.id,
                'title': book.title,
                'author': book.author.name,
                'url': book.get_absolute_url()
            })

        return JsonResponse({'suggestions': suggestions})

    return JsonResponse({'suggestions': []})

