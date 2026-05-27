"""
Custom exception classes for the blog application.

This module defines a hierarchy of custom exceptions that provide:
- Clear semantic meaning for different error scenarios
- Standardized error handling across the application
- Better debugging information and error tracking
- Improved API error responses

Exception Hierarchy:
    BlogAppException (Base)
        ├── RecordingException
        │   ├── RecordingNotFound
        │   ├── RecordingValidationError
        │   └── InvalidConfidenceScore
        ├── SpeciesException
        │   └── SpeciesNotFound
        ├── LocationException
        │   └── LocationNotFound
        └── FormException
            ├── InvalidFormData
            └── FileUploadError
"""


class BlogAppException(Exception):
    """
    Base exception class for all blog application exceptions.
    
    All custom exceptions in the application should inherit from this to allow
    for broad exception handling at the application level.
    
    Attributes:
        message (str): Human-readable error message
        error_code (str): Machine-readable error identifier
        details (dict): Additional context-specific error information
    """
    
    error_code = "BLOG_APP_ERROR"
    http_status_code = 500
    
    def __init__(self, message, error_code=None, details=None, **kwargs):
        self.message = message
        self.error_code = error_code or self.error_code
        self.details = details or {}
        self.details.update(kwargs)
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary for JSON responses."""
        return {
            'error': self.error_code,
            'message': self.message,
            'details': self.details
        }


class RecordingException(BlogAppException):
    """Base exception for recording-related errors."""
    error_code = "RECORDING_ERROR"


class RecordingNotFound(RecordingException):
    """Raised when a recording cannot be found in the database."""
    error_code = "RECORDING_NOT_FOUND"
    http_status_code = 404
    
    def __init__(self, recording_id, **kwargs):
        message = f"Recording with ID {recording_id} not found."
        super().__init__(message, details={'recording_id': recording_id}, **kwargs)


class RecordingValidationError(RecordingException):
    """Raised when recording data fails validation."""
    error_code = "RECORDING_VALIDATION_ERROR"
    http_status_code = 400
    
    def __init__(self, message, field=None, value=None, **kwargs):
        super().__init__(message, details={'field': field, 'value': value}, **kwargs)


class InvalidConfidenceScore(RecordingValidationError):
    """Raised when confidence score is outside valid range (0.0-1.0)."""
    error_code = "INVALID_CONFIDENCE_SCORE"
    
    def __init__(self, value, **kwargs):
        message = f"Confidence score must be between 0.0 and 1.0, got {value}."
        super().__init__(message, field='confidence_score', value=value, **kwargs)


class SpeciesException(BlogAppException):
    """Base exception for species-related errors."""
    error_code = "SPECIES_ERROR"


class SpeciesNotFound(SpeciesException):
    """Raised when a species cannot be found in the database."""
    error_code = "SPECIES_NOT_FOUND"
    http_status_code = 404
    
    def __init__(self, species_id=None, species_name=None, **kwargs):
        if species_id:
            message = f"Species with ID {species_id} not found."
            details = {'species_id': species_id}
        else:
            message = f"Species '{species_name}' not found."
            details = {'species_name': species_name}
        super().__init__(message, details=details, **kwargs)


class LocationException(BlogAppException):
    """Base exception for location-related errors."""
    error_code = "LOCATION_ERROR"


class LocationNotFound(LocationException):
    """Raised when a location cannot be found in the database."""
    error_code = "LOCATION_NOT_FOUND"
    http_status_code = 404
    
    def __init__(self, location_id=None, location_name=None, **kwargs):
        if location_id:
            message = f"Location with ID {location_id} not found."
            details = {'location_id': location_id}
        else:
            message = f"Location '{location_name}' not found."
            details = {'location_name': location_name}
        super().__init__(message, details=details, **kwargs)


class FormException(BlogAppException):
    """Base exception for form-related errors."""
    error_code = "FORM_ERROR"
    http_status_code = 400


class InvalidFormData(FormException):
    """Raised when form data is invalid."""
    error_code = "INVALID_FORM_DATA"
    
    def __init__(self, message, form_errors=None, **kwargs):
        super().__init__(message, details={'form_errors': form_errors or {}}, **kwargs)


class FileUploadError(FormException):
    """Raised when file upload fails."""
    error_code = "FILE_UPLOAD_ERROR"
    
    def __init__(self, message, filename=None, reason=None, **kwargs):
        super().__init__(
            message,
            details={'filename': filename, 'reason': reason},
            **kwargs
        )
