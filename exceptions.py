class NginxManagerError(Exception):
    """Base exception for NginxManager"""
    pass


class ConfigurationError(NginxManagerError):
    """Raised when there's an error in nginx configuration"""
    pass


class PermissionError(NginxManagerError):
    """Raised when there's insufficient permissions"""
    pass
