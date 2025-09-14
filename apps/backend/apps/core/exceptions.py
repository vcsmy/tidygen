"""
Custom exceptions for TidyGen ERP platform.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for API responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Get the error details
        error_details = response.data
        
        # Log the error
        logger.error(f"API Error: {exc.__class__.__name__}: {error_details}")
        
        # Customize the error response
        custom_response_data = {
            'error': {
                'type': exc.__class__.__name__,
                'message': get_error_message(exc, error_details),
                'details': error_details,
                'status_code': response.status_code
            }
        }
        
        response.data = custom_response_data
    
    return response


def get_error_message(exc, error_details):
    """
    Get a user-friendly error message.
    """
    if isinstance(exc, Http404):
        return "The requested resource was not found."
    elif isinstance(exc, PermissionDenied):
        return "You don't have permission to perform this action."
    elif hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        elif isinstance(exc.detail, list) and exc.detail:
            return exc.detail[0]
        elif isinstance(exc.detail, dict):
            # Get the first error message from the dict
            for field, errors in exc.detail.items():
                if isinstance(errors, list) and errors:
                    return f"{field}: {errors[0]}"
                elif isinstance(errors, str):
                    return f"{field}: {errors}"
    elif isinstance(error_details, dict):
        # Handle validation errors
        for field, errors in error_details.items():
            if isinstance(errors, list) and errors:
                return f"{field}: {errors[0]}"
            elif isinstance(errors, str):
                return f"{field}: {errors}"
    
    return "An unexpected error occurred."


class ValidationError(Exception):
    """
    Custom validation error.
    """
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """
    Custom business logic error.
    """
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class Web3Error(Exception):
    """
    Custom Web3 related error.
    """
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OrganizationError(Exception):
    """
    Custom organization related error.
    """
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)
