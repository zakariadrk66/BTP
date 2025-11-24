from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'articles', views.ArticleViewSet)
router.register(r'purchase-requests', views.PurchaseRequestViewSet, basename='purchaserequest')
router.register(r'quotations', views.QuotationViewSet)
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'goods-receipts', views.GoodsReceiptViewSet, basename='goodsreceipt')

urlpatterns = [
    path('', include(router.urls)),
]