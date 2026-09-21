from django.urls import path
from rest_framework.routers import SimpleRouter

from reviews_app.api.views import BaseInfoView, ReviewViewSet


router = SimpleRouter()
router.register('reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]
urlpatterns += router.urls
