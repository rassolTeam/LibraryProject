from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from books import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login_view, name='accounts_login'),
    path('books/', include('books.urls')),

    # هذا هو الحل
    path('', RedirectView.as_view(url='/books/', permanent=False)),
]