# AWS alternative — validation is not deployment

This configuration follows the written rubric: VPC, two public and two private
subnets, NAT, EKS, and a managed worker group. EBS CSI with IRSA supplies the
storage driver. Install an AWS load balancer controller appropriate to the
desired public Service before using the shared Helm chart. Define a gp3
StorageClass and set `postgres.storageClass` accordingly.

No AWS deployment is claimed. Provider authentication and real cloud capacity
are required for a meaningful plan and apply; `validate` checks configuration
structure only. Check EKS regional version support before applying.

```powershell
aws sts get-caller-identity
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit admin_cidrs to your actual trusted public address.
terraform init
terraform fmt -check
terraform validate
terraform plan -out=aws.tfplan
terraform apply aws.tfplan
aws eks update-kubeconfig --region ap-south-1 --name labshelf-eks
kubectl get nodes
```

Keep credentials in the normal AWS credential chain, not HCL or tfvars. Keep
state and saved plans outside Git. Single NAT is a classroom cost/availability
tradeoff, not a highly available design. Provisioning incurs AWS costs.
Destroy only after explicit cleanup authorization and record the real result.

References: [EKS module](https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest),
[VPC module](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest).
