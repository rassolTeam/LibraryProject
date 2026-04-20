from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="اسم التصنيف")
    description = models.TextField(blank=True, verbose_name="الوصف")
    icon = models.CharField(max_length=50, default='fas fa-book', verbose_name="الأيقونة")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('books_by_category', kwargs={'category_id': self.pk})


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المؤلف")
    bio = models.TextField(blank=True, verbose_name="السيرة الذاتية")
    photo = models.ImageField(upload_to='authors/', blank=True, null=True, verbose_name="صورة المؤلف")

    class Meta:
        verbose_name = "مؤلف"
        verbose_name_plural = "المؤلفون"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk': self.pk})


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان الكتاب")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="المؤلف")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="التصنيف")
    description = models.TextField(blank=True, verbose_name="الوصف")
    cover_image = models.ImageField(upload_to='book_covers/', verbose_name="صورة الغلاف")
    pdf_file = models.FileField(upload_to='books_pdf/', blank=True, null=True, verbose_name="ملف PDF")
    read_online_url = models.URLField(blank=True, verbose_name="رابط القراءة online")
    published_year = models.IntegerField(verbose_name="سنة النشر")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    is_available = models.BooleanField(default=True, verbose_name="متاح للعرض")
    is_approved = models.BooleanField(default=True, verbose_name="موافق عليه من الإدمن")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم الذي رفع الكتاب", null=True, blank=True)

    # إحصائيات
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    downloads_count = models.PositiveIntegerField(default=0, verbose_name="عدد التحميلات")
    reads_count = models.PositiveIntegerField(default=0, verbose_name="عدد مرات القراءة")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كتاب"
        verbose_name_plural = "الكتب"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.pk})


class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name="التقييم")
    comment = models.TextField(verbose_name="التعليق")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مراجعة"
        verbose_name_plural = "المراجعات"
        unique_together = ['book', 'user']


class FavoriteBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كتاب مفضل"
        verbose_name_plural = "الكتب المفضلة"
        unique_together = ['user', 'book']