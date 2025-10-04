# AI Review CI/CD Integration

This folder contains **ready-to-use CI/CD templates** for running AI Review automatically on **Pull Requests** (GitHub,
Bitbucket, Jenkins) or **Merge Requests** (GitLab).

Each example shows how to:

- Install and configure AI Review
- Pass LLM and VCS credentials securely via environment variables
- Trigger inline, summary, or context review commands

---

## ⚙️ Supported CI/CD Providers

| Provider | Template                     | Description                                                        |
|----------|------------------------------|--------------------------------------------------------------------|
| GitHub   | [github.yaml](./github.yaml) | Manual workflow dispatch from Actions tab                          |
| GitLab   | [gitlab.yaml](./gitlab.yaml) | Manual job trigger in Merge Request pipelines                      |
| Jenkins  | [Jenkinsfile](./Jenkinsfile) | Declarative pipeline with **inline/context/summary** review stages |

---

👉 Choose the template matching your CI system, copy it into your repository, and adjust environment
variables (`OPENAI_API_KEY`, `GITHUB_TOKEN`, `CI_JOB_TOKEN`, `BITBUCKET_TOKEN`, etc.) as needed.