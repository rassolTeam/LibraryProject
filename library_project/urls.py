from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from books import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login_view, name='accounts_login'),
    path('books/', include('books.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),

    # هذا هو الحل
    path('', RedirectView.as_view(url='/books/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)