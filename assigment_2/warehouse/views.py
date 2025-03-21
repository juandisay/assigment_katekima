from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Item, PurchaseHeader, PurchaseDetail, SellHeader, SellDetail
from .serializers import (
    ItemSerializer,
    PurchaseHeaderSerializer,
    PurchaseDetailSerializer,
    SellHeaderSerializer,
    SellDetailSerializer
)
from django.db.models import F, Sum
from django.utils.timezone import make_aware
from datetime import datetime
from decimal import Decimal


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = ItemSerializer
    lookup_field = 'code'

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class PurchaseHeaderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseHeader.objects.filter(is_deleted=False)
    serializer_class = PurchaseHeaderSerializer
    lookup_field = 'code'

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=['post'])
    def add_detail(self, request, code=None):
        header = self.get_object()
        serializer = PurchaseDetailSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(header=header)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def details(self, request, code=None):
        header = self.get_object()
        details = PurchaseDetail.objects.filter(header=header, is_deleted=False)
        serializer = PurchaseDetailSerializer(details, many=True)
        return Response(serializer.data)


class SellHeaderViewSet(viewsets.ModelViewSet):
    queryset = SellHeader.objects.filter(is_deleted=False)
    serializer_class = SellHeaderSerializer
    lookup_field = 'code'

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=['post'])
    def add_detail(self, request, code=None):
        header = self.get_object()
        serializer = SellDetailSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(header=header)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def details(self, request, code=None):
        header = self.get_object()
        details = SellDetail.objects.filter(header=header, is_deleted=False)
        serializer = SellDetailSerializer(details, many=True)
        return Response(serializer.data)


class Report(viewsets.ViewSet):
    lookup_field = 'code'

    def retrieve(self, request, code=None):
        try:
            item = get_object_or_404(Item, code=code, is_deleted=False)
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            if start_date:
                start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            # Get all purchase and sell details for the item with date filtering
            purchases = PurchaseDetail.objects.filter(
                item=item,
                is_deleted=False,
                header__date__range=(start_date, end_date) if start_date and end_date else (None, None)
            ).select_related('header')
            
            sells = SellDetail.objects.filter(
                item=item,
                is_deleted=False,
                header__date__range=(start_date, end_date) if start_date and end_date else (None, None)
            ).select_related('header')
            
            # Combine and sort all transactions by date
            transactions = []
            
            for purchase in purchases:
                transactions.append({
                    'date': purchase.header.date,
                    'description': purchase.header.description or '',
                    'code': purchase.header.code,
                    'type': 'purchase',
                    'quantity': purchase.quantity,
                    'unit_price': purchase.unit_price,
                    'remaining_quantity': purchase.remaining_quantity
                })
            
            for sell in sells:
                transactions.append({
                    'date': sell.header.date,
                    'description': sell.header.description or '',
                    'code': sell.header.code,
                    'type': 'sell',
                    'quantity': sell.quantity
                })
            
            # Sort transactions by date
            transactions.sort(key=lambda x: x['date'])
            
            # Process transactions to build the report
            result = []
            running_stock = []
            total_in_qty = Decimal('0')
            total_out_qty = Decimal('0')
            
            for trans in transactions:
                if trans['type'] == 'purchase':
                    # Handle purchase transaction
                    stock_entry = {
                        'quantity': trans['quantity'],
                        'price': trans['unit_price'],
                        'remaining': trans['remaining_quantity']
                    }
                    running_stock.append(stock_entry)
                    
                    # Calculate current stock quantities and totals
                    stock_qty = [entry['remaining'] for entry in running_stock]
                    stock_price = [entry['price'] for entry in running_stock]
                    stock_total = [qty * price for qty, price in zip(stock_qty, stock_price)]
                    
                    entry = {
                        'date': trans['date'].strftime('%d-%m-%Y'),
                        'description': trans['description'],
                        'code': trans['code'],
                        'in_qty': int(trans['quantity']),
                        'in_price': int(trans['unit_price']),
                        'in_total': int(trans['quantity'] * trans['unit_price']),
                        'out_qty': 0,
                        'out_price': 0,
                        'out_total': 0,
                        'stock_qty': [int(qty) for qty in stock_qty],
                        'stock_price': [int(price) for price in stock_price],
                        'stock_total': [int(total) for total in stock_total],
                        'balance_qty': int(sum(stock_qty)),
                        'balance': int(sum(stock_total))
                    }
                    
                    total_in_qty += trans['quantity']
                    
                else:  # sell transaction
                    out_qty = trans['quantity']
                    out_total = Decimal('0')
                    out_price = Decimal('0')
                    
                    # Process FIFO for selling
                    remaining_to_sell = out_qty
                    for stock in running_stock:
                        if remaining_to_sell <= 0:
                            break
                            
                        available = stock['remaining']
                        if available > 0:
                            sold = min(remaining_to_sell, available)
                            stock['remaining'] -= sold
                            out_total += sold * stock['price']
                            remaining_to_sell -= sold
                    
                    if out_qty > 0:
                        out_price = out_total / out_qty
                    
                    # Calculate current stock quantities and totals
                    stock_qty = [entry['remaining'] for entry in running_stock]
                    stock_price = [entry['price'] for entry in running_stock]
                    stock_total = [qty * price for qty, price in zip(stock_qty, stock_price)]
                    
                    entry = {
                        'date': trans['date'].strftime('%d-%m-%Y'),
                        'description': trans['description'],
                        'code': trans['code'],
                        'in_qty': 0,
                        'in_price': 0,
                        'in_total': 0,
                        'out_qty': int(out_qty),
                        'out_price': int(out_price),
                        'out_total': int(out_total),
                        'stock_qty': [int(qty) for qty in stock_qty],
                        'stock_price': [int(price) for price in stock_price],
                        'stock_total': [int(total) for total in stock_total],
                        'balance_qty': int(sum(stock_qty)),
                        'balance': int(sum(stock_total))
                    }
                    
                    total_out_qty += out_qty
                
                result.append(entry)
            
            response_data = {
                'result': {
                    'items': result,
                    'item_code': item.code,
                    'name': item.name,
                    'unit': item.unit,
                    'summary': {
                        'in_qty': int(total_in_qty),
                        'out_qty': int(total_out_qty),
                        'balance_qty': int(total_in_qty - total_out_qty),
                        'balance': int(sum(entry['remaining'] * entry['price'] for entry in running_stock))
                    }
                }
            }

            return Response(response_data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
