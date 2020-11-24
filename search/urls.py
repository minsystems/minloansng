from django.urls import path

from search.views import SearchSystemView

urlpatterns = [
    path('<slug:slug>/', SearchSystemView.as_view(), name='query'),
]