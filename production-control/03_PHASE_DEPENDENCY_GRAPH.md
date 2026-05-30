# Phase Dependency Graph

Last updated: 2026-05-30

```mermaid
flowchart TB
    PR00["PR-00<br/>Visible Roadmap and Memory<br/>verified"]
    PR01["PR-01<br/>Production Authentication<br/>verified"]
    PR02["PR-02<br/>Abuse Protection and Widget Origins<br/>verified"]
    PR03["PR-03<br/>Tenant Isolation and Privacy<br/>verified"]
    PR04["PR-04<br/>Production Infra, TLS, Backups<br/>verified"]
    PR05["PR-05<br/>Real Queue and Worker<br/>verified after PR-13A"]
    PR06["PR-06<br/>Website and Sitemap Ingestion<br/>verified"]
    PR07["PR-07<br/>Document/PDF/DOCX Ingestion<br/>verified"]
    PR08["PR-08<br/>Scalable RAG, Citations, Safety<br/>verified"]
    PR09["PR-09<br/>Onboarding and Widget UX<br/>verified after PR-13A"]
    PR10["PR-10<br/>Monitoring, Metering, Quotas<br/>verified after PR-13A"]
    PR11["PR-11<br/>Billing and Paid Beta Controls<br/>verified"]
    PR12["PR-12<br/>Final Audit and Launch Gate<br/>verified"]
    PR12A["PR-12A<br/>Security Corrections<br/>verified<br/>public launch NO-GO pending owner/live evidence"]
    PR13["PR-13<br/>Post-Merge Audit<br/>verified with findings"]
    PR13A["PR-13A<br/>Repository Remediation<br/>verified<br/>High findings closed"]
    PR14["PR-14<br/>External VPS/Staging Validation Umbrella<br/>split into PR-14A/PR-14B"]
    PR14A["PR-14A<br/>GitHub Actions Staging Framework<br/>in progress"]
    PR14B["PR-14B<br/>Owner-Approved Staging Execution<br/>not started"]

    GateA["Gate A<br/>Controlled Internal Demo<br/>GO WITH CONDITIONS"]
    GateB["Gate B<br/>Secure Private Internet Demo<br/>requires PR-01..PR-05"]
    GateC["Gate C<br/>Real Customer Pilot<br/>NO-GO pending PR-14B external evidence"]
    GateD["Gate D<br/>Paid Beta<br/>NO-GO pending PR-14B, owner approval and external evidence"]
    GateE["Gate E<br/>Public Production Launch<br/>NO-GO pending live evidence and owner approval"]

    PR00 --> PR01 --> PR02 --> PR03 --> PR04 --> PR05
    PR05 --> PR06
    PR05 --> PR07
    PR06 --> PR08
    PR07 --> PR08
    PR08 --> PR09 --> PR10 --> PR11 --> PR12 --> PR12A --> PR13 --> PR13A --> PR14 --> PR14A --> PR14B

    PR00 --> GateA
    PR05 --> GateB
    PR14B --> GateC
    PR14B --> GateD
    PR14B --> GateE

    classDef verified fill:#dcfce7,stroke:#15803d,color:#052e16
    classDef blocker fill:#fee2e2,stroke:#b91c1c,color:#450a0a
    classDef high fill:#ffedd5,stroke:#c2410c,color:#431407
    classDef notStarted fill:#f1f5f9,stroke:#64748b,color:#0f172a
    classDef gate fill:#fef3c7,stroke:#b45309,color:#451a03

    class PR00,PR01,PR02,PR03,PR04,PR05,PR06,PR07,PR08,PR09,PR10,PR11,PR12,PR12A,PR13A verified
    class PR13 high
    class PR14 notStarted
    class PR14A high
    class PR14B notStarted
    class GateA,GateB,GateC,GateD,GateE gate
```

## Why Gates Block Public Onboarding

PR-01 through PR-05 cover the minimum repository-controlled security and infrastructure requirements before any private internet demo with real risk exposure: production auth, abuse controls, tenant/privacy integrity, TLS/private networking/backups/secrets/scans, and a real worker. PR-06 and PR-07 add safe ingestion paths, PR-08 adds grounded scalable retrieval, PR-09 adds customer setup UX, PR-10 adds operational visibility and quotas, and PR-11 adds manual paid-beta entitlements.

PR-12 is verified as a repository-controlled launch-gate package. PR-12A adds independent-review security corrections for mandatory production super-admin MFA and Redis-backed application rate limiting. PR-13 adds the post-merge audit and PR-13A closes its repository High findings for worker concurrency-safe job claiming, persisted rate-limit abuse analytics, and reproducible mocked browser/e2e evidence. PR-14A prepares GitHub Actions staging deployment and evidence capture, but PR-14B must still execute owner-approved staging validation. Gate E remains NO-GO because public production still requires owner-approved live evidence for TLS, firewall, backup/restore, worker/Redis, PostgreSQL/pgvector RAG, controlled crawl/document smoke, alerting, quota/abuse smoke, target-environment MFA/rate-limit smoke, and explicit owner approval.
