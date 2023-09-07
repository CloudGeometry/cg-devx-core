# Welcome to the CG-DEVX Azure module

This complex module allows you to deploy both a simple configuration in the form of an almost empty kubernetes cluster, and a more complex solution that is more suitable for production.
By default, the firewall configuration is enabled, which is open to the public Internet by Public IP, and the cluster behind it. A more detailed description of the architecture will be in the corresponding chapter.

This configuration is capable of running on a new Azure subscription and uses a mini cluster configuration.

## Prerequisites

- **[AZ tool](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)** is required for full-fledged work.
  
- Kubernetes command-line tool (**[kubectl](https://kubernetes.io/releases/download/)**)

- After, you need to connect to your Azure subscription using **[az tool](https://learn.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-bash?tabs=bash#authenticate-to-azure-via-a-microsoft-account)**

 - **[Azure service principal](https://learn.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-bash?tabs=bash#create-a-service-principal)**
We can use a different authentication method for terraforms, but the Principal service is considered the most optimal.
Service Principal is created with Contributor rights for the entire subscription.
(Optional) Add the User Access Administrator role for the service principal.


To successfully connect to the cluster, you need to install the **kubelogin** tool. You can use **[THIS](https://azure.github.io/kubelogin/install.html)**) guide to install.

## Usage

- Add service principal data to main file (inside of provider block) or environment parameters(or other **[options](https://learn.microsoft.com/en-us/azure/developer/terraform/authenticate-to-azure?tabs=bash#terraform-and-azure-authentication-scenarios)**)
  
- Add your public ssh key to the variable **"ssh_public_key"** inside of main variable file.

- Navigate to the /cg-devx-core/platform/terraform/hosting_provider/ folder (or cd ../../hosting_provider/ if you're in the cloud_azure folder).
  
- You can change a small number of variables inside the main.ft file, for example: region, cluster_name etc. You can find more parameters in the folder with the module - cloud_azure.

- Run terraform

## How to connect to AKS cluster

After successfully deploying the code, you will be able to **[connect to your cluster](https://learn.microsoft.com/en-us/azure/architecture/guide/security/access-azure-kubernetes-service-cluster-api-server#access-the-aks-cluster-over-the-internet)**.
By default, the credentials are merged into the .kube/config file so kubectl can use them. **For full access to the AKS cluster, you need to get administrator credentials**

> az aks get-credentials --name devxaks --resource-group devxaks-rg --admin

If you are using the default settings, you need to run:
> az aks get-credentials --name DevXAks --resource-group DevX-rg

After that, your kubeconfig will be updated automatically.
## Architecture
