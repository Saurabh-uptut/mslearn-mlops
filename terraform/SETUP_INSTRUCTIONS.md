# Terraform Setup Instructions

## Overview
This Terraform configuration creates Azure ML resources with unique names using a random suffix. This avoids conflicts with soft-deleted resources.

## Updated Resource Naming

All resources now include a random 6-character suffix:

- Resource Group: `rg-mlops-{environment}-{random}`
- ML Workspace: `mlw-diabetes-{environment}-{random}`
- Application Insights: `appi-mlops-{environment}-{random}`
- Key Vault: `kv-mlops-{environment}-{random}`
- Storage Account: `stmlops{environment}{random}`

## Step-by-Step Setup

### 1. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform apply
```

Review the plan and type `yes` to proceed.

### 2. Get Resource Names

After deployment completes, get the resource names:

```bash
terraform output -json
```

Or get specific values:

```bash
terraform output workspace_name
terraform output resource_group_name
```

### 3. Update GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **AZURE_RESOURCE_GROUP**: Use the value from `terraform output resource_group_name`
2. **AZURE_WORKSPACE_NAME**: Use the value from `terraform output workspace_name`

Example commands to get values:

```bash
# Get resource group name
echo "AZURE_RESOURCE_GROUP=$(terraform output -raw resource_group_name)"

# Get workspace name
echo "AZURE_WORKSPACE_NAME=$(terraform output -raw workspace_name)"
```

### 4. Quick Setup Script

You can use this script to extract and display the values:

```bash
#!/bin/bash
cd terraform

echo "=== Azure ML Resource Names ==="
echo ""
echo "Add these to your GitHub Secrets:"
echo ""
echo "AZURE_RESOURCE_GROUP=$(terraform output -raw resource_group_name)"
echo "AZURE_WORKSPACE_NAME=$(terraform output -raw workspace_name)"
echo ""
echo "Other resource names:"
echo "Storage Account: $(terraform output -raw storage_account_name)"
echo "Key Vault: $(terraform output -raw key_vault_name)"
echo "Application Insights: $(terraform output -raw application_insights_name)"
```

Save this as `get-resource-names.sh` and run:

```bash
chmod +x get-resource-names.sh
./get-resource-names.sh
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

This will properly clean up all resources, including purging the Key Vault (as configured in the provider settings).

## Notes

- The random suffix ensures resource names are globally unique
- The Key Vault is configured with `purge_soft_delete_on_destroy = true` for easier cleanup
- ML Workspaces may still be soft-deleted; if recreating, you may need to wait or manually purge

