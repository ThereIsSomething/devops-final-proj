# Azure execution runbook

Azure is the instructor-approved alternative for this demonstration. This creates
a resource group, VNet, two subnets, AKS, and a two-node system pool. The second
subnet is reserved for future services. Azure subnets are not equivalents of AWS
public subnets; AKS manages load balancer networking and its node resource group.

Authenticate with `az login`. Check subscription policy, regional/family vCPU
quota, available Kubernetes versions, and SKU restrictions before planning.

```powershell
$env:TF_VAR_subscription_id = az account show --query id -o tsv
terraform init
terraform fmt -check
terraform validate
terraform plan -out=azure.tfplan
terraform apply azure.tfplan
az aks get-credentials --resource-group labshelf-rg --name labshelf-aks
kubectl get nodes
```

State and saved plans stay local and are ignored. Back up state securely outside
Git before changing machines. Do not expose kubeconfig or Terraform state in
screenshots. The Free AKS tier has no financially backed control-plane SLA;
nodes, disks, public IP, bandwidth, and load balancer still incur charges.

Two D2s_v3 nodes consume four DSv3 vCPUs. Upgrade surge may require another node;
check family quota before upgrading. No automatic cleanup is configured.

After evaluation and an explicit cleanup instruction, run `terraform destroy`
from this directory and capture its actual result.

References: [AKS Terraform quickstart](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-terraform),
[AzureRM cluster resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster).
