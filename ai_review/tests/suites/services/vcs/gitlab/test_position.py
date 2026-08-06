from ai_review.clients.gitlab.mr.schema.changes import GitLabDiffRefsSchema, GitLabMRChangeSchema
from ai_review.services.vcs.gitlab.position import build_inline_position, find_change

# Two hunks where the first inserts one line, so every line number in the second
# hunk differs between the old and the new file.
TWO_HUNK_DIFF = """@@ -80,4 +80,5 @@
 class Store:
     def __init__(self, session):
+        self.cache = {}
     def get(self, key):
         return self.session.get(key)
@@ -126,4 +127,5 @@
 def remove(session, key):
     entry = session.get(key)
-    session.delete(entry)
+    session.mark_deleted(entry)
+    session.flush()
     session.commit()
"""

DIFF_REFS = GitLabDiffRefsSchema(base_sha="base-sha", head_sha="head-sha", start_sha="start-sha")

CHANGES = [
    GitLabMRChangeSchema(diff=TWO_HUNK_DIFF, old_path="src/db.py", new_path="src/db.py"),
    GitLabMRChangeSchema(diff="@@ -1,0 +1,1 @@\n+first", old_path="src/new.py", new_path="src/new.py"),
]


# ---------- find_change ----------

def test_find_change_matches_the_new_path() -> None:
    """Should find the change entry describing the file."""
    assert find_change(CHANGES, "src/db.py") is CHANGES[0]


def test_find_change_matches_the_old_path_of_a_rename() -> None:
    """Should also match on the pre-rename path."""
    changes = [GitLabMRChangeSchema(diff=TWO_HUNK_DIFF, old_path="src/old.py", new_path="src/new.py")]

    assert find_change(changes, "src/old.py") is changes[0]


def test_find_change_returns_none_for_unknown_file() -> None:
    """Should return nothing when the file is not part of the MR."""
    assert find_change(CHANGES, "src/absent.py") is None


# ---------- build_inline_position ----------

def test_build_inline_position_pairs_a_context_line() -> None:
    """Should send both line numbers for an unchanged line, which GitLab needs to resolve it."""
    position = build_inline_position(file="src/db.py", line=131, diff_refs=DIFF_REFS, changes=CHANGES)

    assert position.position_type == "text"
    assert position.base_sha == "base-sha"
    assert position.head_sha == "head-sha"
    assert position.start_sha == "start-sha"
    assert position.old_path == "src/db.py"
    assert position.new_path == "src/db.py"
    assert position.old_line == 129
    assert position.new_line == 131


def test_build_inline_position_pairs_a_context_line_in_the_first_hunk() -> None:
    """Should keep the two sides in step before any shift has accumulated."""
    position = build_inline_position(file="src/db.py", line=81, diff_refs=DIFF_REFS, changes=CHANGES)

    assert position.old_line == 81
    assert position.new_line == 81


def test_build_inline_position_omits_the_old_line_for_an_added_line() -> None:
    """An added line has no counterpart in the old file, so old_line must stay unset."""
    position = build_inline_position(file="src/db.py", line=129, diff_refs=DIFF_REFS, changes=CHANGES)

    assert position.old_path == "src/db.py"
    assert position.new_path == "src/db.py"
    assert position.old_line is None
    assert position.new_line == 129


def test_build_inline_position_omits_the_new_line_for_a_removed_line() -> None:
    """A removed line exists only in the old file, so new_line must be dropped."""
    changes = [
        GitLabMRChangeSchema(
            diff="@@ -1,5 +1,2 @@\n alpha\n-beta\n-gamma\n-delta\n epsilon\n",
            old_path="src/list.py",
            new_path="src/list.py",
        )
    ]

    position = build_inline_position(file="src/list.py", line=3, diff_refs=DIFF_REFS, changes=changes)

    assert position.old_path == "src/list.py"
    assert position.new_path == "src/list.py"
    assert position.old_line == 3
    assert position.new_line is None


def test_build_inline_position_uses_both_paths_of_a_rename() -> None:
    """Should carry the pre- and post-rename paths, which GitLab uses to locate the diff file."""
    changes = [GitLabMRChangeSchema(diff=TWO_HUNK_DIFF, old_path="src/old.py", new_path="src/new.py")]

    position = build_inline_position(file="src/new.py", line=131, diff_refs=DIFF_REFS, changes=changes)

    assert position.old_path == "src/old.py"
    assert position.new_path == "src/new.py"
    assert position.old_line == 129
    assert position.new_line == 131


def test_build_inline_position_keeps_the_new_line_when_the_line_is_not_in_the_diff() -> None:
    """An unresolvable line keeps the payload unchanged, so the inline fallback still applies."""
    position = build_inline_position(file="src/db.py", line=900, diff_refs=DIFF_REFS, changes=CHANGES)

    assert position.old_path is None
    assert position.new_path == "src/db.py"
    assert position.old_line is None
    assert position.new_line == 900


def test_build_inline_position_keeps_the_new_line_when_the_file_is_not_in_the_changes() -> None:
    """A file GitLab did not report keeps the payload unchanged."""
    position = build_inline_position(file="src/absent.py", line=12, diff_refs=DIFF_REFS, changes=CHANGES)

    assert position.old_path is None
    assert position.new_path == "src/absent.py"
    assert position.old_line is None
    assert position.new_line == 12


def test_build_inline_position_keeps_the_new_line_when_the_diff_is_missing() -> None:
    """GitLab omits the diff body for large files, which must not break comment creation."""
    changes = [GitLabMRChangeSchema(diff=None, old_path="src/big.py", new_path="src/big.py")]

    position = build_inline_position(file="src/big.py", line=12, diff_refs=DIFF_REFS, changes=changes)

    assert position.old_path is None
    assert position.new_path == "src/big.py"
    assert position.old_line is None
    assert position.new_line == 12


def test_build_inline_position_keeps_the_new_line_when_the_diff_does_not_parse() -> None:
    """A diff body we cannot parse must degrade, not raise."""
    changes = [
        GitLabMRChangeSchema(diff="@@ not a hunk header @@\n+x\n", old_path="src/odd.py", new_path="src/odd.py")
    ]

    position = build_inline_position(file="src/odd.py", line=1, diff_refs=DIFF_REFS, changes=changes)

    assert position.old_path is None
    assert position.new_path == "src/odd.py"
    assert position.old_line is None
    assert position.new_line == 1


def test_build_inline_position_keeps_the_new_line_for_a_diff_without_hunks() -> None:
    """GitLab reports binary files without any hunk, so there is nothing to resolve against."""
    changes = [
        GitLabMRChangeSchema(
            diff="Binary files a/logo.png and b/logo.png differ\n",
            old_path="logo.png",
            new_path="logo.png",
        )
    ]

    position = build_inline_position(file="logo.png", line=1, diff_refs=DIFF_REFS, changes=changes)

    assert position.old_path is None
    assert position.new_path == "logo.png"
    assert position.old_line is None
    assert position.new_line == 1


def test_build_inline_position_keeps_the_new_line_without_any_changes() -> None:
    """An empty changes payload keeps the payload unchanged."""
    position = build_inline_position(file="src/db.py", line=131, diff_refs=DIFF_REFS, changes=[])

    assert position.old_path is None
    assert position.new_path == "src/db.py"
    assert position.old_line is None
    assert position.new_line == 131
