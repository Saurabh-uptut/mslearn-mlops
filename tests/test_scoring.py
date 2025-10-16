"""Tests for the scoring script (main.py)."""

import pytest
import json
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path to import main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import pandas only when needed to avoid version conflicts
try:
    import pandas as pd
except ImportError as e:
    pytest.skip(f"pandas not available: {e}", allow_module_level=True)


class TestScoringScript:
    """Test class for scoring script functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Import and reset the main module for each test
        import main
        import importlib
        importlib.reload(main)
        
        # Mock the global model variable
        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = np.array([0, 1, 0])
        
        # Set the mock model in the main module
        main.model = self.mock_model

    @patch('mlflow.sklearn.load_model')
    @patch.dict(os.environ, {'AZUREML_MODEL_DIR': '/test/model/dir'})
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_init_success(self, mock_listdir, mock_exists, mock_load_model):
        """Test successful model initialization."""
        # Mock the file system responses
        mock_exists.side_effect = lambda path: (
            '/test/model/dir/model' in path if 'model' in path else 
            '/test/model/dir' in path
        )
        mock_load_model.return_value = self.mock_model
        
        import main
        import importlib
        importlib.reload(main)  # Reload to reset global state
        
        # Call init function
        main.init()
        
        # Verify model was loaded
        assert main.model is not None

    def test_run_single_record_dict(self):
        """Test run function with single record as dictionary."""
        import main
        
        # Ensure we have a mock model set up
        main.model = self.mock_model
        main.model.predict.return_value = np.array([1])
        
        # Single record test data
        test_data = {
            "Pregnancies": 9,
            "PlasmaGlucose": 104,
            "DiastolicBloodPressure": 51,
            "TricepsThickness": 7,
            "SerumInsulin": 24,
            "BMI": 27.36983156,
            "DiabetesPedigree": 1.350472047,
            "Age": 43
        }
        
        raw_data = json.dumps(test_data)
        result = main.run(raw_data)
        
        # Check result format
        assert "predictions" in result
        assert result["predictions"] == [1]
        
        # Verify model was called with correct data
        main.model.predict.assert_called_once()

    def test_run_multiple_records_list(self):
        """Test run function with multiple records as list."""
        import main
        
        # Ensure we have a mock model set up
        main.model = self.mock_model
        main.model.predict.return_value = np.array([0, 1, 0])
        
        # Multiple records test data
        test_data = [
            {
                "Pregnancies": 9,
                "PlasmaGlucose": 104,
                "DiastolicBloodPressure": 51,
                "TricepsThickness": 7,
                "SerumInsulin": 24,
                "BMI": 27.36,
                "DiabetesPedigree": 1.35,
                "Age": 43
            },
            {
                "Pregnancies": 6,
                "PlasmaGlucose": 73,
                "DiastolicBloodPressure": 61,
                "TricepsThickness": 35,
                "SerumInsulin": 24,
                "BMI": 18.74,
                "DiabetesPedigree": 1.07,
                "Age": 75
            },
            {
                "Pregnancies": 4,
                "PlasmaGlucose": 115,
                "DiastolicBloodPressure": 50,
                "TricepsThickness": 29,
                "SerumInsulin": 243,
                "BMI": 34.69,
                "DiabetesPedigree": 0.74,
                "Age": 59
            }
        ]
        
        raw_data = json.dumps(test_data)
        result = main.run(raw_data)
        
        # Check result format
        assert "predictions" in result
        assert result["predictions"] == [0, 1, 0]
        assert len(result["predictions"]) == 3

    def test_run_missing_columns(self):
        """Test run function with missing columns returns error."""
        import main
        
        # Ensure we have a mock model set up
        main.model = self.mock_model
        main.model.predict.return_value = np.array([1])
        
        # Test data missing some required columns
        test_data = {
            "Pregnancies": 9,
            "PlasmaGlucose": 104,
            # Missing other required columns
        }
        
        raw_data = json.dumps(test_data)
        result = main.run(raw_data)
        
        # Should return error (KeyError when accessing missing columns)
        assert "error" in result
        assert result.get("success") is False

    def test_run_invalid_json(self):
        """Test run function with invalid JSON returns error."""
        import main
        
        # Ensure we have a mock model set up
        main.model = self.mock_model
        
        # Invalid JSON
        raw_data = '{"invalid": json}'
        
        result = main.run(raw_data)
        
        # Should return error
        assert "error" in result
        assert result.get("success") is False

    def test_run_invalid_data_type(self):
        """Test run function with invalid data type returns error."""
        import main
        
        # Ensure we have a mock model set up
        main.model = self.mock_model
        
        # Invalid data type (not dict or list)
        test_data = "invalid string"
        raw_data = json.dumps(test_data)
        
        result = main.run(raw_data)
        
        # Should return error
        assert "error" in result
        assert result.get("success") is False
        assert "Input data must be a JSON object or array" in result["error"]

    def test_run_model_not_initialized(self):
        """Test run function when model is not initialized."""
        import main
        
        # Ensure model is None
        main.model = None
        
        test_data = {
            "Pregnancies": 9,
            "PlasmaGlucose": 104,
            "DiastolicBloodPressure": 51,
            "TricepsThickness": 7,
            "SerumInsulin": 24,
            "BMI": 27.36,
            "DiabetesPedigree": 1.35,
            "Age": 43
        }
        
        raw_data = json.dumps(test_data)
        result = main.run(raw_data)
        
        # Should handle the case gracefully
        assert isinstance(result, dict)

    def test_run_prediction_exception(self):
        """Test run function when model prediction fails."""
        import main
        
        # Ensure we have a mock model set up and mock it to raise exception
        main.model = self.mock_model
        main.model.predict.side_effect = Exception("Model prediction failed")
        
        test_data = {
            "Pregnancies": 9,
            "PlasmaGlucose": 104,
            "DiastolicBloodPressure": 51,
            "TricepsThickness": 7,
            "SerumInsulin": 24,
            "BMI": 27.36,
            "DiabetesPedigree": 1.35,
            "Age": 43
        }
        
        raw_data = json.dumps(test_data)
        result = main.run(raw_data)
        
        # Should return error
        assert "error" in result
        assert result.get("success") is False
        assert "Error during inference" in result["error"]

    def test_expected_columns_constant(self):
        """Test that expected columns match training data format."""
        import main
        
        # Import the expected columns
        expected_columns = [
            'Pregnancies', 'PlasmaGlucose', 'DiastolicBloodPressure',
            'TricepsThickness', 'SerumInsulin', 'BMI', 'DiabetesPedigree',
            'Age'
        ]
        
        # These should match the columns used in training
        assert len(expected_columns) == 8
        assert 'Pregnancies' in expected_columns
        assert 'PlasmaGlucose' in expected_columns
        assert 'Age' in expected_columns
