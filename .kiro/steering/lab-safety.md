---
inclusion: always
---

# Lab safety

Agents **author** the walkthrough; they do **not** create IoT Things, certificates,
Greengrass deployments, or IAM roles unless the operator has opted in.

## Opt-in

```bash
export GG_EDGE_ALLOW_AWS=1
```

Without this, the Kiro hook `guard-aws-mutations` blocks mutating `aws` / Terraform /
CDK / SAM / CloudFormation deploy-destroy style commands. Read-only `describe` /
`list` / `get` / `sts get-*` remain allowed.

## Cost and leftovers

- IoT Core Things and certificates are cheap but leave clutter; delete certs from
  Things before deleting Things.
- Greengrass deployments and local Nucleus processes should be stopped and
  unregistered as documented in teardown.
- Never leave long-lived admin policies attached for “demo convenience.”

## Operator responsibility

Only the human runs mutating commands against a real account. Agents paste
commands into docs/scripts and verify with read-only checks when helpful.
