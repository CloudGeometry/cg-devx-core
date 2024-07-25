# Contributing

Before contributing to this repository, please discuss your proposed changes with the repository owners through an issue, email, or any other available method."

Note: Our community thrives by adhering to a Code of Conduct, which we expect all participants to follow in all project interactions.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[How Can I Contribute?](#how-can-i-contribute)

* [Reporting Bugs](#reporting-bugs)
* [Suggesting Enhancements](#suggesting-enhancements)
* [Pull Request Process](#pull-request-process)

[Styleguide](#styleguide)

* [Git Commit Messages](#git-commit-messages)
* [Python Styleguide](#python-styleguide)
* [Documentation Styleguide](#documentation-styleguide)

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By
participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report.
To submit a bug report, first verify that your issue hasn't been addressed by checking the list below. This helps avoid duplicate reports.

> Note: If you find a Closed issue that seems like it is the same thing that you're experiencing, open a new issue and
> include a link to the original issue in the body of your new one.

#### Before Submitting A Bug

* **Determine which components of the platform cause problem**
* **Check the FAQs, git pages and forums of those components to identify if the problem is with component itself**
* **Perform a [cursory search](https://github.com/CloudGeometry/cgdevx-core/issues)** to see if the problem has already
  been reported. Please review the list to see if a similar suggestion has already been submitted.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue and provide the
following information by filling in [the template](ISSUE_TEMPLATE.md).

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem
* **Describe the exact steps which reproduce the problem** in as many details as possible
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/paste
  snippets, which you use. If you're providing snippets in the issue,
  use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines)
  and [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that
  behavior
* **Explain which behavior you expected to see instead and why**

Provide more context by answering these questions:

* **Did the problem start happening recently** (e.g. after updating to a new version(s) of packages) or was this always
  a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version?** What's the most
  recent version in which the problem does not happen?
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which
  conditions it normally happens

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor
improvements. Following these guidelines helps maintainers and the community understand your suggestion.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you
might find out that you don't need to create one. When you are creating an enhancement suggestion,
please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill
in [the template](ISSUE_TEMPLATE.md), including the steps that you imagine you would take if the feature you're
requesting existed.

#### Before Submitting An Enhancement Suggestion

* **Check if enhancement is implemented in existing component of pipeline or there is an existing component with
  desired functionality**
* **Perform a [cursory search](https://github.com/CloudGeometry/cgdevx-core/issues)** to see if the enhancement has
  already been suggested. If it has, add a comment to the existing issue instead of opening a new one

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on
that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible
* **Provide specific examples to demonstrate the steps**. Include copy/paste snippets which you use in those examples,
  as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines)
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why
* **Explain why this enhancement would be useful** to users

### Pull Request Process

* Fill in [the template](PULL_REQUEST_TEMPLATE.md)
* Avoid including issue numbers in the PR title to maintain clarity. Instead, reference issue numbers in the PR description if necessary.
* Follow the [Python](#python-styleguide) styleguide
* Document new code based on the [Documentation Styleguide](#documentation-styleguide)
* Update the corresponding README.md with details of changes.

> You can get more info on creating pull requests [here](https://help.github.com/articles/creating-a-pull-request/)

## Styleguide

### Git Commit Messages

Please use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) with the following change
types:
`feat`, `fix`, `chore`, `reafactor`, `docs`, `test`

* Write commit messages in the present tense, e.g., 'Add feature' rather than 'Added feature.'
* Use the imperative mood ("Move logic to..." not "Moves logic to...")
* Limit the first line to 72 characters or fewer
* To indicate Breaking Change appends a ! after the type/scope
* Reference issues and pull requests after the first line

### Python Styleguide

* We are using Python 3.10
* Use [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Additionally, use [flake8](https://flake8.pycqa.org/en/latest/)

### IaC (Terraform) Styleguide

* We follow the [official HashiCorp style guide](https://developer.hashicorp.com/terraform/language/syntax/style) for
  Terraform.

### Documentation Styleguide

* Document all that may not be clear to you
* Use Markdown
