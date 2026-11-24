from enum import Enum

from app.core.config import settings

ACCESS_TOKEN_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600


class Messages(str, Enum):
    EMAIL_EXISTS = "Email already exists"
    AUTH_FAILED = "Email or password is incorrect"
    ACCOUNT_INACTIVE = "Your account is inactive. Please contact support."
    TOKEN_MISSING = "Refresh token missing"
    TOKEN_INVALID = "Invalid token"
    SESSION_EXPIRED = "Session expired or user inactive"
    TOKEN_WRONG = "Wrong token"
    USER_NOT_FOUND = "User not found"
    LOGIN_SUCCESS = "User logged in successfully"
    TOKEN_REFRESH_SUCCESS = "New Access Token generated successfully"
    LOGOUT_SUCCESS = "Logged out successfully"

    RESTAURANT_CREATED = "Restaurant created successfully"
    RESTAURANT_DELETED = "Restaurant deleted successfully"
    RESTAURANT_NOT_FOUND = "Restaurant not found"

    MENU_ITEM_CREATED = "Menu item created successfully"
    MENU_ITEM_DELETED = "Menu item deleted successfully"
    MENU_ITEM_NOT_FOUND = "Menu item not found"
    MENU_ITEM_ALREADY_EXISTS = "Menu item already exists with this name"
    PERMISSION_DENIED = "You do not have permission to perform this action"

    CART_ACTIVE_NOT_FOUND = "No active cart found for this restaurant."
    CART_NOT_FOUND = "Cart not found."
    CART_DOES_NOT_EXIST = "Cart does not exist."
    CART_ITEM_WRONG_RESTAURANT = "This menu item does not belong to the specified restaurant."
    CART_ITEM_OUT_OF_STOCK = "'{name}' is currently out of stock."
    CART_ITEM_INSUFFICIENT_STOCK = "Only {stock} units of '{name}' are available."
    CART_ITEM_REMOVED_EMPTY = "Item removed and empty cart deleted."
    CART_UPDATED = "Cart updated successfully."
    CART_DELETE_FORBIDDEN = "Not authorized to delete this cart."
    CART_DELETED = "Cart deleted successfully."
    CART_CONFLICT = "Cart could not be updated due to a database constraint conflict."

    ORDER_PLACED = "Order placed successfully."
    ORDER_NOT_FOUND = "Order not found."
    ORDER_VIEW_FORBIDDEN = "Not authorized to view this order."
    ORDER_UPDATE_FORBIDDEN = "Only the owner of this restaurant can update the order status."
    ORDER_INSUFFICIENT_STOCK = "Insufficient stock for '{name}'. Available: {stock}"
    ORDER_STATUS_ALREADY_SET = "Order status is already {status}."
    ORDER_INVALID_TRANSITION = "Cannot transition order from {current_status} to {new_status}."
    ORDER_STATUS_UPDATED = "Order status updated to {status}."
