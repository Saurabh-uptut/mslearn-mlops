# Changes Summary - Resource Name Uniqueness Update

## Problem Solved
Fixed the Terraform deployment issue caused by soft-deleted Azure ML workspace conflicts. All resources now have unique names using a random suffix.

## Files Modified

### 1. `terraform/main.tf`
Updated resource names to include random suffix:

- **Resource Group**: `rg-mlops-dev` → `rg-mlops-dev-{random}`
- **ML Workspace**: `mlw-diabetes-dev` → `mlw-diabetes-dev-{random}`
- **Application Insights**: `appi-mlops-dev` → `appi-mlops-dev-{random}`
- Key Vault and Storage Account already had random suffixes ✓

### 2. `.github/workflows/mlops-pipeline.yml`
Updated the workflow to use GitHub Secrets instead of hardcoded resource names:

```yaml
# Before:
--resource-group "rg-mlops-dev" --workspace-name "mlw-diabetes-dev"

# After:
--resource-group "${{secrets.AZURE_RESOURCE_GROUP}}" --workspace-name "${{secrets.AZURE_WORKSPACE_NAME}}"
```

### 3. New Files Created

#### `terraform/SETUP_INSTRUCTIONS.md`
Comprehensive guide for deploying and configuring the infrastructure.

#### `terraform/get-resource-names.sh`
Helper script to extract resource names from Terraform outputs and display them in a format ready for GitHub Secrets.

## Next Steps

### 1. Deploy Infrastructure
```bash
cd terraform
terraform apply
```

### 2. Get Resource Names
```bash
cd terraform
./get-resource-names.sh
```

### 3. Update GitHub Secrets
Add the following secrets to your GitHub repository:
- `AZURE_RESOURCE_GROUP`
- `AZURE_WORKSPACE_NAME`

See `terraform/SETUP_INSTRUCTIONS.md` for detailed steps.

## Benefits

✅ **No more soft-delete conflicts** - Each deployment gets unique resource names
✅ **Easier parallel environments** - Can create dev/staging/prod simultaneously
✅ **Automated cleanup** - Key Vault auto-purges on destroy
✅ **Better workflow integration** - GitHub Actions now use dynamic resource names
✅ **Terraform validated** - Configuration passes validation checks

## Notes

- The random suffix is 6 lowercase alphanumeric characters
- The suffix is consistent across all resources in a single Terraform state
- To recreate with new names, run `terraform destroy` then `terraform apply`

