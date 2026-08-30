# PR Preparation Checklist

This checklist ensures the first PR is ready for Qodo review and meets hackathon submission requirements.

## Before Opening PR

### Code Quality
- [x] All tests pass (`python3 -m pytest -v`)
- [x] Core reconcile module is complete with matching logic
- [x] Extract module handles canonical demo emails
- [x] No secrets or API keys in repo (check `.env` is in `.gitignore`)
- [x] `.env.example` has placeholder variable names only
- [x] Type hints present in Python code
- [x] `py.typed` marker exists in stamp package

### Documentation
- [x] README.md has clear setup instructions
- [x] README.md documents the Stack (TrueForge, Composio, Daytona, OpenAI)
- [x] README.md has "Qodo Code Review Evidence" placeholder
- [x] SUBMISSION.md ready for hackathon form
- [x] demo/INBOX.md explains how to plant test emails
- [x] skills/stamp/SKILL.md contains agent procedure
- [x] agent/stamp.spec.json is configured correctly

### Agent Configuration
- [x] Agent spec references "composio" MCP server
- [x] Sandbox enabled in agent spec
- [x] Subagents enabled
- [x] Approval policy: `@write` and `@destructive`
- [x] Skill "stamp" attached
- [x] Temperature set appropriately (0.2 for books work)

### Deployment
- [x] Dockerfile builds TrueForge in hosted mode
- [x] render.yaml defines Postgres and Redis
- [x] Environment variables documented
- [x] No hardcoded credentials

### PRD Compliance
- [x] Reconcile module catches duplicate #4412
- [x] Extract module parses demo invoice text
- [x] Demo ledger CSV exists in both `demo/` and `skills/stamp/`
- [x] Skill defines mail-hunter and numbers subagents
- [x] Agent instructions refuse non-money-mail tasks
- [x] No mocks, no simulated inbox mentioned as fallback

## PR Branch Strategy

```bash
# Create feature branch from main
git checkout -b feature/initial-implementation

# Commit substantive changes
git add stamp/ tests/ skills/ agent/ demo/ README.md SUBMISSION.md
git commit -m "feat: implement Stamp invoice reconciliation agent

- Add reconcile module with duplicate detection
- Add extract module for Gmail thread parsing
- Add 11 test cases covering PRD scenarios
- Add TrueForge agent spec with Composio MCP
- Add stamp skill with subagent procedures
- Add documentation and deployment configs
"

# Push to GitHub
git push -u origin feature/initial-implementation
```

## Open PR

1. **Title:** `feat: Stamp invoice reconciliation agent for TrueForge`
2. **Description Template:**

```markdown
## Summary
Implements Stamp, a TrueForge agent that reconciles vendor invoices from Gmail against a ledger and requires approval before creating Gmail drafts.

## Changes
- **Core Logic:** `stamp/reconcile.py` - Books check that flags duplicate invoices
- **Extraction:** `stamp/extract.py` - Parse invoice details from Gmail threads
- **Tests:** 11 pytest cases covering duplicate detection, vendor aliases, currency mismatches
- **Agent:** TrueForge agent spec with Composio (Gmail), Daytona (sandbox), approval on writes
- **Skill:** `skills/stamp/SKILL.md` - Procedure for mail-hunter and numbers subagents
- **Demo:** Ledger CSV and inbox setup instructions

## Testing
```bash
python3 -m pytest -v  # All 11 tests pass
```

## TrueForge Features Used
- MCP: Composio connector for Gmail (search, read, create_draft)
- Sandbox: Daytona runs reconcile code
- Approval: `@write` tools gated by TrueForge
- Skills: Git-backed procedure
- Subagents: Mail-hunter (read-only) and numbers (sandbox-only)
- Sessions: Persistent across browser refresh

## Demo Scenario
| Gmail | Ledger | Result |
|---|---|---|
| Invoice #4412 $4,200 | paid | dispute_duplicate → wait for stamp |
| Reminder #4412 $4,200 | same row | one dispute (idempotent) |
| Invoice #4419 $890 | absent | confirm_new_invoice → wait for stamp |

## Deployment
- Local: `npx @truefoundry/trueforge@latest`
- Render: Dockerfile with Postgres + Redis (see render.yaml)

## Qodo Review
This PR is ready for Qodo `/agentic_review`. High-severity findings will be fixed or dismissed with written reasons. A follow-up review will run on the final code before merge.
```

## After Opening PR

### Qodo Review
1. Comment on PR: `/agentic_review`
2. Wait for Qodo analysis
3. Review findings:
   - **High severity:** Must fix or dismiss with written justification
   - **Medium/Low:** Fix if quick, otherwise document decision
4. Commit fixes to the same branch
5. Request follow-up review: `/agentic_review` (second pass)
6. Document the review cycle in PR comments

### Before Merge
- [ ] At least one Qodo review completed
- [ ] High-severity findings addressed
- [ ] Follow-up review shows improvements
- [ ] All checks pass (tests, build)
- [ ] PR approved by human reviewer (if required)

### After Merge
1. Update README.md "Qodo Code Review Evidence" section:
   ```markdown
   ## Qodo Code Review Evidence
   
   PR: [#1 - Stamp invoice reconciliation agent](https://github.com/USERNAME/stamp/pull/1)
   
   **Qodo Findings:**
   - [List key findings from initial review]
   
   **Actions Taken:**
   - [What was fixed]
   - [What was dismissed and why]
   
   **Follow-up Review:**
   - Second Qodo review completed on [commit hash]
   - [Summary of improvements]
   ```

2. Commit the updated README to main

## Notes

- **No direct pushes to main** except for README updates after PR merge
- **Branch naming:** `feature/`, `fix/`, or `docs/` prefix
- **Commit messages:** Conventional commits format (feat:, fix:, docs:, test:)
- **Qodo requirement:** Hackathon rules require code review via Qodo on substantive changes
- **Evidence:** The merged PR with Qodo comments is the proof for submission
