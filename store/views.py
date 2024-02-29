from utils import custom_response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .payment import initiate_payment
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from .models import Cart, CartItem, Order, OrderItem, Payment, ShippingAddress, CouponCode
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, \
    PaymentSerializer, AddressSerializer, CouponCodeSerializer


class IsOrderOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


@extend_schema(
    summary="Create and Retrieve User Carts",
    description="API endpoint for creating and retrieving user carts. Requires user authentication.",
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(description="Cart created successfully"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
        status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
    }
)
class CartListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    @extend_schema(
        summary="Create a New Cart",
        description="Handle POST requests to create a new cart for the user.",
        request=CartSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Cart created successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return custom_response(serializer.data, "Cart created successfully", status.HTTP_201_CREATED, 'success')
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, 'error')
        except Exception as e:
            data = {"error_message": f"An error occurred while creating cart: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


@extend_schema(
    summary="Manage Cart Items",
    description="API endpoint for managing cart items. Requires user authentication.",
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(description="CartItem created successfully"),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data or not enough quantity available"),
        status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
    }
)
class CartItemListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    @extend_schema(
        summary="Add a New Item to the Cart",
        description="Handle POST requests to add a new item to the cart.",
        request=CartItemSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="CartItem created successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data or not enough quantity available"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
                return custom_response(serializer.data, "CartItem created successfully", status.HTTP_201_CREATED,
                                       "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {"error_message": f"An error occurred while creating cart item: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class CartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    @extend_schema(
        summary="Retrieve Cart Details",
        description="API endpoint for retrieving user carts. Requires user authentication.",
        parameters=[OpenApiParameter(name="cart_id", description="ID of the cart to retrieve", required=True)],
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Cart retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Cart not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def get(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            data = self.get_cart_details(cart)
            return custom_response(data, "Cart retrieved successfully", status.HTTP_201_CREATED, "success")

        except Cart.DoesNotExist:
            return custom_response({}, "Cart not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while retrieving cart: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    @extend_schema(
        summary="Update Cart",
        description="API endpoint for updating user carts. Requires user authentication.",
        parameters=[OpenApiParameter(name="cart_id", description="ID of the cart to update", required=True)],
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Cart updated successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Cart not found"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
                return custom_response(serializer.data, "Cart updated successfully", status.HTTP_201_CREATED, "success")
            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")

        except Cart.DoesNotExist:
            return custom_response({}, "Cart not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while updating cart: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    @extend_schema(
        summary="Delete Cart",
        description="API endpoint for deleting user carts. Requires user authentication.",
        parameters=[OpenApiParameter(name="cart_id", description="ID of the cart to delete", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Cart deleted successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Cart not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def delete(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            cart.delete()
            return custom_response({}, "Cart deleted successfully", status.HTTP_200_OK, "success")

        except Cart.DoesNotExist:
            return custom_response({}, "Cart not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while deleting cart: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    @extend_schema(
        summary="Retrieve Cart Item",
        description="API endpoint for retrieving individual cart items. Requires user authentication and ownership of "
                    "the cart item.",
        parameters=[OpenApiParameter(name="cart_item_id", description="ID of the cart item to retrieve",
                                     required=True)],
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="CartItem retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="CartItem not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def get(self, request, cart_item_id):
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            serializer = CartItemSerializer(cart_item)
            return custom_response(serializer.data, "CartItem retrieved successfully", status.HTTP_201_CREATED,
                                   "success")

        except CartItem.DoesNotExist:
            return custom_response({}, "CartItem not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while retrieving cartItem: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    @extend_schema(
        summary="Update Cart Item",
        description="API endpoint for updating individual cart items. Requires user authentication and ownership of "
                    "the cart item.",
        parameters=[OpenApiParameter(name="cart_item_id", description="ID of the cart item to update", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="CartItem updated successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data or not enough quantity available"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="CartItem not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
                return custom_response(serializer.data, "CartItem updated successfully", status.HTTP_200_OK, "success")

            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")

        except CartItem.DoesNotExist:
            return custom_response({}, "CartItem not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while updating cartItem: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class OrderListView(APIView):
    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = OrderSerializer

    class OrderListPagination(PageNumberPagination):
        page_size = 8

    pagination_class = OrderListPagination

    @extend_schema(
        summary="Get Orders",
        description="API endpoint for retrieving user new orders. Requires user authentication and admin privileges "
                    "for listing all orders.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="List of orders"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Orders not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    @action(detail=False, methods=['get'])
    def get_orders(self, request):
        try:
            if not request.user.is_staff:
                orders = Order.objects.filter(user=request.user)
            else:
                orders = Order.objects.all()

            page = self.paginate_queryset(orders)
            if page is not None:
                serializer = OrderSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = OrderSerializer(orders, many=True)
            return custom_response(serializer.data, status.HTTP_200_OK, 'success')

        except Order.DoesNotExist:
            return custom_response({}, "Orders not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while retrieving Order List: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    @extend_schema(
        summary="Create Order",
        description="API endpoint for creating new orders. Requires user authentication and admin privileges for "
                    "listing all orders.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Filtered orders retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Orders not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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

            return custom_response(serializer.data, "Filtered orders retrieved successfully", status.HTTP_200_OK,
                                   "success")

        except Order.DoesNotExist:
            return custom_response({}, "Orders not found", status.HTTP_404_NOT_FOUND, "error")

        except Exception as e:
            data = {"error_message": f"An error occurred while retrieving filtered Order List: {str(e)}"}
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class OrderItemList(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add Order Item",
        description="API endpoint for adding a new item to an order. Requires user authentication.",
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="OrderItem created successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data or not enough quantity available"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
    permission_classes = [IsAuthenticated, IsOrderOwner]
    serializer_classes = OrderSerializer

    @staticmethod
    def get_order_details(order):
        serializer = OrderSerializer(order)
        item_details = OrderItemSerializer(order.orderitem_set.all(), many=True)
        serializer.data["item_details"] = item_details.data
        return serializer.data

    @extend_schema(
        summary="Retrieve Order",
        description="API endpoint for retrieving. Requires user authentication "
                    "and ownership of the order.",
        parameters=[OpenApiParameter(name="order_id", description="ID of the order to retrieve", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Order retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Order not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            data = self.get_order_details(order)
            return custom_response(data, "Order retrieved successfully", status.HTTP_200_OK, "success")
        except Order.DoesNotExist:
            return custom_response({}, "Order not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving order: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    @extend_schema(
        summary="Update Order",
        description="API endpoint for retrieving, updating, and deleting user orders. Requires user authentication "
                    "and ownership of the order.",
        parameters=[OpenApiParameter(name="order_id", description="ID of the order to update", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Order updated successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Order not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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

    @extend_schema(
        summary="Remove Order",
        description="API endpoint for deleting user orders. Requires user authentication "
                    "and ownership of the order.",
        parameters=[OpenApiParameter(name="order_id", description="ID of the order to retrieve", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Order deleted successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Order not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
    permission_classes = [IsAuthenticated, IsOrderOwner]
    serializer_classes = OrderItemSerializer

    @extend_schema(
        summary="Retrieve Order Item",
        description="API endpoint for managing individual items within an order. Requires user authentication and "
                    "ownership of the order item.",
        parameters=[
            OpenApiParameter(name="order_item_id", description="ID of the order item to retrieve", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OrderItem retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="OrderItem not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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

    @extend_schema(
        summary="Update Order Item",
        description="API endpoint for managing individual items within an order. Requires user authentication and "
                    "ownership of the order item.",
        parameters=[
            OpenApiParameter(name="order_item_id", description="ID of the order item to update", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OrderItem updated successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="OrderItem not found"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
    serializer_class = PaymentSerializer

    @extend_schema(
        summary="Create Payment",
        description="API endpoint for managing payments associated with orders. Requires user authentication.",
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Payment created successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data or failed to initiate payment"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def post(self, request):
        try:
            serializer = PaymentSerializer(data={**request.data, 'user': request.user.id})
            if serializer.is_valid():
                order_id = serializer.validated_data['order'].id
                order = Order.objects.get(id=order_id, user=request.user)
                serializer.save(order=order)

                amount = serializer.validated_data['amount']
                email = serializer.validated_data['user'].email
                redirect_url = "https://your-redirect-url.com"
                flutterwave_response = initiate_payment(amount, email, redirect_url)

                if 'status' in flutterwave_response and flutterwave_response['status'] == 'success':
                    return custom_response(serializer.data, "Payment created successfully",
                                           status.HTTP_201_CREATED, "success")
                else:
                    return custom_response(flutterwave_response, "Failed to initiate payment",
                                           status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

            return custom_response(serializer.errors, "Invalid data", status.HTTP_400_BAD_REQUEST, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while creating payment: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = PaymentSerializer

    @extend_schema(
        summary="Retrieve Payment",
        description="API endpoint for retrieving payment details. Requires user authentication.",
        parameters=[OpenApiParameter(name="payment_id", description="ID of the payment to retrieve", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Payment details retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Payment not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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

    @extend_schema(
        summary="Update Payment",
        description="API endpoint for updating. Requires user authentication.",
        parameters=[OpenApiParameter(name="payment_id", description="ID of the payment to update", required=True)],
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Payment updated successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Payment not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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

    @extend_schema(
        summary="Delete Payment",
        description="API endpoint for deleting payment details. Requires user authentication.",
        parameters=[OpenApiParameter(name="payment_id", description="ID of the payment to delete", required=True)],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Payment canceled successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Payment not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
    serializer_classes = AddressSerializer

    @extend_schema(
        summary="Retrieve Shipping Address",
        description="API endpoint for retrieving address details. Requires user authentication.",
        parameters=[OpenApiParameter(name="address_id", description="ID of the shipping address to retrieve",
                                     required=True)],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Shipping Address details retrieved successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Shipping Address not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def get(self, request, address_id):
        try:
            address = ShippingAddress.objects.get(id=address_id, order__user=request.user)
            serializer = AddressSerializer(address)
            return custom_response(serializer.data, "Shipping address details retrieved successfully",
                                   status.HTTP_200_OK, "success")
        except ShippingAddress.DoesNotExist:
            return custom_response({}, "Shipping address not found", status.HTTP_404_NOT_FOUND, "error")
        except Exception as e:
            data = {
                "error_message": f"An error occurred while retrieving address: {str(e)}",
            }
        return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")

    @extend_schema(
        summary="Update Shipping Address",
        description="API endpoint for updating address details. Requires user authentication.",
        parameters=[
            OpenApiParameter(name="address_id", description="ID of the shipping address to update", required=True)],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Shipping Address details updated successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid date"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Shipping Address not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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

    @extend_schema(
        summary="Delete Shipping Address",
        description="API endpoint for deleting address details. Requires user authentication.",
        parameters=[
            OpenApiParameter(name="address_id", description="ID of the shipping address to delete", required=True)],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Shipping Address details removed successfully"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Shipping Address not found"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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
    serializer_classes = AddressSerializer

    @extend_schema(
        summary="Create or Add Shipping Address",
        description="API endpoint for creating new shipping addresses details. Requires user authentication.",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Shipping Address details added successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid data"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
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


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Initiate Checkout Process",
        description="API endpoint for handling the checkout process. Requires user authentication.",
        parameters=[
            OpenApiParameter(name="address_id", description="ID of the shipping address to retrieve", required=True)],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Checkout process initiated successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Checkout initiation failed"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def post(self, request):
        try:

            cart = Cart.objects.get(user=request.user)
            coupon_code = request.data.get('coupon_code', None)

            if coupon_code:
                try:
                    coupon = CouponCode.objects.get(code=coupon_code, expired=False)
                except CouponCode.DoesNotExist:
                    return custom_response({}, "Invalid coupon code", status.HTTP_400_BAD_REQUEST, "error")
                if not coupon.is_valid():
                    return custom_response({}, "Coupon code has expired", status.HTTP_400_BAD_REQUEST, "error")

                cart.apply_coupon(coupon)

            order_serializer = OrderSerializer(data={'user': request.user.id, 'cart': cart.id})
            if order_serializer.is_valid():
                order = order_serializer.save()

                payment_serializer = PaymentSerializer(data={'order': order.id, 'amount': cart.calculate_total()})
                if payment_serializer.is_valid():
                    payment_serializer.save()
                else:
                    order.delete()
                    return custom_response(payment_serializer.errors, "Payment failed", status.HTTP_400_BAD_REQUEST,
                                           "error")

                for cart_item in cart.cartitem_set.all():
                    product = cart_item.product
                    product.quantity -= cart_item.quantity
                    product.save()

                return Response({"message": "Checkout process initiated successfully", "order_id": order.id}, status.
                                HTTP_200_OK)
            else:
                return custom_response(order_serializer.errors, "Checkout initiation failed",
                                       status.HTTP_400_BAD_REQUEST, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred during checkout: {str(e)}",
            }
            return custom_response(data, "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR, "error")


class CouponCodeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve Available Coupons",
        description="API endpoint for retrieving available coupon codes. Requires user authentication.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Coupons retrieved successfully"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description="Internal server error"),
        }
    )
    def get(self, request):

        try:
            coupons = CouponCode.objects.filter(expired=False)
            serializer = CouponCodeSerializer(coupons, many=True)
            return custom_response(serializer.data, "Coupons retrieved successfully", status.HTTP_200_OK, "error")

        except Exception as e:
            data = {
                "error_message": f"An error occurred while fetching coupons: {str(e)}",
            }
            return custom_response(data, status.HTTP_500_INTERNAL_SERVER_ERROR, "error")
