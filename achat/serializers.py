from rest_framework import serializers
from .models import Supplier, Project
from .models import Article, PurchaseRequest
from .models import Quotation, PurchaseOrder
from .models import Invoice, GoodsReceipt


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        # Optional: Exclude auto-managed fields if you prefer
        # fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'rating']

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0.00 and 5.00.")
        return value


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        # Example of excluding audit fields from API (optional)
        # exclude = ['created_at', 'updated_at']

    def validate_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero.")
        return value
    
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

    def validate_reorderMax(self, value):
        if value < 1:
            raise serializers.ValidationError("Reorder max must be at least 1.")
        return value

    def validate_averageCost(self, value):
        if value < 0:
            raise serializers.ValidationError("Average cost cannot be negative.")
        return value


class PurchaseRequestSerializer(serializers.ModelSerializer):
    # Nested representation for reads
    item = ArticleSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    # Writable fields for POST/PUT (accept IDs)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        write_only=True,
        source='item',
        required=True
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True,
        source='project',
        required=True
    )

    class Meta:
        model = PurchaseRequest
        fields = '__all__'
        # Exclude auto-fields if desired, but we keep all for now

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero.")
        return value
    
class QuotationSerializer(serializers.ModelSerializer):
    # Nested read
    purchase_request = PurchaseRequestSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)

    # Writable ID fields
    purchase_request_id = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseRequest.objects.all(),
        write_only=True,
        source='purchase_request',
        required=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        write_only=True,
        source='supplier',
        required=True
    )
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        write_only=True,
        source='article',
        required=True
    )

    class Meta:
        model = Quotation
        fields = '__all__'
        # Exclude auto-fields like 'created_at' if desired, but we keep all for now

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value

    def validate_quantity_offered(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity offered must be at least 1.")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    # Nested read
    purchase_request = PurchaseRequestSerializer(read_only=True)
    selected_quotation = QuotationSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)

    # Writable ID fields
    purchase_request_id = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseRequest.objects.all(),
        write_only=True,
        source='purchase_request',
        required=True
    )
    selected_quotation_id = serializers.PrimaryKeyRelatedField(
        queryset=Quotation.objects.all(),
        write_only=True,
        source='selected_quotation',
        required=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        write_only=True,
        source='supplier',
        required=True
    )
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        write_only=True,
        source='article',
        required=True
    )

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['order_number', 'total_amount', 'order_date']

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value

    def validate_quantity_ordered(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity ordered must be at least 1.")
        return value
    
class InvoiceSerializer(serializers.ModelSerializer):
    # Nested read
    purchase_order = PurchaseOrderSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)

    # Writable ID fields
    purchase_order_id = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrder.objects.all(),
        write_only=True,
        source='purchase_order',
        required=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        write_only=True,
        source='supplier',
        required=True
    )
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        write_only=True,
        source='article',
        required=True
    )

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['total_amount', 'created_at']

    def validate_quantity_invoiced(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity invoiced must be at least 1.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value

    def validate(self, data):
        issue_date = data.get('issue_date')
        due_date = data.get('due_date')
        if issue_date and due_date and due_date < issue_date:
            raise serializers.ValidationError("Due date cannot be before issue date.")
        return data


class GoodsReceiptSerializer(serializers.ModelSerializer):
    # Nested read
    purchase_order = PurchaseOrderSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)

    # Writable ID fields
    purchase_order_id = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrder.objects.all(),
        write_only=True,
        source='purchase_order',
        required=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        write_only=True,
        source='supplier',
        required=True
    )
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        write_only=True,
        source='article',
        required=True
    )

    class Meta:
        model = GoodsReceipt
        fields = '__all__'
        read_only_fields = ['receipt_number', 'quantity_ordered', 'delivery_date', 'created_at']

    def validate_quantity_received(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity received cannot be negative.")
        return value