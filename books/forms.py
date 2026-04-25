from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime

from .models import Book, BookReview, Author, Category


# ─────────────────────────────────────────────
#  1. فورم تسجيل مستخدم جديد
# ─────────────────────────────────────────────
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="الاسم الأول",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسمك الأول',
            'id': 'id_first_name',
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label="اسم العائلة",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم العائلة',
            'id': 'id_last_name',
        })
    )
    email = forms.EmailField(
        required=True,
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'id': 'id_email',
        })
    )
    username = forms.CharField(
        max_length=30,
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اختر اسم مستخدم فريد',
            'id': 'id_username',
        })
    )
    password1 = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '8 أحرف على الأقل',
            'id': 'id_password1',
        })
    )
    password2 = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور',
            'id': 'id_password2',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    # ── Validation ──
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("هذا البريد الإلكتروني مسجّل مسبقاً.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError("اسم المستخدم يجب أن يكون 4 أحرف على الأقل.")
        if not username.isalnum():
            raise ValidationError("اسم المستخدم يجب أن يحتوي على أحرف وأرقام فقط (بدون مسافات أو رموز).")
        if User.objects.filter(username=username).exists():
            raise ValidationError("اسم المستخدم هذا مأخوذ، اختر اسماً آخر.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError("الاسم الأول مطلوب.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError("اسم العائلة مطلوب.")
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────
#  2. فورم تسجيل الدخول
# ─────────────────────────────────────────────
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم',
            'id': 'id_login_username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور',
            'id': 'id_login_password',
        })
    )

    error_messages = {
        'invalid_login': "اسم المستخدم أو كلمة المرور غير صحيحة.",
        'inactive': "هذا الحساب غير مفعّل.",
    }


# ─────────────────────────────────────────────
#  3. فورم رفع / إضافة كتاب
# ─────────────────────────────────────────────
class BookUploadForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        label="عنوان الكتاب",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل عنوان الكتاب',
            'id': 'id_book_title',
        })
    )
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label="المؤلف",
        empty_label="── اختر المؤلف ──",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_book_author',
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        label="التصنيف",
        empty_label="── اختر التصنيف ──",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_book_category',
        })
    )
    description = forms.CharField(
        required=False,
        label="وصف الكتاب",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'اكتب وصفاً مختصراً للكتاب...',
            'id': 'id_book_description',
        })
    )
    cover_image = forms.ImageField(
        label="صورة الغلاف",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'id_book_cover',
            'accept': 'image/*',
        })
    )
    pdf_file = forms.FileField(
        required=False,
        label="ملف PDF",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'id_book_pdf',
            'accept': '.pdf',
        })
    )
    read_online_url = forms.URLField(
        required=False,
        label="رابط القراءة أونلاين",
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://...',
            'id': 'id_book_url',
        })
    )
    published_year = forms.IntegerField(
        label="سنة النشر",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 2023',
            'id': 'id_book_year',
            'min': '1000',
            'max': str(datetime.datetime.now().year),
        })
    )

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'category', 'description',
            'cover_image', 'pdf_file', 'read_online_url', 'published_year',
        ]

    # ── Validation ──
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 2:
            raise ValidationError("عنوان الكتاب قصير جداً.")
        return title

    def clean_published_year(self):
        year = self.cleaned_data.get('published_year')
        current_year = datetime.datetime.now().year
        if year < 1000:
            raise ValidationError("سنة النشر غير صحيحة.")
        if year > current_year:
            raise ValidationError(f"سنة النشر لا يمكن أن تكون بعد {current_year}.")
        return year

    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image')
        if image:
            # التحقق من الحجم (5MB كحد أقصى)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("حجم صورة الغلاف يجب أن يكون أقل من 5MB.")
            # التحقق من نوع الملف
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = image.name.lower()
            if not any(ext.endswith(e) for e in valid_extensions):
                raise ValidationError("صيغة الصورة يجب أن تكون: JPG, PNG, أو WEBP.")
        return image

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            # التحقق من الحجم (50MB كحد أقصى)
            if pdf.size > 50 * 1024 * 1024:
                raise ValidationError("حجم ملف PDF يجب أن يكون أقل من 50MB.")
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError("الملف المرفق يجب أن يكون بصيغة PDF.")
        return pdf

    def clean(self):
        cleaned_data = super().clean()
        pdf_file = cleaned_data.get('pdf_file')
        read_online_url = cleaned_data.get('read_online_url')
        # يجب توفير طريقة واحدة على الأقل للقراءة
        if not pdf_file and not read_online_url:
            raise ValidationError(
                "يجب توفير ملف PDF أو رابط القراءة أونلاين على الأقل."
            )
        return cleaned_data


# ─────────────────────────────────────────────
#  4. فورم مراجعة كتاب (تقييم + تعليق)
# ─────────────────────────────────────────────
class BookReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        ('', '── اختر تقييمك ──'),
        (5, '⭐⭐⭐⭐⭐  ممتاز'),
        (4, '⭐⭐⭐⭐    جيد جداً'),
        (3, '⭐⭐⭐      جيد'),
        (2, '⭐⭐        مقبول'),
        (1, '⭐          ضعيف'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        label="التقييم",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_review_rating',
        })
    )
    comment = forms.CharField(
        label="تعليقك على الكتاب",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'شاركنا رأيك في هذا الكتاب...',
            'id': 'id_review_comment',
            'maxlength': '1000',
        })
    )

    class Meta:
        model = BookReview
        fields = ['rating', 'comment']

    # ── Validation ──
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise ValidationError("يرجى اختيار تقييم للكتاب.")
        rating = int(rating)
        if rating not in [1, 2, 3, 4, 5]:
            raise ValidationError("التقييم يجب أن يكون بين 1 و 5.")
        return rating

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if len(comment) < 10:
            raise ValidationError("التعليق قصير جداً، اكتب 10 أحرف على الأقل.")
        if len(comment) > 1000:
            raise ValidationError("التعليق طويل جداً، الحد الأقصى 1000 حرف.")
        return comment


# ─────────────────────────────────────────────
#  5. فورم البحث عن الكتب
# ─────────────────────────────────────────────
class BookSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label="ابحث عن كتاب",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث بالعنوان أو المؤلف...',
            'id': 'id_search_query',
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        label="التصنيف",
        empty_label="جميع التصنيفات",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_search_category',
        })
    )
    year_from = forms.IntegerField(
        required=False,
        label="من سنة",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2000',
            'id': 'id_year_from',
            'min': '1000',
            'max': str(datetime.datetime.now().year),
        })
    )
    year_to = forms.IntegerField(
        required=False,
        label="إلى سنة",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': str(datetime.datetime.now().year),
            'id': 'id_year_to',
            'min': '1000',
            'max': str(datetime.datetime.now().year),
        })
    )

    # ── Validation ──
    def clean(self):
        cleaned_data = super().clean()
        year_from = cleaned_data.get('year_from')
        year_to = cleaned_data.get('year_to')
        current_year = datetime.datetime.now().year

        if year_from and year_from > current_year:
            self.add_error('year_from', f"السنة لا يمكن أن تكون أكبر من {current_year}.")

        if year_to and year_to > current_year:
            self.add_error('year_to', f"السنة لا يمكن أن تكون أكبر من {current_year}.")

        if year_from and year_to and year_from > year_to:
            raise ValidationError("سنة البداية يجب أن تكون أصغر من أو تساوي سنة النهاية.")

        return cleaned_data


# ─────────────────────────────────────────────
#  6. فورم تحديث الملف الشخصي
# ─────────────────────────────────────────────
class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        label="الاسم الأول",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الاسم الأول',
            'id': 'id_profile_first_name',
        })
    )
    last_name = forms.CharField(
        max_length=50,
        label="اسم العائلة",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم العائلة',
            'id': 'id_profile_last_name',
        })
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'id': 'id_profile_email',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    # ── Validation ──
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # تجاهل البريد الحالي للمستخدم نفسه
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("هذا البريد الإلكتروني مستخدم من قِبل حساب آخر.")
        return email

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        if not name:
            raise ValidationError("الاسم الأول لا يمكن أن يكون فارغاً.")
        return name

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        if not name:
            raise ValidationError("اسم العائلة لا يمكن أن يكون فارغاً.")
        return name


# ─────────────────────────────────────────────
#  7. فورم تغيير كلمة المرور المخصص
# ─────────────────────────────────────────────
class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="كلمة المرور الحالية",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور الحالية',
            'id': 'id_old_password',
        })
    )
    new_password1 = forms.CharField(
        label="كلمة المرور الجديدة",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '8 أحرف على الأقل',
            'id': 'id_new_password1',
        })
    )
    new_password2 = forms.CharField(
        label="تأكيد كلمة المرور الجديدة",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور الجديدة',
            'id': 'id_new_password2',
        })
    )

    # ── Validation ──
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise ValidationError("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
        if password.isdigit():
            raise ValidationError("كلمة المرور لا يمكن أن تكون أرقاماً فقط.")
        if password.isalpha():
            raise ValidationError("كلمة المرور يجب أن تحتوي على أرقام أيضاً.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("كلمتا المرور غير متطابقتين.")
        return cleaned_data
