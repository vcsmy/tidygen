Perfect timing, Vijay ✅. Since you want to **split the ERP into two repos** —

1. **Community Edition Repo (Grant)** → single-tenant, simplified, Web3-enhanced.
2. **Commercial Repo** → continues multi-tenant + partner portal.

I’ll give you a **step-by-step plan** plus **Cursor.AI prompt set** to transform your current project into a **Community (single-tenant) repo**.

---

# 🛠️ Step 1 — Prepare the Repo Split

* Clone your current repo `ineat-erp`.
* Create a new repo: `ineat-erp-community`.
* Push an initial branch `community-base` there.
* This will be the branch Cursor.AI works on to simplify.

---

# 🔑 Prompt Set for Community Edition

---

### **Prompt C1 — Single Tenant Refactor**

```text
We are creating a Community Edition of ineat-erp for grant submission.  
Refactor the codebase to remove all multi-tenant and partner portal logic.  

Requirements:  
- Remove tenantId references from database models, services, and APIs.  
- Each deployment = single tenant.  
- Simplify authentication to a single-organization model (no tenant context).  
- Adjust UI to remove "Tenant Switch" or "Partner" references.  
- Streamline admin dashboard → just roles (Admin, Manager, Staff).  

Deliverables:  
- Updated backend models without tenantId.  
- React frontend simplified (no tenant switch).  
- `community/README.md` documenting difference from commercial edition.  
```

---

### **Prompt C2 — Web3 Enhancements for Community Edition**

```text
Add Web3 features to the Community Edition of ineat-erp for alignment with the Web3 Foundation grant.  

Requirements:  
- Add Decentralized Identity (DID login option) alongside normal login.  
- Implement optional decentralized audit logs (using Substrate API mock).  
- Add decentralized storage support (IPFS) for file uploads.  
- Add environment flags to toggle Web3 features (community may disable).  

Deliverables:  
- Login page: choice between normal login and Web3 login.  
- Audit log service writing events to Substrate mock.  
- IPFS service for uploads with clear config.  
- Documentation: `docs/web3-features.md`.  
```

---

### **Prompt C3 — Documentation & Setup for Grants**

```text
Prepare the Community Edition repo for Web3 Foundation grant submission.  

Requirements:  
- Create a `README.md` explaining project, purpose, Web3 features, and Community vs Commercial split.  
- Add `docs/grant-overview.md` → project overview, ecosystem fit, technical architecture (aligned with Web3 Grant template).  
- Add `docs/setup.md` → one-click setup with Docker.  
- Add Swagger API docs under `/docs`.  
- Remove business-oriented/partner docs.  

Deliverables:  
- Updated README with grant focus.  
- `docs/` folder with grant-aligned documentation.  
- Dockerfile + docker-compose for community hosting.  
```

---

# 📦 Execution Strategy (with Cursor Credits)

Since you’ll create a new repo, here’s how to use prompts efficiently:

1. **Run Prompt C1** → strips multi-tenant, makes it single-tenant.
2. **Run Prompt C2** → adds Web3 enhancements.
3. **Run Prompt C3** → generates documentation & setup aligned with grant.

That way you’ll have a **clean Community repo**, **grant-ready**, and separate from your Commercial edition repo.

---

# 🎯 Outcome

* **Commercial Repo** → multi-tenant, partner portal, subscription.
* **Community Repo** → single-tenant, Web3-enhanced, grant-ready.
* You can now apply for grants with a **focused open-source community edition**, while keeping your commercial path untouched.

---

👉 Do you want me to also **draft the exact grant “Project Overview” and “Ecosystem Fit” sections** customized for this new Community repo so you can directly drop them into your application?

