# Architecture Overview - tidygen

## Introduction

This document outlines the architecture of **TidyGen**, detailing its core components, data flows, and technology stack. TidyGen is a Web3 + AI-powered tool for generating Substrate-based smart contracts with integrated decentralized identity (DID) login.

---

## System Components

### 1. Frontend

- **Technology:** React, TypeScript, Tailwind CSS  
- **Responsibilities:**  
  - Provides user interface for DID login, contract specification input, code preview, and editing  
  - Communicates with backend REST APIs for authentication and contract generation  
  - Integrates with Polkadot.js SDK for contract deployment and interaction  

### 2. Backend

- **Technology:** Node.js, TypeScript, Express.js  
- **Responsibilities:**  
  - Handles user authentication via DID protocols, validating decentralized identities  
  - Processes contract generation requests by calling AI model APIs (e.g., OpenAI)  
  - Manages business logic, input validation, and error handling  
  - Serves RESTful API endpoints consumed by the frontend  

### 3. AI Code Generation API

- External AI model (e.g., OpenAI GPT) used for generating contract source code based on user inputs  
- Backend acts as intermediary, formatting requests and processing AI responses  

### 4. Blockchain Integration

- **Platform:** Substrate-based blockchains in the Polkadot ecosystem  
- **Tools:** Polkadot.js SDK  
- Enables contract deployment, testing, and interaction directly from the frontend  

---

## Data Flow

```mermaid
graph TD
  User[User]
  DIDAuth[DID Authentication Service]
  Frontend[React Frontend]
  Backend[Node.js Backend]
  AIModel[AI Code Generation API]
  Blockchain[Substrate Blockchain]

  User -->|Login with DID| DIDAuth
  DIDAuth -->|Authenticate| Frontend
  Frontend -->|Request contract generation| Backend
  Backend -->|Send contract specs| AIModel
  AIModel -->|Generated contract code| Backend
  Backend -->|Send code| Frontend
  Frontend -->|Deploy contract| Blockchain
````

---

## Technology Stack Summary

| Layer            | Technology / Framework                 |
| ---------------- | -------------------------------------- |
| Frontend         | React, TypeScript, Tailwind CSS        |
| Backend          | Node.js, TypeScript, Express.js        |
| AI Integration   | OpenAI API (or alternative)            |
| Authentication   | Decentralized Identity (DID) Protocols |
| Blockchain       | Substrate Framework, Polkadot.js SDK   |
| Package Manager  | pnpm                                   |
| Testing          | Jest, React Testing Library            |
| Containerization | Docker (optional)                      |

---

## Security Considerations

* DID login eliminates reliance on centralized authentication, reducing attack surface
* AI-generated code undergoes validation and linting before deployment
* User data and credentials are never stored centrally, enhancing privacy

---

## Scalability & Extensibility

* Modular monorepo structure allows independent development of frontend/backend
* AI model integration abstracted, enabling switching or upgrading models easily
* Designed to support multiple DID methods and wallet integrations in future

---

## Diagram

![Architecture Diagram](./assets/architecture-diagram.png)
*(Add your architecture diagram image here)*

---

## Summary

TidyGen’s architecture balances modern AI capabilities with decentralized Web3 principles, delivering a secure, efficient tool tailored for blockchain developers in the Polkadot ecosystem.
