from functools import wraps
from flask import request, jsonify, current_app
import os
import secrets

# In production, these will come from Secret Manager
API_KEYS = {
    'admin_key': os.getenv('ADMIN_API_KEY', secrets.token_urlsafe(32)),
    'read_only_key': os.getenv('READONLY_API_KEY', secrets.token_urlsafe(32))
}

def require_api_key(permissions=['read']):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                current_app.logger.warning(
                    f'Missing API key - Path: {request.path}, IP: {request.remote_addr}'
                )
                return jsonify({'error': 'API key required'}), 401
            
            # Validate API key
            if api_key == API_KEYS['admin_key']:
                request.user_permissions = ['read', 'write', 'delete']
            elif api_key == API_KEYS['read_only_key']:
                request.user_permissions = ['read']
            else:
                current_app.logger.warning(
                    f'Invalid API key - Path: {request.path}, IP: {request.remote_addr}'
                )
                return jsonify({'error': 'Invalid API key'}), 403
            
            # Check permissions
            for permission in permissions:
                if permission not in request.user_permissions:
                    current_app.logger.warning(
                        f'Insufficient permissions - Required: {permissions}, Has: {request.user_permissions}'
                    )
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            current_app.logger.info(
                f'Authentication successful - Permissions: {request.user_permissions}'
            )
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator