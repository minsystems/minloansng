"""minloansng URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView

from accounts.views import LoginView, RegisterView

urlpatterns = [
    re_path(r'^accounts/$', RedirectView.as_view(url='/account')),
    re_path(r'^account/', include(("accounts.urls", 'accounts-url'), namespace='account')),
    re_path(r'^accounts/', include(("accounts.passwords.urls", 'accounts-password-url'), namespace='account-password')),
    path('dashboard/', include(('company.urls', 'company-url'), namespace='company-url')),
    path('loans/', include(('loans.urls', 'loans-url'), namespace='loans-url')),
    path('borrowers/', include(('borrowers.urls', 'borrowers-url'), namespace='borrowers-url')),
    path('system/handler/', include(('mincore.urls', 'mincore-url'), namespace='mincore-url')),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', TemplateView.as_view(template_name='index.html'), name='homepage'),
    path('page-not-found/', TemplateView.as_view(template_name='404_.html'), name='404_'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)),] + urlpatterns
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
