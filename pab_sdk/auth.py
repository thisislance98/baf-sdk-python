"""
Authentication module for the BAF SDK.

This module handles OAuth token acquisition and refresh.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Optional

import requests


logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages OAuth tokens for the BAF SDK.
    
    This class handles token acquisition, caching, and automatic refresh.
    """
    
    def __init__(self, auth_url: str, client_id: str, client_secret: str):
        """
        Initialize the token manager.
        
        Args:
            auth_url: The OAuth token endpoint URL
            client_id: The client ID for authentication
            client_secret: The client secret for authentication
        """
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None
    
    def get_token(self) -> str:
        """
        Get a valid OAuth token.
        
        If a token is already available and not close to expiration, it will be reused.
        Otherwise, a new token will be obtained.
        
        Returns:
            The OAuth token as a string
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        # Check if we need a new token (if current one is missing or about to expire)
        if not self._token or not self._expires_at or self._expires_at <= time.time() + 60:
            self._refresh_token()
            
        return self._token
    
    def _refresh_token(self) -> None:
        """
        Obtain a new OAuth token from the authorization server.
        
        Updates the internal token and expiration time.
        
        Raises:
            AuthenticationError: If token acquisition fails
        """
        logger.debug("Obtaining new OAuth token")
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(self.auth_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self._token = token_data["access_token"]
            # Set expiration time with a safety margin
            self._expires_at = time.time() + token_data["expires_in"] * 0.9
            
            logger.debug("Successfully acquired new OAuth token")
            
        except requests.RequestException as e:
            logger.error(f"Failed to obtain OAuth token: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise AuthenticationError(f"Failed to obtain OAuth token: {str(e)}") from e


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""
    pass 