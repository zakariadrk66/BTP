from django.db import models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Supplier(models.Model):
    """
    Represents a vendor or supplier who provides quotations and delivers goods.
    """
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.00,
        help_text="Average rating from 0.00 to 5.00"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']


class Project(models.Model):
    """
    Represents a business project with a defined budget and description.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']

class Article(models.Model):
    """
    Represents an inventory item or product that can be requested, quoted, ordered, and received.
    """
    articleSKU = models.CharField(
        max_length=50,
        unique=True,
        help_text="Stock Keeping Unit - unique identifier for this item"
    )
    description = models.TextField(blank=True)
    reorderMax = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Maximum stock level before reordering is suggested"
    )
    averageCost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        default=0.00,
        help_text="Average historical cost per unit"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.articleSKU} - {self.description[:30]}..."

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['articleSKU']

class PurchaseRequest(models.Model):
    """
    Represents a formal request to purchase an article for a specific project.
    Can be approved, flagged for review, or rejected.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for Review'),
    ]

    requestID = models.AutoField(primary_key=True)
    item = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='purchase_requests')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    chantierRef = models.CharField(max_length=100, blank=True, help_text="Reference to construction site or department")
    urgency = models.CharField(max_length=20, default='normal', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ])
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        help_text="Estimated cost for this request"
    )
    requester = models.CharField(max_length=255, help_text="Name of person requesting")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchase_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve_request(self):
        """Approve this purchase request."""
        if self.status == 'pending':
            self.status = 'approved'
            self.save()
            # Optional: trigger notification, create quotation, etc.
        else:
            raise ValueError("Cannot approve request: status is not 'pending'.")

    def flag_for_review(self):
        """Flag this request for further review."""
        self.status = 'flagged'
        self.save()

    def __str__(self):
        return f"PR#{self.requestID} - {self.item.articleSKU} ({self.quantity})"

    class Meta:
        verbose_name = "Purchase Request"
        verbose_name_plural = "Purchase Requests"
        ordering = ['-created_at']

class Quotation(models.Model):
    """
    A price offer from a supplier for a specific article in response to a purchase request.
    Multiple quotations may exist per purchase request from different suppliers.
    """
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='quotations'
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    quantity_offered = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity the supplier is willing to provide at this price"
    )
    validity_date = models.DateField(
        help_text="Last date this quotation is valid"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quotation from {self.supplier.name} for PR#{self.purchase_request.requestID}"

    class Meta:
        verbose_name = "Quotation"
        verbose_name_plural = "Quotations"
        ordering = ['-created_at']
        # Ensure one supplier doesn't submit duplicate quotations for the same PR/article
        unique_together = ('purchase_request', 'supplier', 'article')


class PurchaseOrder(models.Model):
    """
    A formal order sent to a supplier based on an approved purchase request and selected quotation.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    selected_quotation = models.ForeignKey(
        Quotation,
        on_delete=models.PROTECT,  # Prevent deletion if order exists
        related_name='purchase_orders'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    quantity_ordered = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        help_text="Auto-calculated: quantity × unit price"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)

    def send_order(self):
        """Send the purchase order to the supplier and update status."""
        if self.status == 'draft':
            self.status = 'sent'
            self.save()
            # Optional: trigger email to supplier, log action, etc.
        else:
            raise ValueError("Cannot send order: status is not 'draft'.")

    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        self.total_amount = self.quantity_ordered * self.unit_price
        # Auto-generate order number if not set (simple example)
        if not self.order_number:
            self.order_number = f"PO{self.pk or 0}"
            # Note: Final number generation may require post-save hook
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PO {self.order_number} - {self.article.articleSKU}"

    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ['-order_date']

class Invoice(models.Model):
    """
    Represents a supplier invoice linked to a purchase order.
    Requires validation before payment processing.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('validated', 'Validated'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    invoice_number = models.CharField(max_length=100, unique=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    quantity_invoiced = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        help_text="Auto-calculated: quantity × unit price"
    )
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def validate_invoice(self):
        """Validate the invoice and update status."""
        if self.status in ['draft', 'submitted']:
            self.status = 'validated'
            self.save()
            # Optional: trigger accounting workflow, payment scheduling
        else:
            raise ValueError("Cannot validate invoice: status not 'draft' or 'submitted'.")

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity_invoiced * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.supplier.name}"

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-issue_date']


class GoodsReceipt(models.Model):
    """
    Confirms physical receipt of goods against a purchase order.
    Validates delivery and may update inventory.
    """
    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Delivered'),
        ('complete', 'Fully Delivered'),
        ('rejected', 'Delivery Rejected'),
    ]

    receipt_number = models.CharField(max_length=100, unique=True, editable=False)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='goods_receipts'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='goods_receipts'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='goods_receipts'
    )
    quantity_received = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Actual quantity received (may be less than ordered)"
    )
    quantity_ordered = models.IntegerField(editable=False)
    delivery_date = models.DateField(auto_now_add=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def validate_delivery(self):
        """Confirm delivery and update status based on quantity received."""
        if self.quantity_received == 0:
            self.delivery_status = 'rejected'
        elif self.quantity_received < self.quantity_ordered:
            self.delivery_status = 'partial'
        else:
            self.delivery_status = 'complete'
        self.save()
        # Optional: update warehouse inventory, notify accounting

    def save(self, *args, **kwargs):
        # Capture quantity ordered at time of receipt creation
        if not self.pk and self.purchase_order:
            self.quantity_ordered = self.purchase_order.quantity_ordered
        # Simple receipt number (can be enhanced later)
        if not self.receipt_number:
            self.receipt_number = f"GR{self.pk or 0}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.article.articleSKU}"

    class Meta:
        verbose_name = "Goods Receipt"
        verbose_name_plural = "Goods Receipts"
        ordering = ['-delivery_date']