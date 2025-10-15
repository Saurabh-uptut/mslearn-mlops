output "workspace_name" {
  description = "Name of the Azure ML workspace"
  value       = azurerm_machine_learning_workspace.mlops.name
}

output "workspace_id" {
  description = "ID of the Azure ML workspace"
  value       = azurerm_machine_learning_workspace.mlops.id
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.mlops.name
}

output "compute_cluster_name" {
  description = "Name of the compute cluster"
  value       = azurerm_machine_learning_compute_cluster.cpu_cluster.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.mlops.name
}

output "key_vault_name" {
  description = "Name of the key vault"
  value       = azurerm_key_vault.mlops.name
}

output "application_insights_name" {
  description = "Name of the Application Insights instance"
  value       = azurerm_application_insights.mlops.name
}

