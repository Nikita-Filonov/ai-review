# 📘 AI Review Troubleshooting

This document describes common environment-related issues when running **ai-review**. All cases below are expected Git /
CI behavior, not bugs in `ai-review`.

---

## 🧩 Non-ASCII (Cyrillic) filenames break diff parsing

### Symptoms

- Diff is empty or files are not matched
- Inline review does not work for files with Cyrillic names

### Cause

By default, Git escapes non-ASCII paths in diff output (`core.quotepath=true`).

### Solution

`ai-review` [Docker image](./../../Dockerfile) sets this automatically:

```bash
git config --global core.quotepath false
````

If running outside Docker, make sure this option is enabled manually.

---

## 🧩 `git diff` fails with exit code 128 (missing commits)

### Symptoms

```text
git diff <BASE_SHA> <HEAD_SHA> ... returned exit status 128
```

### Cause

One of the compared commits is not present locally. This usually happens due to **shallow clones in CI**.

### Solution

Fetch full Git history before running `ai-review`.

#### GitHub Actions

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

#### GitLab CI

```yaml
variables:
  GIT_DEPTH: 0
```

Or manually:

```bash
git fetch --unshallow
```



