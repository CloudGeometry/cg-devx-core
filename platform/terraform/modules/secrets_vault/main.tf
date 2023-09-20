terraform {

  required_providers {
    vault = {
      source = "hashicorp/vault"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
    }
  }
}


