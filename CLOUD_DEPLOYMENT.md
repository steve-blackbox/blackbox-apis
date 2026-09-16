# ☁️ PRODUCTION CLOUD DEPLOYMENT BLUEPRINT
### INFRASTRUCTURE ORCHESTRATION — BLACKBOX AUDIO LABS LLC

This document details the deployment pipelines and cloud infrastructure rules for hosting the 5 micro-SaaS standalone cavities on global scalable networks (Target platforms: Render.com or Railway.app).

---

## 🛠️ 1. GLOBAL INFRASTRUCTURE PRE-REQUISITES
Because the ecosystem is strictly database-less and built using native JavaScript, deployment requirements are hyper-lightweight:

*   **Runtime:** Node.js v20.x or higher (LTS).
*   **Process Manager:** Built-in platform process allocation (Zero PM2 overhead required).
*   **Storage Allocation:** Ephemeral local disk storage (Sandbox execution space for uploads).

---

## 🎙️ 2. THE FFMPEG AUDIO LAYER CONFIGURATION (ROBOT 02)
To maintain the **$0.00 Third-Party API overhead** standard on `wavtomp3.co` [23context], the cloud environment must support native binary execution:

1.  **Platform Buildpack:** Add the official **FFmpeg Buildpack** inside your Render/Railway dashboard settings:
    *   Target: `https://github.com`
2.  **Binary Path Verification:** The Node.js application utilizes the local system layer via `child_process`. The underlying cloud OS must map `ffmpeg` directly to the global environment variables.

---

## 🔒 3. ENVIRONMENT KEYS INJECTION & PRODUCTION LAUNCH
For each independent application repository, inject the verified secure keys inside the cloud hosting provider's management interface:

```env
NODE_ENV=production
PORT=424X
STRIPE_SECRET_KEY=sk_live_...
```

### ➡️ DEPLOYMENT EXECUTION COMMANDS
*   **Build Command:** `npm install` (Installs lightweight compressed Express framework components).
*   **Start Command:** `node server.js`

---

## ⚡ 4. ZERO-DOWNTIME MIGRATION CHECKLIST FOR BUYERS
The transfer protocol from BlackBox Audio Labs LLC to the acquiring fund follows 3 automated phases:

1.  **Domain Push:** Instant Namecheap account-to-account domain push for the 5 commercial cores [23context].
2.  **Repository Hand-off:** Transfer of the master Git ledger directory containing the sterile production code.
3.  **Environment Variable Hot-Swap:** The buyer updates the `STRIPE_SECRET_KEY` inside the host dashboard to point to their own merchant processor. **The pipeline immediately shifts live revenue streams without code modification.**