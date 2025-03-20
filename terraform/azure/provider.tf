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

  client_id                   = var.application_id
  client_certificate_path     = var.client_certificate_path
  client_certificate_password = var.client_certificate_password
  subscription_id             = var.azure_subscription_id
  tenant_id                   = var.tenant_id
}
