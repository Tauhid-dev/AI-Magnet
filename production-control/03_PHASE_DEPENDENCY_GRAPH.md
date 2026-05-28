# Phase Dependency Graph

Last updated: 2026-05-28

```mermaid
flowchart TB
    PR00["PR-00<br/>Visible Roadmap and Memory<br/>verified"]
    PR01["PR-01<br/>Production Authentication<br/>verified"]
    PR02["PR-02<br/>Abuse Protection and Widget Origins<br/>verified"]
    PR03["PR-03<br/>Tenant Isolation and Privacy<br/>verified"]
    PR04["PR-04<br/>Production Infra, TLS, Backups<br/>verified"]
    PR05["PR-05<br/>Real Queue and Worker<br/>next high blocker"]
    PR06["PR-06<br/>Website and Sitemap Ingestion"]
    PR07["PR-07<br/>Document/PDF/DOCX Ingestion"]
    PR08["PR-08<br/>Scalable RAG, Citations, Safety"]
    PR09["PR-09<br/>Onboarding and Widget UX"]
    PR10["PR-10<br/>Monitoring, Metering, Quotas"]
    PR11["PR-11<br/>Billing and Paid Beta Controls"]
    PR12["PR-12<br/>Final Audit and Launch Gate"]

    GateA["Gate A<br/>Controlled Internal Demo<br/>GO WITH CONDITIONS"]
    GateB["Gate B<br/>Secure Private Internet Demo<br/>requires PR-01..PR-05"]
    GateC["Gate C<br/>Real Customer Pilot<br/>requires PR-01..PR-10"]
    GateD["Gate D<br/>Paid Beta<br/>requires PR-01..PR-11"]
    GateE["Gate E<br/>Public Production Launch<br/>requires PR-12 and owner approval"]

    PR00 --> PR01 --> PR02 --> PR03 --> PR04 --> PR05
    PR05 --> PR06
    PR05 --> PR07
    PR06 --> PR08
    PR07 --> PR08
    PR08 --> PR09 --> PR10 --> PR11 --> PR12

    PR00 --> GateA
    PR05 --> GateB
    PR10 --> GateC
    PR11 --> GateD
    PR12 --> GateE

    classDef verified fill:#dcfce7,stroke:#15803d,color:#052e16
    classDef blocker fill:#fee2e2,stroke:#b91c1c,color:#450a0a
    classDef notStarted fill:#f1f5f9,stroke:#64748b,color:#0f172a
    classDef gate fill:#fef3c7,stroke:#b45309,color:#451a03

    class PR00,PR01,PR02,PR03,PR04 verified
    class PR05 blocker
    class PR06,PR07,PR08,PR09,PR10,PR11,PR12 notStarted
    class GateA,GateB,GateC,GateD,GateE gate
```

## Why Gates Block Public Onboarding

PR-01 through PR-05 cover the minimum security and infrastructure requirements before any private internet demo with real risk exposure: production auth, abuse controls, tenant/privacy integrity, TLS/private networking/backups/secrets/scans, and a real worker. Public onboarding is blocked until these controls are verified because the current MVP can otherwise expose accounts, customer data, provider cost, and operational reliability to preventable failure modes.

Real customer pilots require PR-06 through PR-10 because the product workflow depends on safe ingestion, source-grounded RAG, customer setup UX, and operator visibility. Paid beta additionally requires PR-11. Public production launch requires PR-12 and explicit owner approval.
