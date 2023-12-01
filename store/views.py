from utils import custom_response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from .models import Cart, CartItem, Order, OrderItem, Payment, ShippingAddress
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, \
    PaymentSerializer, AddressSerializer


class CartListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = CartSerializer

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()

                return custom_response(serializer.data, "Cart created successfully", status.HTTP_201_CREATED, 'success')
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, 'error')

        except Exception as e:
            data = {
                "error_message": f"An error occurred while creating cart: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class CartItemListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = CartItemSerializer

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                product = serializer.validated_data['product']
                quantity = serializer.validated_data['quantity']

                if quantity > product.quantity:

                    return custom_response(serializer.data, "Not enough quantity available",
                                           status.HTTP_400_BAD_REQUEST,
                                           "error")
                serializer.save()
                return custom_response(serializer.data, "CartItem created successfully", status.HTTP_201_CREATED,
                                       "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST,
                                   "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while creating cart item: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   "error")


class CartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            serializer = CartSerializer(cart)

            item_details = CartItemSerializer(cart.cartitem_set.all(), many=True)
            serializer.data["item_details"] = item_details

            return custom_response(serializer.data, "cart retrieved successfully", status.HTTP_201_CREATED, "success")

        except Cart.DoesNotExist:
            return custom_response({}, "Cart not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving cart: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   "error")

    def put(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            serializer = CartSerializer(cart, data=request.data)
            if serializer.is_valid():
                serializer.save()

                total_items = cart.total_quantity()
                total_cost = cart.calculate_total()
                serializer.data["total_items"] = total_items
                serializer.data["total_cost"] = total_cost

                return custom_response(serializer.data, "Cart updated successfully", status.HTTP_201_CREATED,
                                       "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Cart.DoesNotExist:
            return custom_response({}, "Cart not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating cart: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   "error")

    def delete(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            cart.delete()

            return custom_response({}, "cart deleted successfully", status.HTTP_200_OK, "success")

        except Cart.DoesNotExist:
            return custom_response({}, "Cart not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while deleting cart: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get(self, request, cart_item_id):
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            serializer = CartItemSerializer(cart_item)

            return custom_response(serializer.data, "cartItem retrieved successfully",
                                   status.HTTP_201_CREATED, "success")

        except CartItem.DoesNotExist:
            return custom_response({}, "CartItem not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving cartItem: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def put(self, request, cart_item_id):
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            serializer = CartItemSerializer(cart_item, data=request.data)
            if serializer.is_valid():

                product = serializer.validated_data['product']
                quantity = serializer.validated_data['quantity']

                if quantity > product.quantity:
                    return custom_response({}, "Not enough quantity available", status.HTTP_400_BAD_REQUEST)

                serializer.save()
                return custom_response(serializer.data, "CartItem updated successfully", status.HTTP_200_OK)
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST)

        except CartItem.DoesNotExist:
            return custom_response({}, "CartItem not found", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving cartItem: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class OrderListView(APIView):
    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_classes = OrderSerializer

    def get(self, request):
        try:
            if not request.user.is_staff:
                orders = Order.objects.filter(user=request.user)
            else:
                orders = Order.objects.all()

            serializer = OrderSerializer(orders, many=True)

            for order_data in serializer.data:
                order_id = order_data['id']
                order_items = OrderItem.objects.filter(order=order_id)
                order_item_serializer = OrderItemSerializer(order_items, many=True)
                order_data['item_details'] = order_item_serializer.data

            return custom_response(serializer.data, "Order details retrieved successfully",
                                   status.HTTP_200_OK, "success")
        except Order.DoesNotExist:
            return custom_response({}, "Orders not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving Order List: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def post(self, request):
        try:
            status_filter = request.query_params.get('status')
            if status_filter:
                orders = Order.objects.filter(status=status_filter)
            else:
                orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)

            for order_data in serializer.data:
                order_id = order_data['id']
                order_items = OrderItem.objects.filter(order=order_id)
                order_item_serializer = OrderItemSerializer(order_items, many=True)
                order_data['item_details'] = order_item_serializer.data

            return custom_response(serializer.data, "Filtered orders retrieved successfully",
                                   status.HTTP_200_OK, "success")

        except Order.DoesNotExist:
            return custom_response({}, "Orders not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving filtered Order List: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class OrderItemList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = OrderItemSerializer(data=request.data)
            if serializer.is_valid():
                order_item = serializer.save()

                order = order_item.order
                order_total = order.calculate_order_total()
                order.payment.amount = order_total
                order.payment.save()

                return custom_response(serializer.data, "OrderItem created successfully",
                                       status.HTTP_201_CREATED, "success")

            product_quantity = serializer.validated_data['product'].quantity
            requested_quantity = serializer.validated_data['quantity']
            if requested_quantity > product_quantity:
                return custom_response({}, "Not enough quantity available", status.HTTP_400_BAD_REQUEST, "error")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while creating order item: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = OrderSerializer

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderSerializer(order)

            item_details = OrderItemSerializer(order.orderitem_set.all(), many=True)
            serializer.data["item_details"] = item_details

            return custom_response(serializer.data, "Order retrieved successfully", status.HTTP_200_OK, "success")
        except Order.DoesNotExist:
            return custom_response({}, "Order not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error _message": f"An error occurred while retrieving order: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def put(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderSerializer(order, data=request.data)
            if serializer.is_valid():
                serializer.save()

                item_details = OrderItemSerializer(order.orderitem_set.all(), many=True).data
                serializer.data["item_details"] = item_details

                return custom_response(serializer.data, "Order updated successfully", status.HTTP_200_OK, "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Order.DoesNotExist:
            return custom_response({}, "Order not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error _message": f"An error occurred while updating order: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.delete()
            return custom_response({}, "Order deleted successfully", status.HTTP_204_NO_CONTENT, "success")
        except Order.DoesNotExist:
            return custom_response({}, "Order not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while deleting order: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class OrderItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = OrderItemSerializer

    def get(self, request, order_item_id):
        try:
            order_item = OrderItem.objects.get(id=order_item_id, order__user=request.user)
            serializer = OrderItemSerializer(order_item)
            return custom_response(serializer.data, "OrderItem retrieved successfully", status.HTTP_200_OK, "success")
        except OrderItem.DoesNotExist:
            return custom_response({}, "OrderItem not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving OrderItem: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def put(self, request, order_item_id):
        try:
            order_item = OrderItem.objects.get(id=order_item_id, order__user=request.user)
            serializer = OrderItemSerializer(order_item, data=request.data)
            if serializer.is_valid():
                serializer.save()

                order = order_item.order
                order_total = order.calculate_order_total()
                order.payment.amount = order_total
                order.payment.save()
                return custom_response(serializer.data, "OrderItem updated successfully", status.HTTP_200_OK, "success")
        except OrderItem.DoesNotExist:
            return custom_response({}, "OrderItem not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating OrderItem: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = PaymentSerializer

    def post(self, request):
        try:
            serializer = PaymentSerializer(data={**request.data, 'user': request.user.id})
            if serializer.is_valid():
                order_id = serializer.validated_data['order'].id
                order = Order.objects.get(id=order_id, user=request.user)
                serializer.save(order=order)
                return custom_response(serializer.data, "Payment created successfully",
                                       status.HTTP_201_CREATED, "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while creating payment: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, order__user=request.user)
            serializer = PaymentSerializer(payment)
            return custom_response(serializer.data, "Payment details retrieved successfully", status.HTTP_200_OK,
                                   "success")
        except Payment.DoesNotExist:
            return custom_response({}, "Payment not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving payment details: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def put(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            serializer = PaymentSerializer(payment, data={**request.data, 'user': request.user.id})
            if serializer.is_valid():
                serializer.save()
                return custom_response(serializer.data, "Payment updated successfully", status.HTTP_200_OK, "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Payment.DoesNotExist:
            return custom_response({}, "Payment not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating payment: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def delete(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            payment.delete()
            return custom_response({}, "Payment canceled successfully", status.HTTP_204_NO_CONTENT, "success")
        except Payment.DoesNotExist:
            return custom_response({}, "Payment not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while deleting payment: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get(self, request, address_id):
        try:
            address = ShippingAddress.objects.get(id=address_id, order__user=request.user)
            serializer = AddressSerializer(address)
            return custom_response(serializer.data, "Shipping address details retrieved succeesfully",
                                   status.HTTP_200_OK, "success")
        except ShippingAddress.DoesNotExist:
            return custom_response({}, "Shipping address not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving address: {str(e)}",
            }
        return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def put(self, request, address_id):
        try:
            address = ShippingAddress.objects.get(id=address_id, user=request.user)
            serializer = AddressSerializer(address, data={**request.data, 'user': request.user.id})
            if serializer.is_valid():
                serializer.save()
                return custom_response(serializer.data, "Shipping address updated successfully", status.HTTP_200_OK,
                                       "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except ShippingAddress.DoesNotExist:
            return custom_response({}, "Shipping address not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while updating shipping address: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    def delete(self, request, address_id):
        try:
            address = ShippingAddress.objects.get(id=address_id, user=request.user)
            address.delete()
            return custom_response({}, "Shipping address removed successfully", status.HTTP_204_NO_CONTENT, "success")
        except ShippingAddress.DoesNotExist:
            return custom_response({}, "Shipping address not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while deleting shipping address: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class AddressView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def post(self, request):
        try:
            serializer = AddressSerializer(data={**request.data, 'user': request.user.id})
            if serializer.is_valid():
                order_id = serializer.validated_data['order'].id
                order = Order.objects.get(id=order_id, user=request.user)
                serializer.save(order=order)
                return custom_response(serializer.data, "Shipping address created successfully",
                                       status.HTTP_201_CREATED, "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while creating shipping address: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")
