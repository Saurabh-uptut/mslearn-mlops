# MLOps Project Guide: Diabetes Classification with Azure Machine Learning

## Learning Objectives

By exploring this MLOps project, you will learn:

1. **End-to-end MLOps Pipeline**: How to implement a complete machine learning operations workflow from development to production including model deployment and testing
2. **CI/CD for ML**: Building, testing, and deploying machine learning models using GitHub Actions for continuous integration and deployment
3. **Azure Machine Learning Integration**: Leveraging Azure ML workspace, compute clusters, job orchestration, and managed endpoints
4. **Model Deployment**: Setting up automated model deployment to managed online endpoints with traffic management
5. **Model Testing and Validation**: Implementing comprehensive endpoint testing and validation strategies for deployed models
6. **Code Quality and Testing**: Implementing proper linting, unit testing, and code validation practices for ML code
7. **Infrastructure as Code**: Using Terraform to provision and manage Azure resources consistently
8. **Data Management**: Understanding data versioning and pipeline abstraction in ML workflows
9. **Model Training Automation**: Converting Jupyter notebooks to production-ready Python scripts with proper parameterization

## Project Structure and Explanation

This project implements a complete MLOps pipeline for diabetes classification using logistic regression. Here's the detailed breakdown of the project structure:

```
mslearn-mlops/
├── .github/
│   └── workflows/
│       └── mlops-pipeline.yml          # GitHub Actions CI/CD pipeline
├── documentation/                      # Learning modules and challenges
├── experimentation/                    # Development environment
│   ├── data/
│   │   └── diabetes-dev.csv           # Development dataset
│   └── train-classification-model.ipynb # Original Jupyter notebook
├── production/                         # Production environment
│   └── data/
│       └── diabetes-prod.csv          # Production dataset
├── src/                               # Source code
│   ├── model/
│   │   └── train.py                   # Main training script
│   ├── job.yml                        # Azure ML job definition
│   ├── job-prod.yml                   # Production job definition
│   ├── endpoint.yml                   # Azure ML endpoint configuration
│   └── deployment.yml                 # Model deployment configuration
├── test_model/                        # Model testing scripts
│   ├── test_endpoint.py               # Endpoint testing script
│   ├── list_resources.py              # Resource listing utility
│   ├── test_data.csv                  # Sample test data
│   └── README.md                      # Testing documentation
├── tests/                             # Test suite
│   ├── test_train.py                  # Unit tests for training script
│   └── datasets/                      # Test data
├── terraform/                         # Infrastructure as Code
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Variable definitions
│   └── outputs.tf                     # Output values
├── requirements.txt                   # Python dependencies
└── pytest.ini                        # pytest configuration
```

### Key Components Explained:

**Source Code (`src/`)**:
- `src/model/train.py`: The main training script that converts the notebook logic into production-ready Python code with:
  - Command-line argument parsing for hyperparameters (`--training_data`, `--reg_rate`)
  - Data loading and preprocessing functions
  - Model training with scikit-learn's LogisticRegression
  - MLflow autologging for experiment tracking and model versioning

**Azure ML Job Definitions**:
- `src/job.yml`: Defines the Azure ML training job with:
  - Environment specification (scikit-learn)
  - Compute target (CPU cluster)
  - Data source reference
  - Parameter configuration

**Model Deployment Configuration**:
- `src/endpoint.yml`: Defines the managed online endpoint configuration:
  - Endpoint name and authentication mode
  - Schema validation using Azure ML schemas
- `src/deployment.yml`: Defines the model deployment specification:
  - Model reference to the trained MLflow model
  - Compute instance type and scaling configuration
  - Traffic allocation settings

**Model Testing (`test_model/`)**:
- `test_model/test_endpoint.py`: Automated endpoint testing script with:
  - Error handling and troubleshooting guidance
  - Real-time prediction testing capabilities
  - Formatted output and result validation
- `test_model/list_resources.py`: Utility script for listing available endpoints and models
- `test_model/test_data.csv`: Sample test data for endpoint validation

**Infrastructure (`terraform/`)**:
- Provisions Azure resources including:
  - Resource Group and Storage Account
  - Machine Learning Workspace
  - Application Insights for monitoring
  - Key Vault for secrets management
  - Compute cluster for model training

## Data Structure

The project uses diabetes classification data with the following characteristics:

### Dataset Schema
The diabetes dataset contains the following features and target:
- **Features**: Pregnancies, PlasmaGlucose, DiastolicBloodPressure, TricepsThickness, SerumInsulin, BMI, DiabetesPedigree, Age
- **Target**: Diabetic (0 or 1)

### Data Organization
1. **Development Data** (`experimentation/data/diabetes-dev.csv`):
   - Used during model development and experimentation
   - Contains sample data for initial training and validation

2. **Production Data** (`production/data/diabetes-prod.csv`):
   - Used for final model training and deployment
   - Represents the real production dataset

3. **Test Data** (`tests/datasets/`):
   - Small synthetic datasets for unit testing
   - Includes `first.csv` and `second.csv` with 10 rows each for testing data loading functions

### Data Pipeline Flow
1. Data is loaded using `get_csvs_df()` function from multiple CSV files
2. Features and target are split using `split_data()` function
3. Training/test split (70/30) is performed with `random_state=0` for reproducibility

## GitHub Actions Workflow

The MLOps pipeline is defined in `.github/workflows/mlops-pipeline.yml` and implements a four-stage workflow:

### Workflow Overview
```yaml
name: MLOps pipeline
on: workflow_dispatch  # Manual trigger only
```

### Stage 1: Linting (`linting` job)
**Purpose**: Code quality validation
```yaml
- Checks out the repository
- Sets up Python 3.8 environment
- Installs Flake8 linting tool
- Runs linting on src/ directory
```

**Validation**: Ensures code follows Python style guidelines and catches basic syntax issues.

### Stage 2: Unit Tests (`unit-tests` job)
**Purpose**: Automated testing of core functionality
```yaml
- Checks out repository
- Sets up Python 3.8 environment  
- Installs dependencies from requirements.txt
- Runs pytest on tests/ directory
```

**Test Coverage**: Tests include:
- `test_csvs_no_files()`: Validates error handling for missing CSV files
- `test_csvs_no_files_invalid_path()`: Tests invalid path error handling
- `test_csvs_creates_dataframe()`: Verifies data loading functionality

### Stage 3: Training (`train` job)
**Purpose**: Model training on Azure ML
```yaml
- Uses 'development' environment for deployment approval
- Checks out repository
- Installs Azure ML CLI extension
- Authenticates using AZURE_CREDENTIALS secret
- Creates data asset (diabetes-dev-folder)
- Triggers Azure ML training job
```

**Azure Integration**: 
- Creates data asset from `experimentation/data/` directory
- Submits training job defined in `src/job.yml`
- Uses hardcoded resource group and workspace names for development environment

### Stage 4: Deployment (`deploy-endpoint` job)
**Purpose**: Model deployment to managed online endpoint
```yaml
- Depends on successful completion of training job (needs: train)
- Uses 'development' environment for deployment approval
- Checks out repository
- Installs Azure ML CLI extension
- Authenticates using AZURE_CREDENTIALS secret
- Creates or updates managed online endpoint
- Deploys trained model to endpoint with 100% traffic allocation
```

**Deployment Process**:
- Creates managed online endpoint using `src/endpoint.yml` configuration
- Deploys the trained MLflow model using `src/deployment.yml` specification
- Automatically routes 100% of traffic to the new deployment
- Enables real-time inference capabilities for the diabetes classification model

### Security and Access Control
- Uses service principal authentication via `AZURE_CREDENTIALS` GitHub secret
- Environment-based deployment approval system
- Secure handling of Azure credentials through GitHub secrets

## Testing Steps

### 1. Local Testing Setup
Before running the full pipeline, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run linting locally
pip install flake8
flake8 src/

# Run unit tests
pytest tests/ -v
```

### 2. Unit Test Execution
The test suite covers critical data handling functionality:

```python
# Test for proper error handling when no CSV files exist
def test_csvs_no_files():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("./")
    assert error.match("No CSV files found in provided data")

# Test for invalid path handling  
def test_csvs_no_files_invalid_path():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("/invalid/path/does/not/exist/")
    assert error.match("Cannot use non-existent path provided")

# Test actual data loading functionality
def test_csvs_creates_dataframe():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    datasets_directory = os.path.join(current_directory, 'datasets')
    result = get_csvs_df(datasets_directory)
    assert len(result) == 20  # Validates correct number of rows loaded
```

### 3. Pipeline Testing
To test the complete pipeline:

1. **Setup Prerequisites**:
   - Azure subscription with proper permissions
   - Service principal with contributor access to resource group
   - GitHub repository with `AZURE_CREDENTIALS` secret configured

2. **Manual Trigger**:
   - Navigate to GitHub Actions tab in your repository
   - Select "MLOps pipeline" workflow
   - Click "Run workflow" button
   - Monitor execution through GitHub Actions interface

3. **Validation Points**:
   - Linting job should complete without errors
   - Unit tests should pass (green checkmarks)
   - Training job should successfully create data asset and submit ML job to Azure

### 4. Azure ML Validation
After the pipeline runs, verify in Azure ML workspace:
- Check for new experiment runs in "diabetes-training" experiment
- Verify data asset "diabetes-dev-folder" is created
- Confirm training job completes successfully with logged metrics and model artifacts
- Verify endpoint "diabetes-endpoint" is created and active
- Confirm model deployment with 100% traffic allocation

### 5. Model Deployment and Endpoint Testing

#### Automated Endpoint Testing
The project includes comprehensive endpoint testing capabilities in the `test_model/` directory:

**Check Available Resources**:
```bash
# List all endpoints and models in your workspace
cd test_model
python3 list_resources.py
```

**Test Deployed Endpoint**:
```bash
# Test the deployed diabetes endpoint with sample data
python3 test_endpoint.py --endpoint-name diabetes-endpoint \
  --resource-group rg-mlops-dev-ksh026 \
  --workspace-name mlw-diabetes-dev-ksh026
```

**Expected Output**:
```
============================================================
AZURE ML MODEL ENDPOINT TESTING
============================================================
Endpoint:       diabetes-endpoint
Resource Group: rg-mlops-dev-ksh026
Workspace:      mlw-diabetes-dev-ksh026
Test Data:      test_data.csv
============================================================
✓ Loaded 3 test samples from test_data.csv

📡 Testing endpoint: diabetes-endpoint
------------------------------------------------------------

✓ Predictions received:
[0, 1, 0]

============================================================
TEST RESULTS SUMMARY
============================================================
Pregnancies  PlasmaGlucose  ...  Age  Prediction
9            104            ...  43   0
6            73             ...  75   1
4            115            ...  59   0

✓ Test completed successfully!
```

#### Manual Testing (Alternative)
You can also test the endpoint manually using Azure CLI:

```bash
# Create test request file
echo '{
  "input_data": {
    "columns": ["Pregnancies","PlasmaGlucose","DiastolicBloodPressure","TricepsThickness","SerumInsulin","BMI","DiabetesPedigree","Age"],
    "index": [0],
    "data": [[9,104,51,7,24,27.36983156,1.350472047,43]]
  }
}' > test_request.json

# Test endpoint
az ml online-endpoint invoke \
  --name diabetes-endpoint \
  --request-file test_request.json \
  --resource-group rg-mlops-dev-ksh026 \
  --workspace-name mlw-diabetes-dev-ksh026
```

### 6. Monitoring and Debugging
- Review GitHub Actions logs for detailed execution information
- Check Azure ML workspace for experiment tracking and model versioning
- Monitor compute cluster utilization during training
- Use `list_resources.py` to verify endpoint and model deployment status
- Check endpoint health and traffic distribution in Azure ML Studio

### 7. End-to-End Pipeline Validation

The complete MLOps pipeline now includes:

1. **Code Quality**: Linting and static analysis
2. **Unit Testing**: Automated test execution
3. **Model Training**: Azure ML job orchestration with MLflow tracking
4. **Model Deployment**: Automated endpoint creation and deployment
5. **Endpoint Testing**: Validation of deployed model functionality

This comprehensive testing approach ensures the MLOps pipeline is robust, maintainable, and production-ready while providing clear feedback at each stage of the workflow from code to deployed model.
