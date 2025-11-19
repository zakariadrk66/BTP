from django.db import models
from authentication.models import CustomUser

class Supplier(models.Model):
    supplierID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    reliabilityIndex = models.FloatField(default=0.0)

    def __str__(self):
        return self.name


class project(models.Model):
    projectID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=25, decimal_places=2)

    def __str__(self):
        return self.name

class PurchaseRequest(models.Model):
    requestID = models.AutoField(primary_key=True)
    item = models.CharField(max_length=255)
    quantity = models.IntegerField()
    chantierRef = models.CharField(max_length=255)
    urgency = models.CharField(max_length=50)
    budget = models.FloatField()
    requester = models.CharField(max_length=255)


class PurchaseOrder(models.Model):
    poNumber = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    projectID = models.ForeignKey(project, on_delete=models.CASCADE)
    totalCost = models.FloatField()
    status = models.CharField(max_length=50, default='Pending Approval')

class Invoice(models.Model):
    invoiceID = models.AutoField(primary_key=True)
    poReference = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    amount = models.FloatField()
    status = models.CharField(max_length=50, default='pending')

class GoodsReceipt(models.Model):
    grnID = models.AutoField(primary_key=True)
    poReference = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    receivedQuantity = models.IntegerField()
    dateReceived = models.DateField()

class Article(models.Model):
    articleSKU = models.CharField(max_length=255, primary_key=True)
    description = models.TextField()
    reorderMax = models.IntegerField(default=0)
    averageCost = models.FloatField(default=0.0)
    
    def __str__(self):
        return self.description

class Quotation(models.Model):
    quotationID = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    price = models.FloatField()
    deliveryTime = models.DateField()
    validity = models.DateField()

class Warehouse(models.Model):
    warehouseID = models.AutoField(primary_key=True)
    location = models.CharField(max_length=255)
    

    def __str__(self):
        return self.location
