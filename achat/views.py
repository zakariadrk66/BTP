# BTP/achat/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Supplier, Project, Article, PurchaseRequest, Quotation, PurchaseOrder, Invoice, GoodsReceipt
from .serializers import (
    SupplierSerializer, ProjectSerializer, ArticleSerializer, PurchaseRequestSerializer,
    QuotationSerializer, PurchaseOrderSerializer, InvoiceSerializer, GoodsReceiptSerializer
)

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        purchase_request = self.get_object()
        try:
            purchase_request.approve_request()  # Call the model method
            return Response(
                {'status': 'Purchase request approved successfully'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def flag_for_review(self, request, pk=None):
        purchase_request = self.get_object()
        purchase_request.flag_for_review()  # Call the model method
        return Response(
            {'status': 'Purchase request flagged for review'},
            status=status.HTTP_200_OK
        )

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def send_order(self, request, pk=None):
        purchase_order = self.get_object()
        try:
            purchase_order.send_order()  # Call the model method
            return Response(
                {'status': 'Purchase order sent successfully'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def validate_invoice(self, request, pk=None):
        invoice = self.get_object()
        try:
            invoice.validate_invoice()  # Call the model method
            return Response(
                {'status': 'Invoice validated successfully'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class GoodsReceiptViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def validate_delivery(self, request, pk=None):
        goods_receipt = self.get_object()
        goods_receipt.validate_delivery()  # Call the model method
        return Response(
            {'status': 'Delivery validated successfully'},
            status=status.HTTP_200_OK
        )
