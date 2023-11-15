[//]: # (![GitHub]&#40;https://img.shields.io/github/license/CloudGeometry/cg-devx-core&#41;)
[//]: # ([![Contributor Covenant]&#40;https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg&#41;]&#40;code_of_conduct.md&#41;)

> **WORK IN PROGRESS**: Repository is under active development, breaking changes are expected.

# Welcome to CG DevX

Here, at CloudGeometry, we use CG DevX as a Reference Architecture for simplifying the creation and management of DevOps
and Cloud resources, and we've decided to make it available to the public.

While we consider it to be pretty exciting, it's important that you realize that this public version is a pre-alpha
release; there's no guarantee that it will work for you, and it's very likely that things will change before the general
release.

## What is CG DevX?

CG DevX is an all-in-one platform designed to simplify and enhance the development, deployment, and management of
cloud-native applications. Whether you are an experienced platform engineer or just a beginner DevOps starting your
cloud-native journey, CG DevX provides the tools and capabilities to empower your team and streamline your workflows.

## Key Features

### Modular approach

In CG DevX, each module functions independently within its designated area of usage. This isolation ensures that modules
remain self-contained and do not interfere with the functionality of other components. Consequently, any changes or
updates made to one module have minimal impact on the overall system, promoting stability and reliability.

### Flexibility and Customizability

The modular architecture of CG DevX empowers users to tailor their platform experience to meet their unique
requirements.
Because modules are decoupled and autonomous, users can easily customize individual components without affecting the
integrity of the entire system. This flexibility enables teams to curate a platform that aligns precisely with their
specific needs and preferences.

### Efficient Troubleshooting and Maintenance

Isolated modules simplify the troubleshooting and maintenance process in CG DevX. If an issue arises within a specific
module, it can be addressed independently without necessitating an extensive system-wide investigation. This targeted
approach accelerates the resolution of problems, reducing downtime and enhancing the overall platform experience.

### Infrastructure as Code (IaC)

With CG DevX, you can leverage the power of Infrastructure as Code (IaC) to automate the provisioning and management of
your cloud infrastructure. Define your infrastructure using simple configuration files, and CG DevX will handle the
rest.
Say goodbye to manually provisioning and hello to consistent, reproducible environments. CG DevX integrates seamlessly
with
Terraform, one of the leading IaC tools available. Terraform provides a simple, declarative language for defining and
managing infrastructure resources across various cloud providers.

### Continuous Integration and Delivery (CI/CD)

CG DevX offers robust CI/CD capabilities to accelerate your software delivery lifecycle. Set up seamless pipelines to
automate building, testing, and deploying your applications. Integrate with popular version control systems like Git,
and choose from a range of deployment strategies such as rolling updates and canary deployments. Effortlessly deliver
your applications with confidence.

### Kubernetes-based Orchestration

Harness the power of Kubernetes, the leading container orchestration platform, with CG DevX. Benefit from its
scalability, resilience, and flexibility without getting bogged down by its complexities. CG DevX provides a simplified
interface to deploy and manage your services, allowing you to focus on what matters most—building and running your
applications.

### Observability

Gain deep insights into the health and performance of your applications with CG DevX's observability and monitoring
features. Collect and analyze metrics, trace application behavior, and troubleshoot issues effectively. CG DevX
integrates seamlessly with popular monitoring tools, providing real-time visibility and empowering you to make informed
decisions about your systems.

### Incident Response and Automation

CG DevX streamlines incident response to ensure a quick and efficient resolution. Detect, triage, and resolve incidents
with ease. Foster collaboration among team members through dedicated communication channels and easily share incident
reports and updates. Leverage automated runbooks to automate repetitive tasks and improve incident response times.

### Cost Optimization

Optimize your cloud costs with CG DevX's cost management capabilities. Gain insights into resource usage, identify
cost-saving opportunities, and implement effective cost-optimization strategies. Automate cleanups, enforce resource
tagging, and visualize cost allocation with user-friendly dashboards. Take control of your cloud spending and maximize
your return on investment.

## Contributing

Interested in contributing to CG DevX? We're always interested in hearing ideas. Please feel free to message us
at [cgdevx@cloudgeometry.io](mailto:cgdevx@cloudgeometry.io?subject=[GitHub]%20Contributing%20to%20CGDevX) or simply
create a pull request, and we'll be happy to look at it!

## Acknowledgements

In the spirit of open source, we build on the work of others, just as we expect others to build on the work we do. To
that end, we wanted to acknowledge the projects whose code is included in this release:

| Project                                                                    | Description                        |
|----------------------------------------------------------------------------|------------------------------------|
| [Kubefirst](https://github.com/kubefirst/kubefirst)                        | The Kubefirst Open Source Platform | 
| [Kubefirst GitOps template](https://github.com/kubefirst/gitops-template/) | A GitOps infrastructure template   | 
| [Otomi](https://github.com/redkubes/otomi-core)                            | Self-hosted PaaS for Kubernetes    |
