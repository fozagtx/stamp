# Stamp

An agent licensed to act on money-mail. It reads a live Gmail inbox, reconciles invoices in a Daytona sandbox, and does not create a Gmail draft until you stamp it.

No mocks. No simulated inbox. No fake send.

## What it does

Same three Acme invoices in a real mailbox:

| Mail | Books | Stamp does |
|---|---|---|
| Invoice #4412 · $4,200 | already paid | dispute draft, then wait |
| Reminder #4412 · $4,200 | same row | one dispute, not two |
| Invoice #4419 · $890 | not on the ledger | confirm-pay draft, then wait |

Prompt: `Process my Acme invoices.`

After Allow, open Gmail → Drafts. If the draft is not there, it did not work.

## Stack

| Piece | What |
|---|---|
| Runtime | TrueForge (bundled chat). Not a custom UI. |
| Model | OpenAI, configured in TrueForge Settings |
| Inbox | Google Gmail MCP `https://gmailmcp.googleapis.com/mcp/v1` |
| Write | Gmail **create_draft** (official MCP does not send). Gated `@write` |
| Sandbox | Daytona |
| Books | `demo/ledger.csv` / `skills/stamp/ledger.csv` read in the sandbox |
| Skill | `skills/stamp/SKILL.md` |

Python in this repo is the books check the sandbox runs. It is not a stand-in for Gmail.

## Local TrueForge

Needs Node 22+.

```bash
npx @truefoundry/trueforge@latest
```

Open `http://localhost:8790`.

1. Settings → Models → OpenAI → API key.
2. Settings → Sandbox providers → Daytona → API key (Sandboxes + Snapshots write).
3. Settings → Connectors → Add MCP Server → URL `https://gmailmcp.googleapis.com/mcp/v1` → OAuth. Enable `gmailmcp.googleapis.com` on a Google Cloud project; add TrueForge’s callback origin to the OAuth client. Complete Connect in chat.
4. Settings → Skills → Import this GitHub repo (or the `skills/stamp` pack).
5. New agent from `agent/stamp.spec.json`: sandbox on, Gmail attached, skill `stamp`, subagents on, approval default `@write` / `@destructive`.
6. Plant the three real emails in `demo/INBOX.md`.
7. `Process my Acme invoices.` Deny once and check Drafts is empty. Allow once and check Drafts.

Local SQLite is for that machine only. Gmail OAuth on localhost uses `PUBLIC_BASE_URL=http://localhost:8790` (or the port you chose).

## Render

Yes. TrueForge hosted mode: one web service + Postgres + Redis. Stamp’s reconcile still runs in **Daytona**, not on the Render box.

```bash
# Blueprint: render.yaml
# After the first URL exists:
#   PUBLIC_BASE_URL=https://<service>.onrender.com
```

In the Render dashboard (or `render.yaml`):

- Web: this Dockerfile (`@truefoundry/trueforge`, `STANDALONE=false`, `HOST=0.0.0.0`).
- Postgres → `POSTGRES_*`.
- Key Value / Redis → `REDIS_URL`.
- `PUBLIC_BASE_URL` = the `https://*.onrender.com` origin. Required for Gmail OAuth.
- Do not use SQLite/standalone on Render.

Put OpenAI and Daytona keys in TrueForge Settings after boot (they live in TrueForge’s DB, not in this image). Same for the Gmail connector.

Without OIDC, anyone who has the Render URL is admin. Enable OIDC for a shared host, or take the service down when you are done showing it.

## Books check (sandbox)

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

```bash
python3 -m stamp.reconcile invoices.json demo/ledger.csv
```

`invoices.json` is produced from live Gmail thread text in the sandbox, not from fixtures.

## Qodo Code Review Evidence

Required for submission. After the first reviewed merge, replace this paragraph with:

- Link to the merged PR
- What Qodo surfaced and what changed or was dismissed
- Note that a follow-up review ran on the final code

Direct pushes to main do not count.

## TrueForge write-up (submission form)

Stamp is a TrueForge agent. MCP reaches Gmail. The sandbox runs extract + reconcile. Skills hold the procedure. Subagents split mail vs numbers. TrueForge pauses on create_draft. The session is TrueForge’s. We did not wrap a chat model in a custom app.
