variable "subscription_id" {
  type        = string
  description = "Subscription to provision. Use TF_VAR_subscription_id or an ignored tfvars file."
}

variable "location" {
  type    = string
  default = "centralindia"
}

variable "project" {
  type    = string
  default = "labshelf"
}

variable "node_size" {
  type    = string
  default = "Standard_D2s_v3"
}

variable "node_count" {
  type    = number
  default = 2
}

variable "kubernetes_version" {
  type    = string
  default = "1.36"
}
