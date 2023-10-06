eks_permissions: [str] = [
    "eks:CreateCluster",
    "eks:CreateNodegroup",
    "eks:DeleteCluster",
    "eks:DeleteNodegroup",
    "eks:DeregisterCluster",
    "eks:DescribeCluster",
    "eks:DescribeIdentityProviderConfig",
    "eks:DescribeNodegroup",
    "eks:DescribeUpdate",
    "eks:ListClusters",
    "eks:ListIdentityProviderConfigs",
    "eks:ListNodegroups",
    "eks:ListTagsForResource",
    "eks:ListUpdates",
    "eks:RegisterCluster",
    "eks:TagResource",
    "eks:UntagResource",
    "eks:UpdateClusterConfig",
    "eks:UpdateClusterVersion",
    "eks:UpdateNodegroupConfig",
    "eks:UpdateNodegroupVersion"
]

s3_permissions: [str] = [
    "s3:CreateAccessPoint",
    "s3:CreateBucket",
    "s3:DeleteAccessPoint",
    "s3:DeleteAccessPointPolicy",
    "s3:DeleteBucket",
    "s3:DeleteBucketPolicy",
    "s3:DeleteObject",
    "s3:DeleteObjectTagging",
    "s3:DeleteObjectVersion",
    "s3:DeleteObjectVersionTagging",
    "s3:GetAccessPoint",
    "s3:GetAccessPointPolicy",
    "s3:GetBucketAcl",
    "s3:GetBucketLocation",
    "s3:GetObject",
    "s3:ListAccessPoints",
    "s3:ListBucket",
    "s3:ListBucketVersions",
    "s3:PutAccessPointPolicy",
    "s3:PutBucketPolicy",
    "s3:PutBucketTagging",
    "s3:PutBucketVersioning",
    "s3:PutEncryptionConfiguration",
    "s3:PutLifecycleConfiguration",
    "s3:PutMetricsConfiguration",
    "s3:PutObject",
    "s3:PutObjectAcl"
]

vpc_permissions: [str] = [
    "ec2:DescribeAccountAttributes",
    "ec2:DescribeAddresses",
    "ec2:DescribeAvailabilityZones",
    "ec2:DescribeClassicLinkInstances",
    "ec2:DescribeClientVpnEndpoints",
    "ec2:DescribeCustomerGateways",
    "ec2:DescribeDhcpOptions",
    "ec2:DescribeEgressOnlyInternetGateways",
    "ec2:DescribeFlowLogs",
    "ec2:DescribeInternetGateways",
    "ec2:DescribeManagedPrefixLists",
    "ec2:DescribeMovingAddresses",
    "ec2:DescribeNatGateways",
    "ec2:DescribeNetworkAcls",
    "ec2:DescribeNetworkInterfaceAttribute",
    "ec2:DescribeNetworkInterfacePermissions",
    "ec2:DescribeNetworkInterfaces",
    "ec2:DescribePrefixLists",
    "ec2:DescribeRouteTables",
    "ec2:DescribeSecurityGroupReferences",
    "ec2:DescribeSecurityGroups",
    "ec2:DescribeSecurityGroupRules",
    "ec2:DescribeStaleSecurityGroups",
    "ec2:DescribeSubnets",
    "ec2:DescribeTags",
    "ec2:DescribeTrafficMirrorFilters",
    "ec2:DescribeTrafficMirrorSessions",
    "ec2:DescribeTrafficMirrorTargets",
    "ec2:DescribeTransitGateways",
    "ec2:DescribeTransitGatewayVpcAttachments",
    "ec2:DescribeTransitGatewayRouteTables",
    "ec2:DescribeVpcAttribute",
    "ec2:DescribeVpcClassicLink",
    "ec2:DescribeVpcClassicLinkDnsSupport",
    "ec2:DescribeVpcEndpoints",
    "ec2:DescribeVpcEndpointConnectionNotifications",
    "ec2:DescribeVpcEndpointConnections",
    "ec2:DescribeVpcEndpointServiceConfigurations",
    "ec2:DescribeVpcEndpointServicePermissions",
    "ec2:DescribeVpcEndpointServices",
    "ec2:DescribeVpcPeeringConnections",
    "ec2:DescribeVpcs",
    "ec2:DescribeVpnConnections",
    "ec2:DescribeVpnGateways",
    "ec2:GetManagedPrefixListAssociations",
    "ec2:GetManagedPrefixListEntries"
]

iam_permissions: [str] = [
    "iam:AddUserToGroup",
    "iam:AttachGroupPolicy",
    "iam:AttachRolePolicy",
    "iam:AttachUserPolicy",
    "iam:ChangePassword",
    "iam:CreateAccessKey",
    "iam:CreateGroup",
    "iam:CreateInstanceProfile",
    "iam:CreatePolicy",
    "iam:CreatePolicyVersion",
    "iam:CreateRole",
    "iam:CreateUser",
    "iam:DeleteGroup",
    "iam:DeleteGroupPolicy",
    "iam:DeleteInstanceProfile",
    "iam:DeletePolicy",
    "iam:DeletePolicyVersion",
    "iam:DeleteRole",
    "iam:DeleteRolePolicy",
    "iam:DeleteServiceLinkedRole",
    "iam:DeleteUser",
    "iam:DeleteUserPolicy",
    "iam:DetachGroupPolicy",
    "iam:DetachRolePolicy",
    "iam:DetachUserPolicy",
    "iam:GetAccountEmailAddress",
    "iam:GetAccountName",
    "iam:GetGroup",
    "iam:GetInstanceProfile",
    "iam:GetPolicy",
    "iam:GetPolicyVersion",
    "iam:GetRole",
    "iam:GetRolePolicy",
    "iam:GetSSHPublicKey",
    "iam:GetUser",
    "iam:GetUserPolicy",
    "iam:ListAccessKeys",
    "iam:ListAttachedGroupPolicies",
    "iam:ListAttachedRolePolicies",
    "iam:ListAttachedUserPolicies",
    "iam:ListGroupPolicies",
    "iam:ListGroups",
    "iam:ListPolicies",
    "iam:ListPolicyTags",
    "iam:ListPolicyVersions",
    "iam:ListRolePolicies",
    "iam:ListRoleTags",
    "iam:ListRoles",
    "iam:ListUserPolicies",
    "iam:ListUserTags",
    "iam:ListUsers",
    "iam:PutGroupPolicy",
    "iam:PutRolePermissionsBoundary",
    "iam:PutRolePolicy",
    "iam:PutUserPermissionsBoundary",
    "iam:PutUserPolicy",
    "iam:UpdateGroup",
    "iam:UpdateRole"
]

own_iam_permissions: [str] = [
    "iam:ChangePassword",
    "iam:GetUser",
    "iam:CreateAccessKey",
    "iam:DeleteAccessKey",
    "iam:ListAccessKeys",
    "iam:UpdateAccessKey",
    "iam:GetAccessKeyLastUsed",
    "iam:DeleteSSHPublicKey",
    "iam:GetSSHPublicKey",
    "iam:ListSSHPublicKeys",
    "iam:UpdateSSHPublicKey",
    "iam:UploadSSHPublicKey"
]
