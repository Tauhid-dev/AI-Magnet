# Staging Auto-Deploy Plan

PR-14A keeps staging deployment manual by default. The deployment workflow uses `workflow_dispatch` plus GitHub Environment approval so the owner controls when staging secrets are released.

## Option A: Manual-First Deployment

Current PR-14A behaviour:

```yaml
on:
  workflow_dispatch:
```

Use this until staging deploy, smoke checks, evidence capture, backup, restore, and rollback are proven with synthetic data.

## Option B: Auto-Deploy After Merge

Later only, after owner approval and repeated successful manual staging runs:

```yaml
on:
  push:
    branches:
      - master
```

This must keep the `staging` Environment approval gate unless the owner explicitly decides to remove it. Do not expose staging secrets to forked pull requests.

## Option C: Tag-Based Staging Deployment

For release-candidate style validation:

```yaml
on:
  push:
    tags:
      - "staging-*"
```

This allows explicit promotion of a known commit to staging without deploying every merge.

## Recommendation

Keep manual deployment with required Environment reviewers until PR-14B provides real staging evidence for:

- TLS and renewal;
- firewall/private-port proof;
- backup and restore drill;
- live PostgreSQL/pgvector smoke;
- live Redis worker and multi-worker job claim smoke;
- controlled website/document ingestion;
- RAG citation smoke;
- rate-limit analytics and quota evidence;
- monitoring/logging proof.

Public production launch remains `NO-GO` until PR-14B and the final owner launch approval are complete.
