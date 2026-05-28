"""
Test suite for custom exception classes in the blog application.

Tests the exception hierarchy, error codes, HTTP status codes, and
error message formatting for all custom exceptions.
"""

import unittest
from blog_app.exceptions import (
    BlogAppException,
    RecordingException,
    RecordingNotFound,
    RecordingValidationError,
    InvalidConfidenceScore,
    SpeciesException,
    SpeciesNotFound,
    LocationException,
    LocationNotFound,
    FormException,
    InvalidFormData,
    FileUploadError
)


class TestBlogAppException(unittest.TestCase):
    """Test the base BlogAppException class."""
    
    def test_exception_creation(self):
        """Test creating a basic exception."""
        exc = BlogAppException("Test error message")
        self.assertEqual(exc.message, "Test error message")
        self.assertEqual(exc.error_code, "BLOG_APP_ERROR")
        self.assertEqual(exc.http_status_code, 500)
    
    def test_exception_with_custom_error_code(self):
        """Test exception with custom error code."""
        exc = BlogAppException("Test error", error_code="CUSTOM_CODE")
        self.assertEqual(exc.error_code, "CUSTOM_CODE")
    
    def test_exception_with_details(self):
        """Test exception with additional details."""
        details = {'key': 'value', 'nested': {'data': 123}}
        exc = BlogAppException("Test error", details=details)
        self.assertEqual(exc.details['key'], 'value')
        self.assertEqual(exc.details['nested']['data'], 123)
    
    def test_exception_to_dict(self):
        """Test converting exception to dictionary for JSON response."""
        exc = BlogAppException("Test error", error_code="TEST_CODE", 
                              details={'info': 'test'})
        exc_dict = exc.to_dict()
        
        self.assertEqual(exc_dict['error'], 'TEST_CODE')
        self.assertEqual(exc_dict['message'], 'Test error')
        self.assertEqual(exc_dict['details']['info'], 'test')
    
    def test_exception_kwargs(self):
        """Test exception with additional kwargs."""
        exc = BlogAppException("Test error", user_id=42, action="create")
        self.assertEqual(exc.details['user_id'], 42)
        self.assertEqual(exc.details['action'], 'create')


class TestRecordingExceptions(unittest.TestCase):
    """Test recording-related exceptions."""
    
    def test_recording_exception_inheritance(self):
        """Test that RecordingException inherits from BlogAppException."""
        exc = RecordingException("Recording error")
        self.assertIsInstance(exc, BlogAppException)
        self.assertEqual(exc.error_code, "RECORDING_ERROR")
    
    def test_recording_not_found(self):
        """Test RecordingNotFound exception."""
        exc = RecordingNotFound(recording_id=123)
        self.assertEqual(exc.http_status_code, 404)
        self.assertEqual(exc.error_code, "RECORDING_NOT_FOUND")
        self.assertIn("123", exc.message)
        self.assertEqual(exc.details['recording_id'], 123)
    
    def test_recording_validation_error(self):
        """Test RecordingValidationError exception."""
        exc = RecordingValidationError("Invalid format", field="title", value="x")
        self.assertEqual(exc.http_status_code, 400)
        self.assertEqual(exc.error_code, "RECORDING_VALIDATION_ERROR")
        self.assertEqual(exc.details['field'], 'title')
        self.assertEqual(exc.details['value'], 'x')
    
    def test_invalid_confidence_score_too_high(self):
        """Test InvalidConfidenceScore with value > 1.0."""
        exc = InvalidConfidenceScore(1.5)
        self.assertIn("1.5", exc.message)
        self.assertEqual(exc.details['field'], 'confidence_score')
        self.assertEqual(exc.details['value'], 1.5)
    
    def test_invalid_confidence_score_negative(self):
        """Test InvalidConfidenceScore with negative value."""
        exc = InvalidConfidenceScore(-0.5)
        self.assertIn("-0.5", exc.message)
    
    def test_invalid_confidence_score_valid(self):
        """Test InvalidConfidenceScore message with valid range."""
        exc = InvalidConfidenceScore(2.0)
        self.assertIn("0.0 and 1.0", exc.message)


class TestSpeciesExceptions(unittest.TestCase):
    """Test species-related exceptions."""
    
    def test_species_exception_inheritance(self):
        """Test that SpeciesException inherits from BlogAppException."""
        exc = SpeciesException("Species error")
        self.assertIsInstance(exc, BlogAppException)
        self.assertEqual(exc.error_code, "SPECIES_ERROR")
    
    def test_species_not_found_by_id(self):
        """Test SpeciesNotFound with species ID."""
        exc = SpeciesNotFound(species_id=456)
        self.assertEqual(exc.http_status_code, 404)
        self.assertEqual(exc.error_code, "SPECIES_NOT_FOUND")
        self.assertIn("456", exc.message)
        self.assertEqual(exc.details['species_id'], 456)
    
    def test_species_not_found_by_name(self):
        """Test SpeciesNotFound with species name."""
        exc = SpeciesNotFound(species_name="Kea")
        self.assertEqual(exc.http_status_code, 404)
        self.assertIn("Kea", exc.message)
        self.assertEqual(exc.details['species_name'], 'Kea')
    
    def test_species_not_found_prefers_id_over_name(self):
        """Test that ID takes precedence when both provided."""
        exc = SpeciesNotFound(species_id=789, species_name="Kea")
        self.assertIn("789", exc.message)
        self.assertIn("species_id", exc.details)


class TestLocationExceptions(unittest.TestCase):
    """Test location-related exceptions."""
    
    def test_location_exception_inheritance(self):
        """Test that LocationException inherits from BlogAppException."""
        exc = LocationException("Location error")
        self.assertIsInstance(exc, BlogAppException)
        self.assertEqual(exc.error_code, "LOCATION_ERROR")
    
    def test_location_not_found_by_id(self):
        """Test LocationNotFound with location ID."""
        exc = LocationNotFound(location_id=789)
        self.assertEqual(exc.http_status_code, 404)
        self.assertEqual(exc.error_code, "LOCATION_NOT_FOUND")
        self.assertIn("789", exc.message)
        self.assertEqual(exc.details['location_id'], 789)
    
    def test_location_not_found_by_name(self):
        """Test LocationNotFound with location name."""
        exc = LocationNotFound(location_name="Fiordland")
        self.assertEqual(exc.http_status_code, 404)
        self.assertIn("Fiordland", exc.message)
        self.assertEqual(exc.details['location_name'], 'Fiordland')
    
    def test_location_not_found_prefers_id_over_name(self):
        """Test that ID takes precedence when both provided."""
        exc = LocationNotFound(location_id=999, location_name="Fiordland")
        self.assertIn("999", exc.message)
        self.assertIn("location_id", exc.details)


class TestFormExceptions(unittest.TestCase):
    """Test form-related exceptions."""
    
    def test_form_exception_inheritance(self):
        """Test that FormException inherits from BlogAppException."""
        exc = FormException("Form error")
        self.assertIsInstance(exc, BlogAppException)
        self.assertEqual(exc.error_code, "FORM_ERROR")
        self.assertEqual(exc.http_status_code, 400)
    
    def test_invalid_form_data(self):
        """Test InvalidFormData exception."""
        form_errors = {
            'title': ['This field is required.'],
            'species': ['Invalid choice.']
        }
        exc = InvalidFormData("Form submission failed", form_errors=form_errors)
        self.assertEqual(exc.error_code, "INVALID_FORM_DATA")
        self.assertEqual(exc.details['form_errors'], form_errors)
    
    def test_invalid_form_data_without_errors(self):
        """Test InvalidFormData without error details."""
        exc = InvalidFormData("Form submission failed")
        self.assertEqual(exc.details['form_errors'], {})
    
    def test_file_upload_error(self):
        """Test FileUploadError exception."""
        exc = FileUploadError("Upload failed", filename="video.mp4", 
                             reason="File too large")
        self.assertEqual(exc.error_code, "FILE_UPLOAD_ERROR")
        self.assertEqual(exc.details['filename'], 'video.mp4')
        self.assertEqual(exc.details['reason'], 'File too large')
    
    def test_file_upload_error_minimal(self):
        """Test FileUploadError with minimal details."""
        exc = FileUploadError("Upload failed")
        self.assertIsNone(exc.details['filename'])
        self.assertIsNone(exc.details['reason'])


class TestExceptionHierarchy(unittest.TestCase):
    """Test the exception inheritance hierarchy."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from BlogAppException."""
        exceptions = [
            RecordingNotFound(1),
            RecordingValidationError("error"),
            InvalidConfidenceScore(1.5),
            SpeciesNotFound(species_id=1),
            LocationNotFound(location_id=1),
            InvalidFormData("error"),
            FileUploadError("error")
        ]
        
        for exc in exceptions:
            self.assertIsInstance(exc, BlogAppException)
    
    def test_exception_catching_by_base_class(self):
        """Test catching exceptions using base class."""
        try:
            raise RecordingNotFound(recording_id=999)
        except BlogAppException as e:
            self.assertEqual(e.error_code, "RECORDING_NOT_FOUND")
    
    def test_exception_catching_by_type(self):
        """Test catching specific exception types."""
        try:
            raise InvalidConfidenceScore(2.0)
        except RecordingValidationError as e:
            self.assertIn("0.0 and 1.0", e.message)


class TestExceptionSerialization(unittest.TestCase):
    """Test exception serialization for API responses."""
    
    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes error, message, and details."""
        exc = RecordingNotFound(recording_id=123)
        exc_dict = exc.to_dict()
        
        self.assertIn('error', exc_dict)
        self.assertIn('message', exc_dict)
        self.assertIn('details', exc_dict)
    
    def test_to_dict_with_complex_details(self):
        """Test to_dict with nested details."""
        exc = InvalidFormData("Form error", form_errors={
            'nested': {
                'field': ['Error 1', 'Error 2']
            }
        })
        exc_dict = exc.to_dict()
        self.assertEqual(
            exc_dict['details']['form_errors']['nested']['field'],
            ['Error 1', 'Error 2']
        )
    
    def test_to_dict_json_serializable(self):
        """Test that to_dict output is JSON-serializable."""
        import json
        exc = RecordingNotFound(recording_id=123)
        exc_dict = exc.to_dict()
        
        # Should not raise an error
        json_str = json.dumps(exc_dict)
        self.assertIsInstance(json_str, str)


if __name__ == '__main__':
    unittest.main()
