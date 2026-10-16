variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project" {
  type    = string
  default = "labshelf"
}

variable "kubernetes_version" {
  type    = string
  default = "1.35"
}

variable "admin_cidrs" {
  type        = list(string)
  description = "Trusted public IPv4 CIDRs for the EKS API, for example your current IP /32."
  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrnetmask(cidr)) && cidr != "0.0.0.0/0"])
    error_message = "Supply at least one restricted IPv4 CIDR; 0.0.0.0/0 is not allowed."
  }
}
