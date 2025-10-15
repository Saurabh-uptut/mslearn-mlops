variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "compute_vm_size" {
  description = "VM size for the compute cluster"
  type        = string
  default     = "Standard_DS3_v2"
}

variable "compute_max_nodes" {
  description = "Maximum number of nodes in the compute cluster"
  type        = number
  default     = 4

  validation {
    condition     = var.compute_max_nodes > 0 && var.compute_max_nodes <= 100
    error_message = "Compute max nodes must be between 1 and 100."
  }
}

