#!/usr/bin/env python3
"""
Helper script to list available Azure ML endpoints and models.
Useful for checking what resources exist before testing.
"""

import argparse
import json
import subprocess
import sys


def run_az_command(cmd):
    """Run Azure CLI command and return parsed JSON output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout) if result.stdout else []
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error running command {' '.join(cmd)}: {e}")
        return []


def list_endpoints(resource_group, workspace_name):
    """List all online endpoints in the workspace."""
    print("🔍 ONLINE ENDPOINTS:")
    print("-" * 40)
    
    cmd = ["az", "ml", "online-endpoint", "list", 
           "--resource-group", resource_group,
           "--workspace-name", workspace_name, 
           "--output", "json"]
    
    endpoints = run_az_command(cmd)
    
    if endpoints:
        for endpoint in endpoints:
            name = endpoint.get('name', 'Unknown')
            status = endpoint.get('provisioningState', 'Unknown')
            print(f"  📍 {name} (Status: {status})")
    else:
        print("  ❌ No endpoints found")
    
    print()


def list_models(resource_group, workspace_name):
    """List all registered models in the workspace."""
    print("🤖 REGISTERED MODELS:")
    print("-" * 40)
    
    cmd = ["az", "ml", "model", "list", 
           "--resource-group", resource_group,
           "--workspace-name", workspace_name, 
           "--output", "json"]
    
    models = run_az_command(cmd)
    
    if models:
        for model in models:
            name = model.get('name', 'Unknown')
            version = model.get('version', 'Unknown')
            description = model.get('description', 'No description')
            print(f"  🎯 {name} (v{version})")
            if description and description != 'No description':
                print(f"     {description}")
    else:
        print("  ❌ No models found")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="List Azure ML endpoints and models"
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
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AZURE ML RESOURCES INVENTORY")
    print("=" * 60)
    print(f"Resource Group: {args.resource_group}")
    print(f"Workspace:      {args.workspace_name}")
    print("=" * 60)
    
    list_endpoints(args.resource_group, args.workspace_name)
    list_models(args.resource_group, args.workspace_name)
    
    print("💡 TIPS:")
    print("  - Use existing endpoint names with test_endpoint.py")
    print("  - If no endpoints exist, you need to deploy a model first")
    print("  - Follow docs/06-deploy-model.md for deployment steps")


if __name__ == "__main__":
    main()
