pytest_plugins = (
    "ai_review.tests.fixtures.services.git",
    "ai_review.tests.fixtures.services.llm",
    "ai_review.tests.fixtures.services.vcs",
    "ai_review.tests.fixtures.services.diff",
    "ai_review.tests.fixtures.services.cost",
    "ai_review.tests.fixtures.services.prompt",
    "ai_review.tests.fixtures.services.artifacts",
    "ai_review.tests.fixtures.services.review.inline",
    "ai_review.tests.fixtures.services.review.summary",

    "ai_review.tests.fixtures.clients.github",
    "ai_review.tests.fixtures.clients.gitlab",
    "ai_review.tests.fixtures.clients.openai",
    "ai_review.tests.fixtures.clients.gemini",
    "ai_review.tests.fixtures.clients.claude",
    "ai_review.tests.fixtures.clients.ollama",
    "ai_review.tests.fixtures.clients.bitbucket",
)
