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


def test_endpoint_cli(endpoint_name, resource_group, workspace_name, request_data):
    """Test endpoint using Azure CLI."""
    print(f"\n📡 Testing endpoint: {endpoint_name}")
    print("-" * 60)
    
    # Save request data to temporary file
    temp_file = Path("temp_request.json")
    with open(temp_file, 'w') as f:
        json.dump(request_data, f, indent=2)
    
    try:
        # Build Azure CLI command
        cmd = [
            "az", "ml", "online-endpoint", "invoke",
            "--name", endpoint_name,
            "--request-file", str(temp_file),
            "--resource-group", resource_group,
            "--workspace-name", workspace_name
        ]
        
        print(f"Running: {' '.join(cmd)}\n")
        
        # Execute command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse and display results
        if result.stdout:
            predictions = json.loads(result.stdout)
            print("✓ Predictions received:")
            print(json.dumps(predictions, indent=2))
            return predictions
        else:
            print("✗ No output received from endpoint")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error invoking endpoint:")
        print(f"  Error: {e.stderr}")
        
        # Check if it's a "ResourceNotFound" error
        if "ResourceNotFound" in str(e.stderr):
            print(f"\n💡 TROUBLESHOOTING:")
            print(f"   The endpoint '{endpoint_name}' was not found.")
            print(f"   This means you need to deploy a model first.")
            print(f"\n🔍 Available endpoints in your workspace:")
            
            endpoints = check_endpoints_exist(resource_group, workspace_name)
            if endpoints:
                for endpoint in endpoints:
                    print(f"   - {endpoint.get('name', 'Unknown')}")
                print(f"\n💡 Try using one of the existing endpoints above.")
            else:
                print(f"   No endpoints found in workspace.")
                print(f"\n📋 NEXT STEPS:")
                print(f"   1. First, register your trained model")
                print(f"   2. Then deploy it to an endpoint using:")
                print(f"      az ml online-endpoint create --file endpoint.yml")
                print(f"      az ml online-deployment create --file deployment.yml")
                print(f"\n   Or follow the documentation in:")
                print(f"   mslearn-mlops/documentation/06-deploy-model.md")
        
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing response: {e}")
        print(f"  Raw output: {result.stdout}")
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
    
    # Add predictions to headers if we have them
    display_headers = headers + (['Prediction'] if predictions else [])
    
    # Calculate column widths for formatting
    col_widths = []
    for i, header in enumerate(display_headers):
        max_width = len(header)
        for row in data:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)  # Add padding
    
    # Print headers
    header_line = " | ".join(f"{h:>{w-2}}" for h, w in zip(display_headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print data rows
    for i, row in enumerate(data):
        display_row = list(row)
        if predictions and i < len(predictions):
            display_row.append(predictions[i])
        
        # Pad each column to its width
        formatted_row = []
        for j, val in enumerate(display_row):
            if j < len(col_widths):
                formatted_row.append(f"{str(val):>{col_widths[j]-2}}")
        
        print(" | ".join(formatted_row))
    
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
