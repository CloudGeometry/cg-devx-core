resource "azurerm_key_vault" "key_vault" {
  name = "${local.name}-kv"

  location            = var.region
  sku_name            = "standard"
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  tags                = local.tags

  enabled_for_deployment          = false
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = false
  enable_rbac_authorization       = true
  purge_protection_enabled        = true
  public_network_access_enabled   = true

  soft_delete_retention_days = 7

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
    virtual_network_subnet_ids = [azurerm_subnet.private_subnet.id]
    ip_rules = ["84.126.33.68"]
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Create",
      "Delete",
      "Get",
      "Purge",
      "Recover",
      "Update",
      "GetRotationPolicy",
      "SetRotationPolicy"
    ]
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  depends_on = [azurerm_subnet.private_subnet]
}
data "azurerm_client_config" "example" {
}

resource "azurerm_role_assignment" "rbac_keyvault_administrator" {
  scope                = azurerm_key_vault.key_vault.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = data.azurerm_client_config.example.object_id
}

resource "random_string" "key_random_suffix" {
  length  = 8
  lower   = true
  upper   = false
  special = false
}

resource "azurerm_key_vault_key" "secret_manager_unseal_kms_key" {
  name         = "secret-manager-unseal-key-${random_string.key_random_suffix.result}"
  key_vault_id = azurerm_key_vault.key_vault.id
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]

  rotation_policy {
    automatic {
      time_before_expiry = "P30D"
    }

    expire_after         = "P90D"
    notify_before_expiry = "P29D"
  }

  depends_on = [azurerm_key_vault.key_vault, azurerm_role_assignment.rbac_keyvault_administrator]
}
