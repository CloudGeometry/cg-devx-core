#!/bin/bash
REGION=eu-north-1
if [[ ${1} == '' ]]; then echo "Usage: ./update-context.sh <cluster-name>"; exit 1; fi
test -x "`which aws`" || echo exit 1
if [[ `aws configure get region`${AWS_REGION} == "" ]]
then
    export AWS_REGION=${REGION}
fi   
aws eks update-kubeconfig --name ${1}
