# Contributing and repository policy

This project welcomes contributions and suggestions. Please follow the guidelines below before opening new issues or pull requests.

## Contributor license agreement

Any pull requests or commits require you to agree to The _Modelica Association Contributor License Agreement_ (MA CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://github.com/modelica/ModelicaAssociationCLA.

When you submit a pull request, a bot will automatically determine whether you need to provide a MA CLA and decorate the pull request appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once.

## Reporting issues

Please check the available labels and use them. The label descriptions clarify the kind of issues that can be reported. _Every_ issue must be labeled with _one_ collated-to category label (`infrastructure`, `user-interface`, `GALEC-checks` or `manifest-checks`) denoting the artifacts and/or functionality of the repository the issue is about. The issue also _must_ be categorized if it is a general question, enhancement request or an actual bug (`question`, `enhancement` and `bug` labels). The `documentation` label is optional and used to denote that the issue is about the documentation of its collated-to category. The `invalid` label is used to denote issues that already exists, doesn't seem right or won't be worked on.

## Branch protection and commits/pull requests

The main branch (`main`) of the repository is protected. All work must be done on separate branches, with pull requests to merge your new contributions into `main`. Respective pull requests must be reviewed by at least one code owner of the changed artefacts. Please cf. the `CODEOWNERS` file for who to add as reviewer to your pull request.

A good overview of the implementation is given in the [implementation documentation](documentation/implementation.md). Please read it first before pushing changes; **and** take care your changes are reflected in it (keep it up-to-date).