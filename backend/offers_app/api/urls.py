from django.urls import path
from rest_framework.routers import SimpleRouter

from offers_app.api.views import OfferDetailView, OfferViewSet


router = SimpleRouter()
router.register('offers', OfferViewSet, basename='offers')

urlpatterns = [
    path(
        'offerdetails/<int:pk>/',
        OfferDetailView.as_view(),
        name='offer-detail',
    ),
]
urlpatterns += router.urls
