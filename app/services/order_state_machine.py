"""
Order State Machine

Defines valid order status transitions and provides validation.
"""

from typing import List, Optional

# Valid status transitions
VALID_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['processing', 'cancelled'],
    'processing': ['shipping', 'cancelled'],
    'shipping': ['delivered'],
    'delivered': ['completed'],
    'completed': [],  # Terminal state
    'cancelled': []   # Terminal state
}


def can_transition(current_status: str, new_status: str) -> bool:
    """
    Check if transitioning from current_status to new_status is valid.
    
    Args:
        current_status: Current order status
        new_status: Desired new status
        
    Returns:
        True if transition is valid, False otherwise
    """
    allowed = VALID_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def get_allowed_transitions(current_status: str) -> List[str]:
    """
    Get list of allowed next statuses for the current status.
    
    Args:
        current_status: Current order status
        
    Returns:
        List of allowed next statuses
    """
    return VALID_TRANSITIONS.get(current_status, [])


def validate_transition(current_status: str, new_status: str) -> Optional[str]:
    """
    Validate status transition and return error message if invalid.
    
    Args:
        current_status: Current order status
        new_status: Desired new status
        
    Returns:
        Error message if invalid, None if valid
    """
    if not can_transition(current_status, new_status):
        allowed = get_allowed_transitions(current_status)
        if not allowed:
            return f"Cannot change status from terminal state '{current_status}'"
        return f"Cannot transition from '{current_status}' to '{new_status}'. Allowed: {', '.join(allowed)}"
    return None


def requires_payment_confirmation(order, new_status: str) -> tuple:
    """
    Check if order requires payment confirmation before status change.
    Prevents manual confirmation of unpaid SePay orders.
    
    Args:
        order: Order object
        new_status: Desired new status
        
    Returns:
        (is_blocked: bool, error_message: str)
    """
    # Block manual confirmation of pending SePay orders that haven't been paid
    if (order.status == 'pending' 
        and new_status == 'confirmed' 
        and order.payment_method == 'SEPAY'):
        
        # Check if payment exists and is successful
        if not order.payment or order.payment.status != 'success':
            return (
                True, 
                "Đơn hàng SePay phải được thanh toán trước khi xác nhận. "
                "Vui lòng đợi khách hàng thanh toán hoặc đổi sang phương thức COD."
            )
    
    return False, ""
