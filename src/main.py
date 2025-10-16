import mlflow
import pandas as pd
import logging
import json
import os
import numpy as np

def init():
    """Initialize the model for inference."""
    global model
    
    # For MLflow models, we load using the MLDIR path directly
    model_dir = os.getenv('AZUREML_MODEL_DIR', '/var/azureml-app/azureml-models/diabetes-model/3')
    
    try:
        # Load the MLflow model - it should be in the model directory
        if os.path.exists(os.path.join(model_dir, 'model.pkl')):
            model = mlflow.sklearn.load_model(f"file://{model_dir}")
        else:
            # Alternative path - try loading the entire directory as MLflow model
            model = mlflow.sklearn.load_model(f"file://{model_dir}")
        
        logging.info(f"Model loaded successfully from {model_dir}")
        
    except Exception as e:
        logging.error(f"Error loading model from {model_dir}: {str(e)}")
        raise e

def run(raw_data):
    """Run inference on the input data."""
    try:
        # Parse the input data
        data = json.loads(raw_data)
        
        # Handle different input formats
        if isinstance(data, list):
            # If it's a list of records, convert to DataFrame
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a single record, convert to DataFrame
            df = pd.DataFrame([data])
        else:
            raise ValueError("Input data must be a JSON object or array")
        
        # Ensure we have the expected columns in the correct order
        expected_columns = ['Pregnancies', 'PlasmaGlucose', 'DiastolicBloodPressure',
                          'TricepsThickness', 'SerumInsulin', 'BMI', 'DiabetesPedigree',
                          'Age']
        
        # Reorder columns to match training data
        df = df[expected_columns]
        
        # Make prediction
        prediction = model.predict(df)
        
        # Return results in the expected format
        result = {"predictions": prediction.tolist()}
        
        logging.info(f"Prediction completed successfully. Input shape: {df.shape}, Output: {result}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error during inference: {str(e)}"
        logging.error(error_msg)
        return {"error": error_msg, "success": False}
