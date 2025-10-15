# Model Endpoint Testing

This directory contains scripts to test the deployed diabetes prediction model endpoint in Azure ML.

## Prerequisites

1. **Azure CLI** installed and configured
2. **Azure ML CLI extension** installed:
   ```bash
   az extension add -n ml -y
   ```
3. **Authentication** to Azure:
   ```bash
   az login
   ```
4. **Python 3** installed (no additional dependencies required - uses only standard library modules)
5. **Deployed model endpoint** in Azure ML

## Files

- `test_endpoint.py` - Main testing script (with enhanced error handling)
- `list_resources.py` - Helper script to list available endpoints and models
- `test_data.csv` - Sample test data (3 patient records)
- `README.md` - This file

## Quick Start

### 1. Check Available Resources
Before testing, see what endpoints and models exist:
```bash
python3 list_resources.py
```

### 2. Test an Endpoint
```bash
python3 test_endpoint.py --endpoint-name <your-endpoint-name>
```

## Usage

### Basic Usage

```bash
python test_endpoint.py --endpoint-name <your-endpoint-name>
```

### With Custom Parameters

```bash
python test_endpoint.py \
  --endpoint-name diabetes-endpoint \
  --resource-group rg-mlops-dev-ksh026 \
  --workspace-name mlw-diabetes-dev-ksh026 \
  --test-data test_data.csv
```

### Using Environment-Specific Endpoints

For production endpoint:
```bash
python test_endpoint.py \
  --endpoint-name diabetes-prod-endpoint \
  --resource-group rg-mlops-prod-ksh026 \
  --workspace-name mlw-diabetes-prod-ksh026
```

## Test Data Format

The test data CSV should contain the following columns:
- Pregnancies
- PlasmaGlucose
- DiastolicBloodPressure
- TricepsThickness
- SerumInsulin
- BMI
- DiabetesPedigree
- Age

## Expected Output

The script will:
1. Load the test data
2. Send it to the specified endpoint
3. Display the predictions
4. Show a summary of results

Example output:
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
Running: az ml online-endpoint invoke --name diabetes-endpoint ...

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

## Troubleshooting

### "Endpoint not found" (ResourceNotFound Error)
This is the most common issue and means you need to deploy a model first.

**The script now provides helpful guidance when this happens:**

1. **Check what exists:**
   ```bash
   python3 list_resources.py
   ```

2. **If no endpoints exist:**
   - You need to deploy your trained model first
   - Follow the documentation: `mslearn-mlops/documentation/06-deploy-model.md`
   - The script will show you the exact commands needed

3. **If endpoints exist:**
   - Use the correct endpoint name from the list
   - Verify resource group and workspace names

### "Authentication failed"
- Run `az login` to authenticate
- Verify you have access to the resource group and workspace

### "Invalid request format"
- Ensure test data CSV has the correct column names
- Verify the data types match the model's expected input

## Next Steps

After successful testing:
1. Integrate this script into your CI/CD pipeline
2. Add automated tests for different scenarios
3. Monitor endpoint performance and latency
4. Set up alerts for prediction anomalies
