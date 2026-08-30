<p align="center">
  <img src="assets/logo.jpg" alt="Stamp logo" width="160" />
</p>

# Stamp

An agent licensed to act on money-mail. It reads a live Gmail inbox, reconciles invoices in a Daytona sandbox, and does not create a Gmail draft until you stamp it.

No mocks. No simulated inbox. No fake send.

## What it does

Three Acme invoices in a real Gmail mailbox:

| Mail | Books | Stamp does |
|---|---|---|
| Invoice #4412 · $4,200 | already paid | draft dispute → **wait for stamp** |
| Reminder #4412 · $4,200 | same row | one dispute, not two |
| Invoice #4419 · $890 | not on ledger | draft pay-confirm → **wait for stamp** |

Prompt: `Process my Acme invoices.`

After you click **Allow**, open Gmail → Drafts. If the draft is not there, it did not work.

## Stack

| Piece | What |
|---|---|
| Runtime | TrueForge (bundled chat). Not a custom UI. |
| Model | OpenAI |
| Inbox | Google Gmail MCP (`gmailmcp.googleapis.com`) |
| Write gate | TrueForge `@write` approval — pauses before `create_draft` |
| Sandbox | Daytona — runs the reconcile Python, not the laptop |
| Books | `demo/ledger.csv` — read in sandbox, not typed into prompt |
| Skill | `skills/stamp/SKILL.md` |

## Prerequisites

Before you start, make sure you have:

- **Node 22+** — `node --version`
- **OpenAI API key** — from [platform.openai.com](https://platform.openai.com/api-keys)
- **Daytona API key** — from [app.daytona.io](https://app.daytona.io) (needs Sandboxes + Snapshots write)
- **Google Cloud project** with Gmail API enabled and an OAuth 2.0 client (see step 3 below)

## Run locally

```bash
# Clone
git clone https://github.com/fozagtx/stamp.git
cd stamp

# Copy env defaults (no secrets in this file)
cp .env.example .env

# Start TrueForge
npx @truefoundry/trueforge@latest --port 8790
```

Open **[http://localhost:8790](http://localhost:8790)** — you should see the TrueForge chat UI.

## Configure TrueForge (one-time, in the UI)

### 1 · Add OpenAI model

**Settings → Models → OpenAI → Add key**

Paste your `OPENAI_API_KEY`. Temperature 0.2 is set in the agent spec.

### 2 · Add Daytona sandbox

**Settings → Sandbox Providers → Daytona → Add key**

Paste your `DAYTONA_API_KEY`. The reconcile Python runs here — not on your machine.

### 3 · Connect Gmail MCP

**Settings → Connectors → Add MCP Server**

| Field | Value |
|---|---|
| Name | `gmail` |
| URL | `https://gmailmcp.googleapis.com/mcp/v1` |
| Transport | Streamable HTTP |

Click **Connect** → Google OAuth popup → sign in with the Gmail account Stamp should read.

> **Google Cloud setup (one-time):**
> 1. [console.cloud.google.com](https://console.cloud.google.com) → your project → **Enable Gmail API**
> 2. **APIs & Services → Credentials → Create OAuth 2.0 Client ID** (Web application)
> 3. Authorized JavaScript origins: `http://localhost:8790`
> 4. Authorized redirect URIs: `http://localhost:8790/auth/callback`
> 5. Paste Client ID + Secret when TrueForge prompts during Connect

### 4 · Import the skill

**Settings → Skills → Import from GitHub** → `fozagtx/stamp`

TrueForge finds `skills/stamp/SKILL.md` automatically.

### 5 · Import the agent

**Agents → Import** → upload `agent/stamp.spec.json` from this repo.

This wires everything: Gmail connector, stamp skill, Daytona sandbox, `@write` approval policy.

## Plant the test emails

Follow `demo/INBOX.md` — send three real emails into the connected Gmail account:

1. Invoice #4412 · $4,200 from Acme
2. A reminder for #4412 (same amount)
3. Invoice #4419 · $890 from Acme

These must be real emails. The agent searches Gmail live — there are no fixtures in this repo.

## Run the demo

In TrueForge chat, type:

```
Process my Acme invoices.
```

Watch it:
1. **Gmail search + read** — ungated, no approval prompt
2. **Daytona sandbox** — reconcile runs as Python, not prose
3. **Table** — `#4412 duplicate_paid`, `#4419 new_unpaid`
4. **Pause** — TrueForge shows `create_draft` tool call, asks Allow / Deny

**Try Deny first** → check Gmail Drafts → empty ✅  
**Try Allow** → check Gmail Drafts → draft appears ✅

## Books check (local, no Gmail needed)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
# 12 passed
```

## Qodo Code Review Evidence

Required for submission. After the first reviewed merge, replace this paragraph with:

- Link to the merged PR
- What Qodo surfaced and what changed or was dismissed
- Note that a follow-up review ran on the final code

Direct pushes to main do not count.

## TrueForge write-up (submission form)

Stamp is a TrueForge agent. MCP reaches Gmail via Google's official Gmail MCP (`gmailmcp.googleapis.com`). The sandbox runs extract + reconcile. Skills hold the procedure. Subagents split mail vs numbers. TrueForge pauses on create_draft. The session is TrueForge's. We did not wrap a chat model in a custom app.
