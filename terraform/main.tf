terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Random suffix for globally unique resource names
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# Data source for current Azure client configuration
data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "mlops" {
  name     = "rg-mlops-${var.environment}-${random_string.suffix.result}"
  location = var.location

  tags = {
    Environment = var.environment
    Project     = "MLOps-Diabetes"
    ManagedBy   = "Terraform"
  }
}

# Application Insights for monitoring
resource "azurerm_application_insights" "mlops" {
  name                = "appi-mlops-${var.environment}-${random_string.suffix.result}"
  location            = azurerm_resource_group.mlops.location
  resource_group_name = azurerm_resource_group.mlops.name
  application_type    = "web"

  tags = {
    Environment = var.environment
    Project     = "MLOps-Diabetes"
    ManagedBy   = "Terraform"
  }
}

# Key Vault for secrets management
resource "azurerm_key_vault" "mlops" {
  name                     = "kv-mlops-${var.environment}-${random_string.suffix.result}"
  location                 = azurerm_resource_group.mlops.location
  resource_group_name      = azurerm_resource_group.mlops.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
  purge_protection_enabled = false

  tags = {
    Environment = var.environment
    Project     = "MLOps-Diabetes"
    ManagedBy   = "Terraform"
  }
}

# Storage Account for ML artifacts
resource "azurerm_storage_account" "mlops" {
  name                     = "stmlops${var.environment}${random_string.suffix.result}"
  location                 = azurerm_resource_group.mlops.location
  resource_group_name      = azurerm_resource_group.mlops.name
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    Environment = var.environment
    Project     = "MLOps-Diabetes"
    ManagedBy   = "Terraform"
  }
}

# Azure Machine Learning Workspace
resource "azurerm_machine_learning_workspace" "mlops" {
  name                          = "mlw-diabetes-${var.environment}-${random_string.suffix.result}"
  location                      = azurerm_resource_group.mlops.location
  resource_group_name           = azurerm_resource_group.mlops.name
  application_insights_id       = azurerm_application_insights.mlops.id
  key_vault_id                  = azurerm_key_vault.mlops.id
  storage_account_id            = azurerm_storage_account.mlops.id
  public_network_access_enabled = true

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "MLOps-Diabetes"
    ManagedBy   = "Terraform"
  }
}

# Compute Cluster for training jobs
resource "azurerm_machine_learning_compute_cluster" "cpu_cluster" {
  name                          = "cpu-cluster"
  location                      = azurerm_resource_group.mlops.location
  machine_learning_workspace_id = azurerm_machine_learning_workspace.mlops.id
  vm_priority                   = "Dedicated"
  vm_size                       = var.compute_vm_size

  scale_settings {
    min_node_count                       = 0
    max_node_count                       = var.compute_max_nodes
    scale_down_nodes_after_idle_duration = "PT30S"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "MLOps-Diabetes"
    ManagedBy   = "Terraform"
  }
}

