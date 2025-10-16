from model.train import get_csvs_df, split_data, train_model
import os
import pytest
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression


def test_csvs_no_files():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("./")
    assert error.match("No CSV files found in provided data")


def test_csvs_no_files_invalid_path():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("/invalid/path/does/not/exist/")
    assert error.match("Cannot use non-existent path provided")


def test_csvs_creates_dataframe():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    datasets_directory = os.path.join(current_directory, 'datasets')
    result = get_csvs_df(datasets_directory)
    assert len(result) == 20


def test_split_data():
    """Test split_data function with valid diabetes data."""
    # Create sample data with expected columns
    data = {
        'Pregnancies': [1, 2, 3, 4, 5],
        'PlasmaGlucose': [100, 110, 120, 130, 140],
        'DiastolicBloodPressure': [60, 65, 70, 75, 80],
        'TricepsThickness': [10, 15, 20, 25, 30],
        'SerumInsulin': [50, 55, 60, 65, 70],
        'BMI': [20.0, 21.0, 22.0, 23.0, 24.0],
        'DiabetesPedigree': [0.5, 0.6, 0.7, 0.8, 0.9],
        'Age': [30, 35, 40, 45, 50],
        'Diabetic': [0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    
    X_train, X_test, y_train, y_test = split_data(df)
    
    # Check return types and shapes
    assert isinstance(X_train, np.ndarray)
    assert isinstance(X_test, np.ndarray)
    assert isinstance(y_train, np.ndarray)
    assert isinstance(y_test, np.ndarray)
    
    # Check shapes (test_size=0.30, so 30% goes to test)
    expected_train_size = int(0.7 * len(df))
    expected_test_size = len(df) - expected_train_size
    
    assert X_train.shape == (expected_train_size, 8)  # 8 features
    assert X_test.shape == (expected_test_size, 8)
    assert y_train.shape == (expected_train_size,)
    assert y_test.shape == (expected_test_size,)


def test_split_data_missing_columns():
    """Test split_data function with missing columns raises error."""
    data = {
        'Pregnancies': [1, 2, 3],
        'PlasmaGlucose': [100, 110, 120],
        'Diabetic': [0, 1, 0]
    }
    df = pd.DataFrame(data)
    
    with pytest.raises(KeyError):
        split_data(df)


def test_split_data_empty_dataframe():
    """Test split_data function with empty dataframe."""
    columns = [
        'Pregnancies', 'PlasmaGlucose', 'DiastolicBloodPressure',
        'TricepsThickness', 'SerumInsulin', 'BMI', 'DiabetesPedigree',
        'Age', 'Diabetic'
    ]
    df = pd.DataFrame(columns=columns)
    
    X_train, X_test, y_train, y_test = split_data(df)
    
    assert X_train.shape[0] == 0
    assert X_test.shape[0] == 0
    assert y_train.shape[0] == 0
    assert y_test.shape[0] == 0


def test_train_model():
    """Test train_model function with mock data."""
    # Create sample training and test data
    X_train = np.array([[1, 100, 60, 10, 50, 20.0, 0.5, 30]] * 5)
    X_test = np.array([[2, 110, 65, 15, 55, 21.0, 0.6, 35]])
    y_train = np.array([0, 1, 0, 1, 0])
    y_test = np.array([1])
    
    reg_rate = 0.01
    model = train_model(reg_rate, X_train, X_test, y_train, y_test)
    
    # Check that model is a LogisticRegression instance
    assert isinstance(model, LogisticRegression)
    
    # Check that model has been fitted
    assert hasattr(model, 'coef_')
    assert hasattr(model, 'intercept_')
    
    # Check that model can make predictions
    predictions = model.predict(X_test)
    assert len(predictions) == len(X_test)
    assert all(pred in [0, 1] for pred in predictions)


def test_train_model_different_reg_rate():
    """Test train_model function with different regularization rates."""
    X_train = np.array([[1, 100, 60, 10, 50, 20.0, 0.5, 30]] * 5)
    X_test = np.array([[2, 110, 65, 15, 55, 21.0, 0.6, 35]])
    y_train = np.array([0, 1, 0, 1, 0])
    y_test = np.array([1])
    
    # Test with different regularization rates
    reg_rates = [0.001, 0.01, 0.1, 1.0]
    
    for reg_rate in reg_rates:
        model = train_model(reg_rate, X_train, X_test, y_train, y_test)
        assert isinstance(model, LogisticRegression)
        
        # Verify the model's C parameter matches expected value
        expected_C = 1 / reg_rate
        assert model.C == expected_C
