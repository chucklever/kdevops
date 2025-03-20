terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>4.21.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~>2.1"
    }
  }
}

provider "azurerm" {
  features {}

  client_certificate_path     = var.client_certificate_path
  client_certificate_password = var.azure_client_certificate_password
  client_id                   = var.azure_application_id
  subscription_id             = var.azure_subscription_id
  tenant_id                   = var.azure_tenant_id
}
