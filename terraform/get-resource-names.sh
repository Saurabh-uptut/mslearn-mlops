#!/bin/bash
# Helper script to extract Terraform outputs for GitHub Secrets

cd "$(dirname "$0")"

echo "=== Azure ML Resource Names ==="
echo ""
echo "Add these to your GitHub Secrets:"
echo "(Settings → Secrets and variables → Actions)"
echo ""
echo "Secret Name: AZURE_RESOURCE_GROUP"
echo "Secret Value: $(terraform output -raw resource_group_name)"
echo ""
echo "Secret Name: AZURE_WORKSPACE_NAME"
echo "Secret Value: $(terraform output -raw workspace_name)"
echo ""
echo "=== Other Resource Information ==="
echo ""
echo "Storage Account: $(terraform output -raw storage_account_name)"
echo "Key Vault: $(terraform output -raw key_vault_name)"
echo "Application Insights: $(terraform output -raw application_insights_name)"
echo "Compute Cluster: $(terraform output -raw compute_cluster_name)"
echo ""
echo "=== Quick Copy Commands ==="
echo ""
echo "# Copy these commands to set environment variables locally:"
echo "export AZURE_RESOURCE_GROUP=\"$(terraform output -raw resource_group_name)\""
echo "export AZURE_WORKSPACE_NAME=\"$(terraform output -raw workspace_name)\""

