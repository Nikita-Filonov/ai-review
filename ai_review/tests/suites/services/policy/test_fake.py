from ai_review.tests.fixtures.services.policy import FakePolicyService


def test_fake_policy_records_reviewed_file() -> None:
    policy = FakePolicyService()
    assert policy.should_review_file("file.py") is True
    assert policy.calls[-1] == ("should_review_file", {"file": "file.py"})
