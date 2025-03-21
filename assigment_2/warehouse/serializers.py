from rest_framework import serializers
from .models import Item, PurchaseHeader, PurchaseDetail, SellHeader, SellDetail

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['code', 'name', 'unit', 'description', 'stock', 'balance']
        read_only_fields = ['stock', 'balance']

class PurchaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item', 'quantity', 'unit_price', 'remaining_quantity']
        read_only_fields = ['remaining_quantity']

class PurchaseHeaderSerializer(serializers.ModelSerializer):
    details = PurchaseDetailSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseHeader
        fields = ['code', 'date', 'description', 'details']

class SellDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellDetail
        fields = ['id', 'item', 'quantity']

class SellHeaderSerializer(serializers.ModelSerializer):
    details = SellDetailSerializer(many=True, read_only=True)

    class Meta:
        model = SellHeader
        fields = ['code', 'date', 'description', 'details']