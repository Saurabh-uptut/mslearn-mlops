#!/usr/bin/env python3
"""
Test script for Azure ML deployed model endpoint.
This script sends test data to a deployed endpoint and displays predictions.
"""

import argparse
import json
import subprocess
import sys
import csv
from pathlib import Path


def load_test_data(csv_path):
    """Load test data from CSV file."""
    try:
        data = []
        headers = []
        
        with open(csv_path, 'r') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Get column names
            
            for row in csv_reader:
                # Convert string values to appropriate types
                converted_row = []
                for i, value in enumerate(row):
                    try:
                        # Try to convert to float first
                        converted_row.append(float(value))
                    except ValueError:
                        # If not a number, keep as string
                        converted_row.append(value)
                data.append(converted_row)
        
        print(f"✓ Loaded {len(data)} test samples from {csv_path}")
        return headers, data
    except Exception as e:
        print(f"✗ Error loading test data: {e}")
        sys.exit(1)


def prepare_request_data(headers, data):
    """Convert data to the format expected by MLflow model endpoint."""
    request_data = {
        "input_data": {
            "columns": headers,
            "index": list(range(len(data))),
            "data": data
        }
    }
    return request_data


def check_endpoints_exist(resource_group, workspace_name):
    """Check what endpoints exist in the workspace."""
    try:
        cmd = ["az", "ml", "online-endpoint", "list", 
               "--resource-group", resource_group,
               "--workspace-name", workspace_name, 
               "--output", "json"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        endpoints = json.loads(result.stdout) if result.stdout else []
        return endpoints
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def check_endpoint_status(endpoint_name, resource_group, workspace_name):
    """Check endpoint and deployment status."""
    try:
        # Check endpoint status
        cmd = ["az", "ml", "online-endpoint", "show", 
               "--name", endpoint_name,
               "--resource-group", resource_group,
               "--workspace-name", workspace_name,
               "--output", "json"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        endpoint_info = json.loads(result.stdout) if result.stdout else {}
        
        # Check deployments
        cmd_deployments = ["az", "ml", "online-deployment", "list",
                          "--endpoint-name", endpoint_name,
                          "--resource-group", resource_group,
                          "--workspace-name", workspace_name,
                          "--output", "json"]
        
        result_deployments = subprocess.run(cmd_deployments, capture_output=True, text=True)
        deployments = json.loads(result_deployments.stdout) if result_deployments.stdout else []
        
        return endpoint_info, deployments
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return None, []


def test_endpoint_cli(endpoint_name, resource_group, workspace_name, request_data):
    """Test endpoint using Azure CLI."""
    print(f"\n📡 Testing endpoint: {endpoint_name}")
    print("-" * 60)
    
    # First check endpoint and deployment status
    print("🔍 Checking endpoint status...")
    endpoint_info, deployments = check_endpoint_status(endpoint_name, resource_group, workspace_name)
    
    if not endpoint_info:
        print(f"✗ Cannot access endpoint '{endpoint_name}'")
        print(f"   Make sure the endpoint exists and you have access to it.")
        sys.exit(1)
    
    endpoint_status = endpoint_info.get('provisioning_state', 'Unknown')
    print(f"   Endpoint status: {endpoint_status}")
    
    if not deployments:
        print(f"✗ No deployments found for endpoint '{endpoint_name}'")
        print(f"\n💡 This endpoint exists but has no model deployments.")
        print(f"   You need to deploy a model to this endpoint first.")
        print(f"\n📋 TO FIX THIS:")
        print(f"   1. Run your GitHub Actions pipeline to deploy a model")
        print(f"   2. Or manually deploy:")
        print(f"      az ml online-deployment create --file deployment.yml --resource-group {resource_group} --workspace-name {workspace_name} --all-traffic")
        sys.exit(1)
    
    active_deployments = [d for d in deployments if d.get('provisioning_state') == 'Succeeded']
    if not active_deployments:
        print(f"✗ No active deployments found for endpoint '{endpoint_name}'")
        print(f"   Deployments exist but none are in 'Succeeded' state.")
        for dep in deployments:
            name = dep.get('name', 'Unknown')
            status = dep.get('provisioning_state', 'Unknown')
            print(f"   - {name}: {status}")
        sys.exit(1)
    
    print(f"✓ Found {len(active_deployments)} active deployment(s)")
    
    # Save request data to temporary file
    temp_file = Path("temp_request.json")
    with open(temp_file, 'w') as f:
        json.dump(request_data, f, indent=2)
    
    try:
        # Build Azure CLI command with timeout and better error handling
        cmd = [
            "az", "ml", "online-endpoint", "invoke",
            "--name", endpoint_name,
            "--request-file", str(temp_file),
            "--resource-group", resource_group,
            "--workspace-name", workspace_name
        ]
        
        print(f"Running: {' '.join(cmd)}\n")
        
        # Execute command with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60  # Add 60 second timeout
        )
        
        # Parse and display results
        if result.stdout:
            try:
                response_data = json.loads(result.stdout)
                print("✓ Raw response received:")
                print(json.dumps(response_data, indent=2))
                
                # Extract predictions from MLflow format
                # MLflow models typically return predictions in different formats
                predictions = None
                if isinstance(response_data, list):
                    # Direct array of predictions
                    predictions = response_data
                elif isinstance(response_data, dict):
                    # Look for common prediction keys
                    if 'predictions' in response_data:
                        predictions = response_data['predictions']
                    elif 'outputs' in response_data:
                        predictions = response_data['outputs']
                    elif len(response_data) == 1 and list(response_data.values())[0]:
                        # Single key with prediction data
                        predictions = list(response_data.values())[0]
                
                if predictions is None:
                    print("⚠️  Could not extract predictions from response format")
                    print("   Returning raw response for display")
                    predictions = response_data
                
                return predictions
            except json.JSONDecodeError as e:
                print(f"✗ Error parsing response JSON: {e}")
                print(f"  Raw output: {result.stdout}")
                return None
        else:
            print("✗ No output received from endpoint")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"✗ Request timed out after 60 seconds")
        print(f"   The endpoint may be overloaded or not responding properly.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error invoking endpoint:")
        print(f"  Return code: {e.returncode}")
        print(f"  Error output: {e.stderr}")
        print(f"  Standard output: {e.stdout}")
        
        # Handle specific error types
        error_msg = str(e.stderr).lower()
        if "connection" in error_msg and "reset" in error_msg:
            print(f"\n💡 CONNECTION ERROR:")
            print(f"   Connection was reset by the endpoint.")
            print(f"   This usually means:")
            print(f"   1. The endpoint is not ready or still provisioning")
            print(f"   2. The endpoint has issues with the deployed model")
            print(f"   3. Network connectivity issues")
            print(f"\n📋 TROUBLESHOOTING:")
            print(f"   1. Check if the endpoint is ready: az ml online-endpoint show --name {endpoint_name}")
            print(f"   2. Check deployment status: az ml online-deployment list --endpoint-name {endpoint_name}")
            print(f"   3. Try again in a few minutes if the deployment just finished")
        elif "resourcenotfound" in error_msg:
            print(f"\n💡 RESOURCE NOT FOUND:")
            print(f"   The endpoint or deployment was not found.")
            endpoints = check_endpoints_exist(resource_group, workspace_name)
            if endpoints:
                print(f"\n🔍 Available endpoints in your workspace:")
                for endpoint in endpoints:
                    print(f"   - {endpoint.get('name', 'Unknown')}")
            else:
                print(f"   No endpoints found in workspace.")
        else:
            print(f"\n💡 UNKNOWN ERROR:")
            print(f"   Please check the error message above for details.")
        
        sys.exit(1)
    finally:
        # Clean up temporary file
        if temp_file.exists():
            temp_file.unlink()


def display_results(headers, data, predictions):
    """Display test data alongside predictions."""
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    # Handle different prediction formats
    prediction_list = []
    if predictions:
        if isinstance(predictions, list):
            prediction_list = predictions
        elif isinstance(predictions, dict):
            # Try to extract array of predictions from dict
            for key in ['predictions', 'outputs', 'result']:
                if key in predictions and isinstance(predictions[key], list):
                    prediction_list = predictions[key]
                    break
        elif isinstance(predictions, (int, float)):
            # Single prediction for all samples
            prediction_list = [predictions] * len(data)
    
    # Add predictions to headers if we have them
    has_predictions = bool(prediction_list)
    display_headers = headers + (['Prediction'] if has_predictions else [])
    
    # Calculate column widths for formatting
    col_widths = []
    for i, header in enumerate(display_headers):
        max_width = len(header)
        
        # Check data column width
        if i < len(headers):
            for row in data:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
        
        # Check prediction column width
        if has_predictions and i == len(headers):
            for pred in prediction_list:
                max_width = max(max_width, len(str(pred)))
        
        col_widths.append(max_width + 2)  # Add padding
    
    # Print headers
    header_line = " | ".join(f"{h:>{w-2}}" for h, w in zip(display_headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print data rows
    for i, row in enumerate(data):
        display_row = list(row)
        if has_predictions and i < len(prediction_list):
            display_row.append(str(prediction_list[i]))
        elif has_predictions and len(prediction_list) == 1:
            # Single prediction for all rows
            display_row.append(str(prediction_list[0]))
        
        # Pad each column to its width
        formatted_row = []
        for j, val in enumerate(display_row):
            if j < len(col_widths):
                formatted_row.append(f"{str(val):>{col_widths[j]-2}}")
        
        print(" | ".join(formatted_row))
    
    if not has_predictions:
        print("\n⚠️  No predictions to display")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Test Azure ML deployed model endpoint with diabetes prediction data"
    )
    parser.add_argument(
        "--endpoint-name",
        required=True,
        help="Name of the Azure ML online endpoint"
    )
    parser.add_argument(
        "--resource-group",
        default="rg-mlops-dev-ksh026",
        help="Azure resource group name (default: rg-mlops-dev-ksh026)"
    )
    parser.add_argument(
        "--workspace-name",
        default="mlw-diabetes-dev-ksh026",
        help="Azure ML workspace name (default: mlw-diabetes-dev-ksh026)"
    )
    parser.add_argument(
        "--test-data",
        default="test_data.csv",
        help="Path to test data CSV file (default: test_data.csv)"
    )
    
    args = parser.parse_args()
    
    # Resolve test data path
    test_data_path = Path(__file__).parent / args.test_data
    
    print("=" * 60)
    print("AZURE ML MODEL ENDPOINT TESTING")
    print("=" * 60)
    print(f"Endpoint:       {args.endpoint_name}")
    print(f"Resource Group: {args.resource_group}")
    print(f"Workspace:      {args.workspace_name}")
    print(f"Test Data:      {test_data_path}")
    print("=" * 60)
    
    # Load test data
    headers, data = load_test_data(test_data_path)
    
    # Prepare request
    request_data = prepare_request_data(headers, data)
    
    # Test endpoint
    predictions = test_endpoint_cli(
        args.endpoint_name,
        args.resource_group,
        args.workspace_name,
        request_data
    )
    
    # Display results
    if predictions:
        display_results(headers, data, predictions)
        print("✓ Test completed successfully!")
    else:
        print("\n✗ Test failed - no predictions received")
        sys.exit(1)


if __name__ == "__main__":
    main()
