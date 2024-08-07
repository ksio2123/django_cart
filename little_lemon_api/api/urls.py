
# from django.urls import path, include
from django.urls import path, include
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<str:pk>', views.removeManager),
    path('groups/delivery-crew/users', views.deliveryCrews),
    path('groups/delivery-crew/users/<str:pk>', views.removeDeliveryCrew),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.OrderDetailView.as_view()),
    path('', include('djoser.urls')),
]
