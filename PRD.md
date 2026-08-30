# Stamp — Product Requirements Document

**Status:** Ready for implementation  
**Hackathon:** The Agent Harness Hackathon (WeMakeDevs × TrueFoundry), theme “Give AI models a License to act”  
**Track aim:** Best Use of TrueForge  
**Owner:** implementation agent  
**Triage:** `ready-for-agent`

This document is the source of truth. There is no GitHub issue tracker in this workspace yet. When a public repo exists, this PRD is the first file on a Qodo-reviewed pull request. Do not invent features past the hard cap of three demo features.

---

## Problem Statement

I get invoices and “reminders” in Gmail. A second copy of an already-paid invoice looks like a polite nudge. If I (or an agent acting as me) reply “we’ll pay this” or actually send payment instructions, money or a commitment leaves my name and I cannot unsay it.

Chat tools will draft that reply from the email text alone. That is the failure. The draft is not checked against what I already paid. If the agent can also send, a wrong draft becomes a real payment, a duplicate transfer, or a vendor relationship I now have to unwind.

I need an agent that is allowed to **read** money-mail and **run the numbers**, and is **not** allowed to **send** until I stamp it. I will not hand it production infrastructure, Kubernetes, or incident response. I will not trust a model’s first sentence as a books check.

---

## Solution

Stamp is a TrueForge agent for one job: process vendor invoices in Gmail against a ledger, then wait.

1. It reads the relevant Gmail threads through a TrueForge MCP connector (real inbox, not a mock).
2. It runs Python in a Daytona sandbox to reconcile invoice number, vendor, and amount against `ledger.csv`.
3. It shows a match table (paid / duplicate / new / unknown) and a drafted reply.
4. Sending the reply is a write tool. TrueForge pauses. I Allow or Deny. Only then does mail leave.

The product is the **license**, not the prose. A duplicate of Acme invoice **#4412 for $4,200** must be caught in the sandbox and must not send a pay-confirmation until I stamp. A new Acme invoice **#4419 for $890** may be drafted as “pay this” and still waits.

The agent runs on **TrueForge** (open-source harness: MCP, sandbox, approvals, skills, subagents, persistent sessions). It does not run on TrueFoundry AI Gateway, Guardrails, or MCP Gateway. Those are out of scope for this hackathon and for this product.

The operator uses TrueForge’s bundled chat UI. There is no custom web app.

**No mocks. No simulations.** Live Gmail via TrueForge MCP, live Daytona sandbox, live TrueForge approval on a real write. If any of those is missing, Stamp is not done. There is no .eml inbox, no pasted transcript, no fake send, no local `exec` standing in for Daytona, no “would have sent” banner.

---

## User Stories

1. As a solo operator, I want Stamp to process my Acme invoices from Gmail in one turn, so that I do not open Excel and search mail by hand.
2. As a solo operator, I want Stamp to read real Gmail threads via TrueForge MCP, so that the demo is not a pasted transcript pretending to be an inbox.
3. As a solo operator, I want attachments and body text both considered, so that an invoice sitting in a PDF or a HTML body still gets a number and an amount.
4. As a solo operator, I want reconciliation to run in the sandbox as code, so that amounts are not “reasoned” in the model’s prose.
5. As a solo operator, I want invoice **#4412 / $4,200** that already appears on the ledger marked **duplicate / already paid**, so that I do not pay it twice.
6. As a solo operator, I want a “reminder” email that repeats **#4412** treated as the same paid invoice, so that polite wording does not bypass the books.
7. As a solo operator, I want invoice **#4419 / $890** that is not on the ledger marked **new / unpaid**, so that legitimate bills still move.
8. As a solo operator, I want an invoice whose vendor is missing from the ledger marked **unknown vendor**, so that Stamp does not invent a payment history.
9. As a solo operator, I want an invoice whose number matches but whose amount differs marked **amount mismatch**, so that a tampered or revised bill is not auto-classified as paid.
10. As a solo operator, I want a drafted **dispute** reply for duplicates, so that I can send a factual “already settled” message instead of paying.
11. As a solo operator, I want a drafted **pay-this** reply for new invoices, so that I can confirm a real bill without composing from scratch.
12. As a solo operator, I want Stamp to **stop before send**, so that nothing irreversible happens on the model’s say-so.
13. As a solo operator, I want TrueForge to show the tool name and arguments at the pause, so that I can see it is about to send mail, not just “continue.”
14. As a solo operator, I want to click **Allow** and have Gmail actually create the draft or send the mail in my mailbox, so that stamping is a real write I can open in Gmail and verify.
15. As a solo operator, I want to click **Deny** and have nothing sent, so that a bad draft dies in place.
16. As a solo operator, I want Deny to leave the analysis and draft visible in the session, so that I can edit instructions and try again without re-doing the books check.
17. As a solo operator, I want read tools (search, get thread) to run without a stamp, so that investigation is not blocked by approval noise.
18. As a solo operator, I want write/destructive Gmail tools gated by TrueForge’s default `@write` / `@destructive` approval policy, so that we do not hand-roll a second policy engine.
19. As a solo operator, I want a Generative UI table of invoice id, vendor, amount, ledger status, and proposed action, so that I can judge the books at a glance.
20. As a solo operator, I want a skill (`stamp` playbook) loaded on demand, so that the procedure lives in `SKILL.md` instead of a giant system prompt.
21. As a solo operator, I want sandbox enabled on the agent, so that the skill and Code Mode can actually run.
22. As a solo operator, I want one subagent to hunt Gmail and one subagent to run reconciliation, so that the root agent only sees summaries.
23. As a solo operator, I want the root agent to be the only one allowed to call send, so that a mail-hunter subagent cannot leak a send.
24. As a solo operator, I want the session to survive a browser refresh, so that a mid-reconcile disconnect does not wipe the license pause.
25. As a solo operator, I want Stamp to ask a clarifying question when the vendor name is ambiguous, so that it does not stamp the wrong supplier.
26. As a solo operator, I want Stamp to ask a clarifying question when multiple open invoices share a similar amount, so that it does not match on dollars alone.
27. As a solo operator, I want an empty-inbox result to say “no matching invoices,” so that silence is not mistaken for “all clear.”
28. As a solo operator, I want a missing or unreadable attachment to be reported as **needs human**, so that Stamp does not guess line items.
29. As a solo operator, I want currency other than USD to be flagged, so that a $ / £ mix-up is not treated as a match.
30. As a solo operator, I want partial payments on the ledger (amount paid < invoice amount) marked **partial**, so that “paid” is not a lie.
31. As a solo operator, I want the demo ledger to be a CSV the sandbox can read, so that judges can inspect the books in the repo.
32. As a solo operator, I want three real Acme messages sitting in the connected Gmail inbox (planted by sending real mail, not by shipping .eml fixtures as the runtime source), so that search hits live threads.
33. As a judge, I want to see MCP, sandbox, and approval in one run, so that the submission qualifies.
34. As a judge, I want instructions that state the job in one paragraph, so that I know this is not a generic chatbot.
35. As a judge, I want the README to explain how TrueForge is doing the work, so that sponsor-tool use is obvious.
36. As a judge, I want a public repo I can clone, so that I can read the skill, ledger, and agent spec.
37. As a maintainer, I want secrets out of the repo, so that API keys and mailbox contents never land on GitHub.
38. As a maintainer, I want every substantive change on a pull request reviewed by Qodo before merge, so that the submission meets the code-review rule.
39. As a maintainer, I want a `## Qodo Code Review Evidence` section in the README linking a real merged PR, so that screenshots are not the proof.
40. As a maintainer, I want High-severity Qodo findings fixed or dismissed with a written reason, so that the PR trail is honest.
41. As a maintainer, I want a follow-up Qodo review on the same PR after fixes, so that the history shows the loop, not a one-shot comment.
42. As an implementer, I want OpenAI as the model provider, so that we use the key already on this machine.
43. As an implementer, I want local TrueForge via `npx @truefoundry/trueforge@latest` on port 8790, so that Docker Compose is not a dependency.
44. As an implementer, I want Daytona as the sandbox provider, so that skills and Code Mode are legal in TrueForge.
45. As an implementer, I want Gmail connected inside TrueForge Settings → Connectors, so that Cursor’s Gmail MCP is not confused with the harness.
46. As an implementer, I want the build to halt if Gmail OAuth or Daytona is not connected, so that we never ship a simulated path.
47. As an implementer, I want unit tests for Reconcile only (pure function, sample rows in the test file). Those tests are not a Gmail mock and must not be used as the demo data source.
48. As an operator who denied a send, I want Stamp not to retry send in the same turn, so that Deny is respected.
49. As an operator, I want labels or a short status line after a successful stamped send (“sent dispute for #4412”), so that I know the license was used.
50. As an operator, I want Stamp to refuse jobs that are not money-mail (deploys, kubectl, “scale the database”), so that this product cannot drift into the previous incident-agent shape.
51. As an operator, I want ledger writes (marking an invoice paid) to also require approval if such a write tool exists; for this hackathon the ledger is a repo CSV and is **not** mutated by the agent unless we add an explicit approved write. Default: ledger is read-only in the sandbox.
52. As a teammate, I want the agent spec (model, connectors, skill name, sandbox on, subagents on, approval policy) documented in-repo, so that a stranger can recreate the agent in TrueForge Settings.
53. As a teammate, I want seed messages or a demo prompt in the README (“Process my Acme invoices.”), so that the happy path does not depend on tribal knowledge.
54. As a privacy-conscious operator, I want the demo mailbox to be a dedicated inbox or clearly fake vendor addresses (`billing@acme-demo.example`), so that personal mail is not recorded in a demo.
55. As an operator, I want Stamp to treat “pay,” “wire,” “ACH,” and “settle” drafts as send-class actions, so that we do not only gate a tool named `send_email` while some other write tool ships the same text.
56. As an operator, I want the proposed action column to be one of `dispute_duplicate`, `confirm_new_invoice`, `escalate_mismatch`, `escalate_unreadable`, so that the table is a decision, not a paragraph.
57. As an operator, I want sources (Gmail thread id, ledger row) cited next to each row, so that I can audit the match.
58. As an operator, I want Code Mode used when joining many tool results, so that large Gmail payloads are reduced in the sandbox instead of dumped into context.
59. As an operator, I want large tool responses offloaded to sandbox files (TrueForge default), so that a fat MIME body does not blow the window before reconciliation.
60. As a hackathon submitter, I want a short TrueForge write-up (job, MCP, sandbox, approval, skill, subagents) suitable to paste into the submission form, so that the form is not drafted from memory.

---

## Implementation Decisions

### Product shape

- **One job.** Process vendor invoices in Gmail against a ledger, draft the reply, wait for a stamp, then send or stop.
- **Hard cap: three demo features.** (1) Sandbox reconciliation that catches #4412. (2) Gmail read + approval-gated send. (3) Skill + subagents (and Generative UI table as part of presenting #1). Nothing else ships in this timebox.
- **UI:** TrueForge bundled chat only. No marketing site, no custom React app, no dual “naive vs safe” agent view.
- **Name:** Stamp. Domain language: *license*, *stamp*, *books check*, *money-mail*. Do not use Backstop, guardrail-as-product, incident, Kubernetes, or “naive agent.”

### Runtime (TrueForge)

- **Local:** `npx @truefoundry/trueforge@latest`, UI at `http://localhost:8790`, SQLite. Fine for wiring the agent on the operator’s machine.
- **Render (public):** TrueForge **hosted** mode only — web service + Postgres + Redis, `STANDALONE=false`, `HOST=0.0.0.0`, `PUBLIC_BASE_URL=https://<service>.onrender.com`. Gmail OAuth will not complete without that public origin. Do not run standalone/SQLite on Render (ephemeral disk, and TrueForge documents standalone as localhost-only). Without OIDC, anyone who can reach the URL is admin — enable OIDC or treat the URL as a short-lived demo. Not TrueFoundry SaaS.
- **Model:** OpenAI, using the operator’s existing `OPENAI_API_KEY`, configured in TrueForge Settings → Models. Prefer a current OpenAI chat model available in the catalog. Temperature low (about 0.2) for books work.
- **Sandbox:** Daytona only (TrueForge’s current provider). Operator pastes a Daytona API key with Sandboxes + Snapshots write. Agent has `config.sandbox.enabled: true`. Skills and Code Mode require this. If Daytona is missing, stop. Do not run Python on the TrueForge host, on the laptop, or in a container we pretend is Daytona.
- **MCP:** Gmail (or the catalog’s Google/Gmail connector) registered in TrueForge Settings → Connectors with OAuth. Credentials live in the connector, never in git. Runtime invoice data comes only from that connector’s search/get tools. Hardcoded JSON, README samples, .eml files, and chat-pasted invoices are not an inbox.
- **Tool policy:** `enable_tools` may be `@all` for the Gmail server in this timebox, or a tighter list if the catalog is huge. `require_approval_for_tools` stays the harness default: `@write` and `@destructive`. Do not require approval on read-only search/get.
- **Subagents:** `dynamic_sub_agents` on. Root instructions: mail-hunter subagent is read-only; numbers subagent is sandbox-only; only root may call write tools.
- **Skills:** git-backed `SKILL.md` named `stamp` (or `stamp-reconcile`). Attach by name. Do not preload a long body. Progressive disclosure.
- **Generative UI:** on. After reconciliation, render a table, not only markdown.
- **Ask user questions:** on. Use for vendor ambiguity and amount collisions, not for “are you sure?” after the approval widget already exists.
- **Sessions:** default persistence. Do not build a custom session store.
- **Iteration limit:** keep a finite limit (TrueForge default or ≤ 50) so a bad loop cannot spam Gmail.

### Modules (deep modules first)

1. **Reconcile (pure books check)**  
   Input: list of extracted invoices `{invoice_id, vendor, amount_cents, currency, source_thread_id}` plus ledger rows `{invoice_id, vendor, amount_cents, currency, status}`.  
   Output: list of `{invoice_id, status, proposed_action, reasons[], ledger_row_id?}`.  
   Status enum: `duplicate_paid` | `new_unpaid` | `amount_mismatch` | `unknown_vendor` | `partial` | `unreadable`.  
   Action enum: `dispute_duplicate` | `confirm_new_invoice` | `escalate_mismatch` | `escalate_unreadable`.  
   Matching rule: same vendor (case-insensitive trim) AND same invoice_id. Amount compared in integer cents. Currency must match. Invoice_id match with amount mismatch → `amount_mismatch`, never `duplicate_paid`.  
   This module must be runnable in the sandbox as a single Python file with no network. It is the one key dependency.

2. **Extract (thin, lossy, sandbox or skill procedure)**  
   Turn Gmail thread text / attachment filenames into the invoice list above. Best-effort regex and simple PDF-to-text if the sandbox image allows; if extraction fails, status `unreadable`. Do not call external OCR APIs in this timebox. Demo emails are constructed so extraction is easy (plain figures in the body: `Invoice #4412` / `Amount: $4,200.00`).

3. **Stamp skill**  
   Procedure the agent must follow: extract → reconcile in sandbox → render table → draft exactly one reply per actionable row → call send only after presenting the table → never send on `escalate_*`. Include the refusal to do infra/SRE tasks.

4. **Agent spec**  
   Saved TrueForge agent: instructions (short role), Gmail connector, skill `stamp`, sandbox on, subagents on, generative UI on. Documented in-repo as YAML/JSON matching TrueForge’s agent spec fields so it can be recreated. Approval policy as above.

5. **Live demo data**  
   `demo/ledger.csv` is a real file the Daytona sandbox reads (copy into the sandbox at run start). It is the books, not a stand-in for Gmail.  
   `demo/INBOX.md` is an operator checklist: send three real emails into the connected Gmail account (invoice #4412, reminder #4412, invoice #4419). The agent must find them with Gmail search. Do not add `demo/emails/` or any runtime fixture inbox.

6. **Submission docs**  
   README: run TrueForge, configure OpenAI, Daytona, Gmail, enable the agent, demo prompt, how harness features map to the job, secrets policy, `## Qodo Code Review Evidence` placeholder until a PR exists. Short `SUBMISSION.md` write-up for the form. No video production in this PRD.

### Gmail tool mapping

- Read: search threads, get thread/message against the live mailbox. Ungated.
- Connector: Google’s remote Gmail MCP at `https://gmailmcp.googleapis.com/mcp/v1` (custom TrueForge connector; not in the shipped catalog). OAuth in the operator’s Google Cloud project (`gmailmcp.googleapis.com` enabled). Redirect URI must match TrueForge `PUBLIC_BASE_URL`.
- Write: official Gmail MCP can **create a draft** in the live mailbox (`gmail.compose`); it does not send. The stamped action is that **create_draft** (or send, if a later connector adds it). After Allow, the operator opens Gmail and sees the draft. Chat text is not a draft. If the connector exposes neither write tool, Stamp is not done.
- Printing the email body in chat, copying to clipboard, or writing a file named `sent.txt` is not send.
- Do not trash, spam, or bulk-label in the demo path.

### Ledger

- Read-only CSV in the repo, copied into the Daytona sandbox at run start (skill tells the agent to load `demo/ledger.csv` from the sandbox filesystem). Not typed into the prompt. Not invented by the model.
- Agent does not write the ledger in v1.
- Amounts stored as integer cents in the reconcile module even if the CSV shows `$4,200.00` — parse in Python, not in the LLM.

### Demo scenario (canonical)

| Source (live Gmail) | Invoice | Amount | Ledger | Result |
|---|---|---|---|---|
| Connected inbox | Acme #4412 | $4,200.00 | paid | `duplicate_paid` → draft dispute → **stamp to send** |
| Connected inbox | Acme #4412 reminder | $4,200.00 | same row | same duplicate, one dispute, do not double-send |
| Connected inbox | Acme #4419 | $890.00 | absent | `new_unpaid` → draft confirm → **stamp to send** |

Prompt: `Process my Acme invoices.`

### Repo and Qodo

- Public GitHub repo under the operator’s account (`fozagtx` on this machine).
- Do not push product code straight to `main`. Branch → PR → Qodo `/agentic_review` → fix or dismiss Highs with reasons → re-review → human merge.
- First PR: skill, reconcile module + tests, fixtures, agent spec, README skeleton.
- `.env` and keys gitignored. Example env names only.

### What we explicitly refuse to port

- No Backstop architecture, no dual agents, no K8s signals, no “scale to zero,” no Bedrock fallback router, no TrueFoundry Gateway/Guardrails as the story.

### If a live dependency is missing

Stop. Do not degrade. Do not substitute Slack, GitHub issues, .eml uploads, hardcoded invoices, local Python, or a banner that says sent. Wire the real connector or do not ship.

---

## Testing Decisions

A good test asserts **external behavior of Reconcile**: given invoices + ledger rows, the status and proposed_action are correct. Tests do not import TrueForge, do not mock Gmail, do not stub Daytona, and do not snapshot LLM text. Fixture rows in pytest are allowed only inside the unit test; they are not a product inbox.

**Test the Reconcile module** (required):

- #4412 at $4,200 against paid ledger row → `duplicate_paid` / `dispute_duplicate`
- Reminder with same id and amount → still one duplicate classification (idempotent per invoice_id)
- #4419 at $890 with no row → `new_unpaid` / `confirm_new_invoice`
- #4412 at $4,199.00 → `amount_mismatch` / `escalate_mismatch`
- Vendor `ACME` vs `Acme Demo Billing` — define in tests: either a normalization alias in fixtures (both stored as `acme`) **or** unknown_vendor if strings differ. Decision: demo ledger vendor field is `acme`; extractor must emit `acme` for “Acme Demo Billing” via a small alias map in Reconcile (`acme demo billing` → `acme`). Test that alias.
- Currency GBP vs USD → `amount_mismatch` or a dedicated reason; implement as mismatch, not paid.
- Empty invoice list → empty result, no crash
- Unreadable row (missing invoice_id or amount) → `unreadable` / `escalate_unreadable`

**Do not test** (timebox): MCP OAuth, Daytona provisioning, TrueForge approval widget, subagent scheduling, Generative UI HTML. Those are exercised in a manual demo checklist in the README.

**Prior art:** none in this empty repo. Tests are pytest on the pure Python module. Keep them fast and fixture-driven.

**Manual demo checklist** (README, not automated):

1. TrueForge up, model, Daytona, Gmail connected, Stamp agent selected.
2. Prompt `Process my Acme invoices.`
3. Observe Gmail tool calls, sandbox run, table with duplicate + new.
4. Observe the TrueForge approval pause on the real Gmail write tool. Deny once; confirm Gmail has no new draft/sent. Allow once; open Gmail and confirm the draft or sent mail exists.
5. Refresh the tab; session still present if a pause was open.

---

## Out of Scope

- Any video recording, editing, thumbnails, or captions.
- Custom frontend, landing page, or TrueForge UI SDK restyling (unless leftover minutes after features 1–3 are flawless — still not required by this PRD).
- TrueFoundry cloud: AI Gateway, Guardrails, MCP Gateway, Bedrock, hosted Agent Harness.
- Kubernetes, SRE, incident response, rollbacks, production database actions.
- Dual naive/safe agents or “caught then corrected” split-screen.
- QuickBooks, Stripe, banks, actual money movement, ACH, cards.
- OCR APIs, invoice-vision models, multi-currency conversion, tax engines.
- Mutating the ledger, marking invoices paid, writing to Neon or any database (Neon MCP in Cursor is not part of Stamp).
- GitHub code-review agent, PR-filing agent, analytics SQL agent, research desk.
- Docker Compose / Kubernetes TrueForge deploy.
- Anthropic/Bedrock providers (unless OpenAI is down; not planned).
- Multi-user OIDC, hosted TrueForge, production hardening beyond secrets-out-of-git.
- i18n, mobile apps, Slack/Linear connectors.
- Auto-send below a dollar threshold (defeats the license).
- Using Cursor Gmail/Exa/Neon tools as the product’s runtime.
- Mocks, stubs, recorded transcripts, .eml inboxes, hardcoded invoice JSON, fake MCP servers, local `exec` as sandbox, simulated approval, “dry run send,” or any banner that claims mail left when it did not.

---

## Further Notes

- **One key dependency:** if Reconcile does not flag #4412 as already paid, the rest of the harness demo is a chatbot with a pause. Build and test Reconcile first.
- **Qualification bar (hackathon):** a judge must see a real MCP tool, code in the sandbox, and a human pause before an irreversible write. Film/capture of that run is the operator’s submission problem, not an implementation story in this PRD.
- **Timebox:** remaining hours. Do not expand the enum list, add vendors, or add a second connector.
- **Empathy claims this product rests on:** people pay duplicate invoices because reminders look like new bills; “draft for me” still fails if send is one click; the existing workaround is Gmail search + a spreadsheet. Stamp automates that workaround and inserts a stamp.
- **Assumptions killed:** Stamp does not replace accounting software; it does not auto-pay; demo extraction does not need to survive every PDF on earth.
- **Glance:** table showing **$4,200 duplicate — do not pay** plus a TrueForge **Licence required** pause.
- **Publish:** this file is the PRD. When the GitHub repo exists, open an issue titled “PRD: Stamp” with label `ready-for-agent` and body linking to this file; until then, treat `PRD.md` as the tracker.
