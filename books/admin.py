from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Author, Book, BookReview, FavoriteBook


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'books_count']
    list_filter = ['is_active']  # تم إصلاح: إزالة created_at
    list_editable = ['is_active']
    search_fields = ['name']

    def books_count(self, obj):
        return obj.book_set.count()

    books_count.short_description = 'عدد الكتب'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'books_count', 'photo_preview']
    search_fields = ['name']
    readonly_fields = ['photo_preview']  # تم إصلاح: إزالة created_at من list_filter

    def books_count(self, obj):
        return obj.book_set.count()

    books_count.short_description = 'عدد الكتب'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                               obj.photo.url)
        return "لا توجد صورة"

    photo_preview.short_description = 'صورة المصغرة'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'category',
        'published_year',
        'is_featured',
        'is_available',
        'is_approved',
        'user',
        'views_count',
        'cover_preview'
    ]
    list_filter = ['category', 'is_featured', 'is_available', 'is_approved', 'published_year']
    list_editable = ['is_featured', 'is_available', 'is_approved']
    actions = ['approve_books', 'disapprove_books']
    search_fields = ['title', 'author__name', 'description']
    readonly_fields = [
        'views_count',
        'downloads_count',
        'reads_count',
        'created_at',
        'cover_preview',
        'file_size_display'
    ]  # تم إصلاح: إزالة updated_at

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'author', 'category', 'description')
        }),
        ('الملفات والوسائط', {
            'fields': ('cover_image', 'cover_preview', 'pdf_file', 'read_online_url')
        }),
        ('معلومات النشر', {
            'fields': ('published_year', 'is_featured', 'is_available')
        }),
        ('الإحصائيات', {
            'fields': ('views_count', 'downloads_count', 'reads_count', 'file_size_display'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="100" style="object-fit: cover; border-radius: 5px;" />',
                               obj.cover_image.url)
        return "لا توجد صورة"

    cover_preview.short_description = 'معاينة الغلاف'

    def file_size_display(self, obj):
        if obj.pdf_file and obj.pdf_file.size:
            size = obj.pdf_file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "غير متوفر"

    file_size_display.short_description = 'حجم الملف'

    def approve_books(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"تمت الموافقة على {updated} كتاب(ات) بنجاح.")

    approve_books.short_description = 'الموافقة على الكتب المحددة'

    def disapprove_books(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"تم إلغاء الموافقة عن {updated} كتاب(ات) بنجاح.")

    disapprove_books.short_description = 'إلغاء الموافقة عن الكتب المحددة'


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['book__title', 'user__username', 'comment']
    readonly_fields = ['created_at']


@admin.register(FavoriteBook)
class FavoriteBookAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'book__title']
    readonly_fields = ['created_at']