# Pilot Plan Template

Objective
- Validate the Service Verification flow in a small real-world environment and gather metrics & feedback.

Scope
- One partner (small cleaning company / operations team) or internal dataset.
- Duration: 4 weeks pilot.
- Success criteria:
  - 100 verified service records processed end-to-end.
  - Zero critical security issues.
  - Partner signs a short pilot acceptance note.

Timeline
- Week 0: Setup, onboarding, contract deployment to Westend or private testnet.
- Week 1: Integration & training (connect ERP backend to SDK/API).
- Week 2-3: Pilot operations (daily submissions and metrics collection).
- Week 4: Analysis, final demo, partner feedback.

Deliverables
- Pilot deployment (testnet or private node).
- Pilot report: metrics, logs, partner statement.
- List of issues discovered and remediation plan.

Data & Access
- Pilot partner provides anonymized service events or uses the demo UI.
- Access to test accounts will be provisioned with instructions.

Monitoring & Metrics
- Transactions processed per day
- Average latency per verification
- Success / failure rates
- Observability: sample logs and Prometheus metrics (if integrated)

Risk & Mitigations
- Data privacy: use anonymized IDs.
- Node availability: use robust hosting or provide local runbook.
- Security: limit funds and use testnet tokens.

Sign-off
- Partner signature + demo video required for pilot acceptance.
```