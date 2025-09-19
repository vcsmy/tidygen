Great! Here’s the **usage.md** — a detailed step-by-step guide for installing, running, authenticating, generating contracts, and deploying them.

---

````markdown
# Usage Guide - tidygen

## Introduction

This document provides detailed instructions on how to install, configure, and use TidyGen, including decentralized identity (DID) login, AI-powered contract generation, and deployment on Substrate-based blockchains.

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js** v18 or higher  
- **pnpm** package manager  
- **Rust toolchain** (`rustup`, `cargo`) for contract compilation  
- **Docker** (optional, for containerized environments)  
- A **DID wallet/provider** compatible with your DID method  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/vcsmy/tidygen.git
cd tidygen
````

2. Install dependencies using pnpm:

```bash
pnpm install
```

---

## Running the Application

### Start the Backend

```bash
pnpm run start:backend
```

This command starts the Node.js backend server responsible for authentication and AI contract generation APIs.

### Start the Frontend

In a new terminal window:

```bash
pnpm run start:frontend
```

This launches the React frontend app accessible at `http://localhost:3000`.

---

## User Authentication (DID Login)

1. On the frontend login page, choose your preferred DID wallet/provider (e.g., Polkadot.js extension, or other compatible wallets).
2. Authenticate using your decentralized identity. This process involves cryptographic proof verification ensuring secure and passwordless login.
3. Upon successful login, you will be redirected to the contract generation dashboard.

---

## Generating Smart Contracts

1. On the dashboard, fill in the required contract parameters such as:

   * Contract type (e.g., NFT, Token, DAO)
   * Desired functionality or modules
   * Configuration parameters

2. Submit the form to request contract generation.

3. The backend will process the input, call the AI API, and return generated contract source code.

4. Review the generated contract code in the built-in editor with syntax highlighting. Modify if necessary.

---

## Deploying Contracts to Substrate

1. Connect your wallet via the frontend to a supported Substrate network.

2. Use the deploy button to compile and deploy the contract on-chain using the Polkadot.js SDK integration.

3. Monitor transaction status and contract deployment results within the app.

---

## Running Tests

To run the full test suite, including backend and frontend tests:

```bash
pnpm run test
```

Tests cover authentication flows, API endpoints, AI generation integration, and UI components.

---

## Troubleshooting & Tips

* Ensure your DID wallet/provider supports the DID method implemented by the app.
* Verify environment variables for AI API keys are set correctly in the backend.
* Use Rust toolchain to compile contracts manually if needed for debugging.
* For any issues, please open an issue on the GitHub repo.

---

## Additional Resources

* [Polkadot.js Extension](https://polkadot.js.org/extension/)
* [Substrate Developer Hub](https://substrate.dev/)
* [Decentralized Identifiers (DIDs) W3C Spec](https://www.w3.org/TR/did-core/)
* [OpenAI API Documentation](https://beta.openai.com/docs/)

---

## Summary

This guide walks you through the entire TidyGen workflow—from authentication, AI-driven contract generation, to deployment—empowering you to build decentralized smart contracts faster and more securely.

```

---

Next up: **roadmap.md** with clear milestones and plans. Ready?
```
