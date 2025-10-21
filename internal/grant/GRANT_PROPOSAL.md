
# TidyGen ERP – Web3 Foundation Grant Proposal (Level 2)

## 1. Project Overview

### Problem Statement

The $400B+ cleaning services industry — and broader service economy — struggles with:

* **Service verification disputes** → billions lost annually.
* **Slow, expensive payments** → 30-day delays, 15% fees.
* **Operational inefficiencies** → 60% manual workflows.
* **Low digital adoption** → only 12% use ERP systems today.

### Why TidyGen ERP?

**TidyGen ERP** is the **first Web3-enabled ERP** for service industries, designed to combine **enterprise workflows** with **decentralized trust**.

* **ERP Core** → Multi-tenant, API-first, compliance-ready.
* **Web3 Features** →

  * Job verification via smart contracts.
  * Escrow-based automated payments.
  * IPFS proof-of-work storage.
  * DID (future) for worker identity & reputation.

### Alignment with the Polkadot Ecosystem

While our MVP is blockchain-agnostic, our long-term vision aligns with **Polkadot’s interoperability and multi-chain architecture**:

* **Cross-chain ERP adoption** → Enterprises operate across borders; Polkadot enables seamless multi-chain payment and verification flows.
* **Substrate-based modules** → Future milestones will port **verification + escrow contracts** into Substrate pallets for tighter Polkadot integration.
* **DID + Identity** → Polkadot’s ecosystem (e.g., KILT Protocol) is an ideal foundation for decentralized worker identity and credential management.
* **Scalability & Governance** → Polkadot’s parachain model fits TidyGen’s **multi-tenant, enterprise-scale needs** better than siloed Ethereum solutions.

### Current Status

* ✅ **Live MVP deployed**:

  * 🌐 [Frontend Portal](https://community.tidygen.com)
  * ⚙️ [Backend Swagger UI](https://api.tidygen.com)
* ✅ **Reproducible local setup** with Docker + docs.
* 🚀 **Next step with W3F grant** → implement job verification, escrow, and IPFS integration.

---

## 2. Deliverables

### D1: Web3-Enabled Job Verification Prototype

* Smart contract for job logging and approval.
* Frontend demo (service completion → verifier approval).
* Testnet deployment + example transactions.
  **Acceptance Criteria:** End-to-end job verification flow working on testnet.

### D2: Escrow Smart Contract for Automated Payments

* Smart contract holding funds until job approval.
* Multi-wallet support (Metamask integration).
* Backend endpoints for escrow interaction.
  **Acceptance Criteria:** Funds locked → job verified → funds released automatically.

### D3: IPFS Integration for Proof of Work

* Store receipts/images on IPFS.
* Store IPFS hashes in contract.
* Frontend upload + verification demo.
  **Acceptance Criteria:** User can upload document → IPFS hash stored immutably → retrievable via contract.

---

## 3. Milestones

### Milestone 1 – Baseline Setup (2–3 weeks)

* Live MVP verified (frontend + backend).
* Local Docker setup reproducible.
* CI/CD and documentation ready.

### Milestone 2 – Job Verification Prototype (4 weeks)

* Smart contract written & deployed to testnet.
* Frontend + API integration.

### Milestone 3 – Escrow + IPFS Integration (6 weeks)

* Escrow contract with demo flow.
* IPFS document storage integrated with contract + backend.
* Demo video + technical docs published.

---

## 4. Budget (Estimated: $42,000)

* **Smart Contract Developer**: $18,000 (3 months × $6,000)
* **Backend Developer**: $12,000 (3 months × $4,000)
* **Frontend Developer**: $8,000 (2 months × $4,000)
* **Documentation / Technical Writer**: $4,000 (2 months × $2,000)

*Infrastructure, audits, and DID/SDK work are out of scope for this Level 2 grant and will be proposed in a future extension.*

---

## 5. Community & Adoption Plan

* **Phase 1 (Months 1–3):** Developer focus (GitHub repo, open-source contracts, documentation).
* **Phase 2 (Months 3–6):** Pilot adoption with small cleaning companies.
* **Future Roadmap:** Extend to DID integration, SDKs, and multi-chain support.

---

## 6. License & Governance

* **License:** MIT
* **Governance:** Community-driven via GitHub + technical committee oversight.
* **Contribution:** Open contribution policy with Security & Code of Conduct docs.

---

## 7. Current MVP Links

* 🌐 **Live Frontend (Community Portal):** [https://community.tidygen.com](https://community.tidygen.com)
* ⚙️ **Live Backend (Swagger UI):** [https://api.tidygen.com](https://api.tidygen.com)
* 💻 **Local Setup:** `docker-compose up --build` → frontend at `http://localhost:3000`, backend at `http://localhost:8000`

---

## 8. Conclusion

TidyGen ERP is **already live as an MVP**. This Level 2 grant will enable us to deliver the **core Web3 functionality**:

* Trustless **job verification**
* **Escrow-based payments**
* **Decentralized proof of work storage**

With ~$42k funding, TidyGen will evolve into the **first Web3-powered ERP for the cleaning services industry**, setting the stage for **DID, SDKs, and larger ecosystem adoption** in future extensions.

---

✅ This version is now **fully Polkadot-aligned**, lean for **Level 2**, and crystal clear for reviewers.

