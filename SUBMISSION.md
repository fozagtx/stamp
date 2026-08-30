# Submission write-up

Stamp gives a model a license to act on invoice mail, not a license to talk.

The job: read live Gmail, check the books in a Daytona sandbox, draft a dispute or a pay-confirm, stop until a human stamps create_draft.

TrueForge runs the loop. Gmail is accessed via Composio MCP connector. Code runs in Daytona, not on the laptop. Write tools use TrueForge's `@write` approval. The `stamp` skill is the procedure. Subagents hunt mail vs numbers. Sessions are TrueForge's.

There is no mock inbox and no simulated send. After Allow, the draft is in Gmail.
