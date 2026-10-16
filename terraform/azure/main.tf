locals {
  tags = { project = var.project, environment = "capstone", managed_by = "terraform" }
}

resource "azurerm_resource_group" "main" {
  name     = "${var.project}-rg"
  location = var.location
  tags     = local.tags
}

resource "azurerm_virtual_network" "main" {
  name                = "${var.project}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.42.0.0/16"]
  tags                = local.tags
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-nodes"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.42.1.0/24"]
}

resource "azurerm_subnet" "services" {
  name                 = "future-services"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.42.2.0/24"]
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.project
  kubernetes_version  = var.kubernetes_version
  sku_tier            = "Free"

  node_provisioning_profile {
    mode = "Manual"
  }

  default_node_pool {
    name            = "system"
    node_count      = var.node_count
    vm_size         = var.node_size
    vnet_subnet_id  = azurerm_subnet.aks.id
    os_disk_size_gb = 64
    max_pods        = 50
    upgrade_settings {
      max_surge = "1"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_policy      = "azure"
    pod_cidr            = "10.244.0.0/16"
    service_cidr        = "10.43.0.0/16"
    dns_service_ip      = "10.43.0.10"
    load_balancer_sku   = "standard"
    outbound_type       = "loadBalancer"
  }

  role_based_access_control_enabled = true
  tags                              = local.tags
}

resource "azurerm_role_assignment" "network" {
  scope                            = azurerm_virtual_network.main.id
  role_definition_name             = "Network Contributor"
  principal_id                     = azurerm_kubernetes_cluster.main.identity[0].principal_id
  skip_service_principal_aad_check = true
}
