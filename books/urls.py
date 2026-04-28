from django.urls import path
from . import views

urlpatterns = [
    # هذا المسار يربط الرابط /books/ بصفحة الرئيسية
    path('', views.home, name='home'),
    # هذا المسار يربط الرابط /books/books/ بقائمة الكتب
    path('books/', views.book_list, name='book_list'),
    # هذا المسار يربط الرابط /books/books/<pk>/ بتفاصيل كتاب معين
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    # هذا المسار يربط الرابط /books/authors/ بقائمة المؤلفين
    path('authors/', views.author_list, name='author_list'),
    # هذا المسار يربط الرابط /books/authors/<pk>/ بتفاصيل مؤلف معين
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    # هذا المسار يربط الرابط /books/categories/<pk>/ بالكتب حسب الفئة
    path('categories/<int:pk>/', views.books_by_category, name='books_by_category'),
    # هذا المسار يربط الرابط /books/about/ بصفحة عن الموقع
    path('about/', views.about, name='about'),
    # هذا المسار يربط الرابط /books/favorites/ بالكتب المفضلة
    path('favorites/', views.favorite_books, name='favorite_books'),
    # هذا المسار يربط الرابط /books/my-books/ بكتب المستخدم
    path('my-books/', views.my_books, name='my_books'),
    # هذا المسار يربط الرابط /books/search/ بصفحة البحث
    path('search/', views.search, name='search_books'),
    # هذا المسار يربط الرابط /books/upload/ بصفحة رفع الكتاب
    path('upload/', views.upload_book, name='upload_book'),
    # هذا المسار يربط الرابط /books/download/<pk>/ بتنزيل كتاب
    path('download/<int:pk>/', views.download_book, name='download_book'),
    # هذا المسار يربط الرابط /books/toggle-favorite/<pk>/ بإضافة/إزالة من المفضلة
    path('toggle-favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    # هذا المسار يربط الرابط /books/logout/ بتسجيل الخروج
    path('logout/', views.logout_view, name='logout'),
    # هذا المسار يربط الرابط /books/login/ بتسجيل الدخول
    path('login/', views.login_view, name='login'),
]