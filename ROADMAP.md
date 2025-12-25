# Datum Project Roadmap

This document outlines the planned features and future direction for **Datum**, the Atomic Unit of Truth.

## 🚀 Near Term (Planned)

### 1. Google Cloud Storage (GCS) Synchronization
*   **Feature:** Enable users to push/pull the ledger to a public or private GCS bucket.
*   **Unique Value:** Facilitates global "Dead Drops" and ledger sharing without manual file transfers.
*   **Note:** Must implement robust global bucket name validation and "Conflict" (409) handling for unique namespace enforcement.

### 2. Steganography Ledger Storage
*   **Feature:** Hide the `ledger.json` file inside image files (JPEG/PNG).
*   **Unique Value:** Stealth mode for sensitive communication. The ledger appears as a normal image on social media or public galleries.

### 3. Multi-Signature (Multi-Sig) Transfers
*   **Feature:** Require signatures from N-of-M wallets to authorize a high-value transaction.
*   **Unique Value:** Enterprise-grade security for shared treasuries.

## 🛰️ Mid Term (Visionary)

### 4. Lightweight P2P Networking
*   **Feature:** Simple peer discovery and chain synchronization over the wire (gRPC or WebSockets).
*   **Unique Value:** Moving from a "Shared File" model to a "Networked Node" model.

### 5. Web Dashboard (GUI)
*   **Feature:** A React or Next.js front-end for visualizing the chain, mining status, and encrypted messages.
*   **Unique Value:** Accessibility for non-CLI users.

### 6. Hardware Wallet Integration
*   **Feature:** Signing transactions using Yubikeys or Ledger devices.
*   **Unique Value:** Maximum security for private keys.

## ✅ Completed Milestones
*   [x] Core Blockchain Logic & Persistence
*   [x] File Notarization & Audit Trails (History Check)
*   [x] ECC Cryptographic Wallets (Project Ironclad)
*   [x] Transaction Signing & Verification
*   [x] Secure Messaging (Dead Drop) via ECDH + AES-GCM
*   [x] Interactive TUI Demos (HPC, Spy, Bazaar)
