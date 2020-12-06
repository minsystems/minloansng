from django.urls import path

from minmarkets.views import WelcomeView, StoreHomepage

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('products/', StoreHomepage.as_view(), name='homepage'),
]
