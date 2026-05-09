
from django.urls import path
from . import views

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # الكتب
    path('books/', views.book_list, name='book_list'),
    path('books/category/<int:category_id>/', views.books_by_category, name='books_by_category'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('search/', views.search_books, name='search_books'),

    # المؤلفون
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),

    # المفضلة والمراجعات
    path('favorites/', views.favorite_books, name='favorite_books'),
    path('books/<int:book_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('books/<int:book_id>/review/', views.add_review, name='add_review'),

    # التحميل والقراءة
    path('books/<int:book_id>/download/', views.download_book, name='download_book'),
    path('books/<int:book_id>/read/', views.read_book, name='read_book'),

    # رفع الكتب
    path('upload-book/', views.upload_book, name='upload_book'),
    path('my-books/', views.my_books, name='my_books'),

    # APIs
    path('api/books/<int:book_id>/favorite/', views.api_toggle_favorite, name='api_toggle_favorite'),
    path('api/search/suggestions/', views.api_search_suggestions, name='api_search_suggestions'),

    # المصادقة
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
