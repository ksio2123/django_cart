import decimal
from email import message
from modulefinder import ReplacePackage
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission

# Create your views here.
from rest_framework import generics
from rest_framework.views import APIView
from .models import Cart, MenuItem, Category, Order, OrderItem
from .serializers import CartSerializer, MenuItemSerializer, CategorySerializer, OrderItemSerializer, OrderSerializer, UserSerializer

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists()

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return [IsAuthenticated()]
        return [IsManager()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        if (self.request.method == 'GET'):
            return [IsAuthenticated()]
        return [IsManager()]

# should only be for customers
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userId = request.user.id
        cart = Cart.objects.filter(user = userId)
        return Response(CartSerializer(cart, many=True).data)

    def post(self, request):
        menu_item = request.data['menu_item']
        menu_item = get_object_or_404(MenuItem, id=menu_item)
        cart = {}
        cart['menu_item'] = menu_item.id
        cart['unit_price'] = menu_item.price
        quantity = request.data['quantity']
        cart['quantity'] = quantity
        cart['user'] = request.user.id
        cart['price'] = menu_item.price * quantity
        cart = CartSerializer(data=cart)
        if (cart.is_valid()):
            cart.save()
            return Response(cart.data)
        return Response(cart.errors)

    def delete(self, request):
        userId = request.user.id
        Cart.objects.filter(user = userId).delete()
        return Response({"message":"ok"})

@api_view(['POST', 'GET'])
@permission_classes([IsManager])
def managers(request):
    if (request.method == 'POST'):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({"message": "ok"}, status.HTTP_201_CREATED)
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
    elif (request.method == 'GET'):
        users = User.objects.filter(groups__name = 'Manager')
        return Response(UserSerializer(users, many=True).data)

@api_view(['DELETE'])
@permission_classes([IsManager])
def removeManager(request, username):
    user = get_object_or_404(User, username=username)
    managers = Group.objects.get(name='Manager')
    managers.user_set.remove(user)
    return Response({"message": "ok"}, status.HTTP_200_OK)

@api_view(['POST', 'GET'])
@permission_classes([IsManager])
def deliveryCrews(request):
    if (request.method == 'POST'):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Delivery Crew')
            managers.user_set.add(user)
            return Response({"message": "ok"}, status.HTTP_201_CREATED)
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
    elif (request.method == 'GET'):
        users = User.objects.filter(groups__name = 'Delivery Crew')
        return Response(UserSerializer(users, many=True).data)

@api_view(['DELETE'])
@permission_classes([IsManager])
def removeDeliveryCrew(request, username):
    user = get_object_or_404(User, username=username)
    managers = Group.objects.get(name='Delivery Crew')
    managers.user_set.remove(user)
    return Response({"message": "ok"}, status.HTTP_200_OK)

class OrdersView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            orders = Order.objects.filter(delivery_crew = user.id)
        else:
            orders = Order.objects.filter(user = user.id)
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user = user.id)
        if (cart.exists()):
            order = Order(user = user, total = 0)
            order.save()
            total = decimal.Decimal('0')
            for cartItem in cart:
                total += cartItem.price
                #could validate before saving the data
                OrderItem(
                    order = order,
                    menu_item = cartItem.menu_item,
                    quantity = cartItem.quantity,
                    unit_price = cartItem.unit_price,
                    price = cartItem.price
                ).save()
            order.total = total
            order.save()
            cart.delete()
            return Response(OrderSerializer(order).data, status.HTTP_201_CREATED)
        return Response({'message': 'empty cart'})

class OrderDetailView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        order = get_object_or_404(Order, id = pk)
        if (not user.groups.filter(name='Manager')):
             if (order.user != user):
                return Response({'message': 'not your order'}, status.HTTP_401_UNAUTHORIZED)
        orderItems = OrderItem.objects.filter(order = order.id)
        response = {
            "order": OrderSerializer(order).data,
            "orderItems": OrderItemSerializer(orderItems, many=True).data
        }
        return Response(response)

    def delete(self, request, pk):
        user = request.user
        if (not user.groups.filter(name='Manager')):
            return Response({'message': 'not a manager'}, status.HTTP_401_UNAUTHORIZED)
        order = get_object_or_404(Order, id = pk)
        order.delete()
        return Response({'message': 'ok'}, status.HTTP_200_OK)

    #only manager or delivery_crew can update cart
    def put(self, request, pk):
        user = request.user
        order = get_object_or_404(Order, id = pk)
        if (user.groups.filter(name='Manager')):
            data = request.data
        elif (user.groups.filter(name='Delivery Crew')):
            data = {'status': request.data['status']}
        else:
            return Response({'message': 'Customer cannot update'}, status.HTTP_401_UNAUTHORIZED)
        serializer = OrderSerializer(order, data, partial=True)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)





