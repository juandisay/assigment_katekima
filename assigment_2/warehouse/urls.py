from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('items', views.ItemViewSet)
router.register('purchase', views.PurchaseHeaderViewSet)
router.register('sell', views.SellHeaderViewSet)
router.register('report', views.Report, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]