# Agentic Review Demo

This folder is a tiny synthetic project for testing agent mode.

## Goal

Give the reviewer enough cross-file context to:

- detect duplicated logic across modules;
- suggest reusing existing helpers;
- notice policy/security checks bypassed in API layer;
- point out weak test coverage.

## Suggested experiment

1. Make changes in `payments/service.py` or `review/api.py`.
2. Run review with `agent.enabled: false`.
3. Run review with `agent.enabled: true`.
4. Compare findings and cost.

## Expected cross-file hints

- `shared/formatting.py` already has `format_currency`.
- `shared/security.py` already has `can_review_pull_request`.
- `payments/service.py` duplicates formatting and uses float math directly.
- `review/api.py` bypasses centralized permission helper.
