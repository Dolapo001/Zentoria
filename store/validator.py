from rest_framework import serializers


def validate_coupon_dates(valid_from, valid_to):
    if valid_from and valid_to and valid_from > valid_to:
        raise serializers.ValidationError("Valid from date must be before or equal to valid to date.")


def validate_coupon_validity(coupon):
    if not coupon.is_valid():
        raise serializers.ValidationError("Coupon is not valid.")


def validate_quantity(value):
    if value <= 0:
        raise serializers.ValidationError("Quantity must be greater than zero.")
    return value


def validate_product(value):
    if not value.is_available:
        raise serializers.ValidationError("The selected product is not available.")
    return value


def validate_cartitem_set(value):
    if not value:
        raise serializers.ValidationError("The cart must have at least one item.")
    return value


def validate_total_quantity(value):
    total_quantity = sum(item['quantity'] for item in value)

    if total_quantity <= 0:
        raise serializers.ValidationError("The total quantity in the cart must be greater than zero.")

    return value


def validate_coupon_dates(valid_from, valid_to):
    if valid_from and valid_to and valid_from > valid_to:
        raise serializers.ValidationError("Valid from date must be before or equal to valid to date.")


