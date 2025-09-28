# AI Review CI/CD Integration

This folder contains **ready-to-use CI/CD templates** for running AI Review automatically on **Pull Requests** (GitHub)
or **Merge Requests** (GitLab).

Each example shows how to:

- Install and configure AI Review
- Pass LLM and VCS credentials securely via environment variables
- Trigger inline, summary, or context review commands

---

## ⚙️ Supported CI/CD Providers

| Provider | Template                     | Description                                   |
|----------|------------------------------|-----------------------------------------------|
| GitHub   | [github.yaml](./github.yaml) | Manual workflow dispatch from Actions tab     |
| GitLab   | [gitlab.yaml](./gitlab.yaml) | Manual job trigger in Merge Request pipelines |


