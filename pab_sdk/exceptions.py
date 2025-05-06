"""
Exception classes for the PAB SDK.

This module contains custom exception classes used throughout the SDK.
"""


class ApiError(Exception):
    """Exception raised for errors in API responses."""
    pass


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""
    pass


class ResourceNotReadyError(Exception):
    """Exception raised when a resource fails to become ready."""
    pass


class TimeoutError(Exception):
    """Exception raised when an operation times out."""
    pass 