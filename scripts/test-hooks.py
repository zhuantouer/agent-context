#!/usr/bin/env python3
"""Behaviour tests for the hook scripts. Standard library only, like the hooks.

Usage: python3 scripts/test-hooks.py

`validate-template.mjs` checks structure and `py_compile` checks syntax; neither
can tell whether the session-start capsule still carries what a resuming agent
needs. These tests cover the failures that actually happened: the whole-file
injection, the tail slice that dropped the last sections, a signal that fired on
bookkeeping-only turns, and fields going missing without a word.
"""

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "plugins" / "agent-context" / "hooks" / "scripts"
HANDOFF_SKILL = REPO_ROOT / "plugins" / "agent-context" / "skills" / "handoff" / "SKILL.md"


def load(name):
    """Import a hyphenated hook script by path."""
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load("session-context")


def handoff(**sections):
    body = "# Agent Handoff\n"
    for name, value in sections.items():
        body += f"\n## {name.replace('_', ' ')}\n{value}\n"
    return body


FULL_HANDOFF = handoff(
    Current_Task="Ship the capsule.",
    Status="In progress.",
    Next_Action="Run python3 scripts/test-hooks.py and confirm it passes.",
    Blockers="Waiting on a Codex install to verify the injection.",
    User_Instructions="Always attach a recommendation.",
    Validation="Last run: validator — passed.",
    Notes_for_Next_Agent="The stop signal reads the dirty worktree, not the branch.",
)


class CapsuleFields(unittest.TestCase):
    def test_carries_every_template_section(self):
        capsule, caveat = sc.build_capsule(FULL_HANDOFF)
        for name in sc.CAPSULE_ORDER:
            self.assertIn(f"## {name}", capsule, f"{name} missing from the capsule")
        self.assertEqual(caveat, "", "a complete handoff must not ask for a file read")

    def test_user_instructions_survive_a_long_handoff(self):
        """The constraint fields are the ones the old tail slice used to lose."""
        long_handoff = handoff(
            Current_Task="x" * 4000,
            Status="y" * 4000,
            Next_Action="z" * 4000,
            Blockers="Waiting on review.",
            User_Instructions="Never force-push.",
            Validation="Nothing ran yet.",
            Notes_for_Next_Agent="Prior attempt failed on the Codex path.",
        )
        capsule, _ = sc.build_capsule(long_handoff)
        self.assertIn("Never force-push.", capsule)
        self.assertIn("Waiting on review.", capsule)
        self.assertIn("Prior attempt failed on the Codex path.", capsule)

    def test_unknown_section_is_named_not_silently_dropped(self):
        text = FULL_HANDOFF + "\n## Rollback Plan\nRevert the capsule commit.\n"
        capsule, caveat = sc.build_capsule(text)
        self.assertNotIn("Rollback Plan\nRevert", capsule)
        self.assertIn("Rollback Plan", caveat)

    def test_placeholder_sections_are_skipped(self):
        text = handoff(Current_Task="No active task.", Next_Action="Pick up the backlog.", Blockers="(none)")
        capsule, caveat = sc.build_capsule(text)
        self.assertNotIn("## Current Task", capsule)
        self.assertNotIn("## Blockers", capsule)
        self.assertIn("Pick up the backlog.", capsule)
        self.assertEqual(caveat, "")

    def test_duplicate_heading_keeps_the_last_body(self):
        text = handoff(Next_Action="stale plan") + "\n## Next Action\nfresh plan\n"
        capsule, _ = sc.build_capsule(text)
        self.assertIn("fresh plan", capsule)
        self.assertNotIn("stale plan", capsule)


class CapsuleSize(unittest.TestCase):
    def test_worst_case_stays_under_the_backstop(self):
        """Per-field caps must bound the total by construction, so no field ever
        has to be dropped at runtime."""
        worst = handoff(**{name.replace(" ", "_"): "x" * 5000 for name in sc.CAPSULE_ORDER})
        capsule, _ = sc.build_capsule(worst)
        self.assertLessEqual(len(capsule), sc.CAPSULE_MAX_CHARS)

    def test_real_handoff_costs_far_less_than_the_file(self):
        text = (REPO_ROOT / ".agent-context" / "HANDOFF.md").read_text(encoding="utf-8")
        capsule, _ = sc.build_capsule(text)
        self.assertLess(len(capsule), len(text), "the capsule must be cheaper than the file")
        self.assertLessEqual(len(capsule), sc.CAPSULE_MAX_CHARS)

    def test_every_capsule_field_has_a_cap(self):
        for name in sc.CAPSULE_ORDER:
            self.assertIn(name, sc.FIELD_MAX_CHARS, f"{name} has no per-field cap")


class Clipping(unittest.TestCase):
    def test_marks_clipped_fields(self):
        clipped, was_clipped = sc.clip_field("Validation", "v" * 900)
        self.assertTrue(was_clipped)
        self.assertTrue(clipped.endswith("…"))

    def test_cuts_on_a_chinese_sentence_boundary(self):
        value = "第一句已经写完。" * 40
        clipped, was_clipped = sc.clip_field("Validation", value)
        self.assertTrue(was_clipped)
        self.assertTrue(clipped.rstrip(" …").endswith("。"), clipped[-20:])

    def test_short_values_are_untouched(self):
        self.assertEqual(sc.clip_field("Blockers", "None yet"), ("None yet", False))


class HandoffSection(unittest.TestCase):
    def test_missing_directory_reports_state_only(self):
        with tempfile.TemporaryDirectory() as project:
            message = sc.build_handoff_section(project)
            self.assertIn("No .agent-context/", message)
            self.assertNotIn("bootstrap-context", message, "the protocol owns instructions")

    def test_empty_handoff_reports_state_only(self):
        with tempfile.TemporaryDirectory() as project:
            agent_dir = pathlib.Path(project, ".agent-context")
            agent_dir.mkdir()
            (agent_dir / "HANDOFF.md").write_text("")
            message = sc.build_handoff_section(project)
            self.assertIn("missing or empty", message)
            self.assertNotIn("Load other", message, "the protocol owns instructions")

    def test_unstructured_handoff_still_resumes(self):
        with tempfile.TemporaryDirectory() as project:
            agent_dir = pathlib.Path(project, ".agent-context")
            agent_dir.mkdir()
            (agent_dir / "HANDOFF.md").write_text("hand-typed notes, no headings at all")
            message = sc.build_handoff_section(project)
            self.assertIn("hand-typed notes", message)


class TemplateContract(unittest.TestCase):
    def test_skill_template_defines_every_capsule_field(self):
        """If the template and the capsule disagree, the hook injects blanks."""
        template = HANDOFF_SKILL.read_text(encoding="utf-8")
        for name in sc.CAPSULE_ORDER:
            self.assertIn(f"## {name}", template, f"{name} is not in the handoff template")

    def test_retired_handoff_field_stays_retired(self):
        """`touched files` was dropped from the handoff on 2026-08-27 because git
        already carries it. It then reappeared in two skills that described the
        handoff independently, so assert it instead of sweeping again. The clause
        that forbids the field is the one place allowed to name it."""
        surfaces = list((REPO_ROOT / "plugins" / "agent-context").rglob("*.md"))
        surfaces.append(REPO_ROOT / "README.md")
        offenders = []
        for path in surfaces:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "touched files" in line.lower() and "do not list touched files" not in line.lower():
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}")
        self.assertEqual(offenders, [], f"retired handoff field reappeared at {offenders}")


class StopSignal(unittest.TestCase):
    """Runs the real script the way a host does: JSON on stdin, JSON on stdout."""

    def run_stop(self, project, **payload):
        payload.setdefault("status", "completed")
        payload.setdefault("workspace_root", str(project))
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "handoff-signal.py"), "cursor"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name)
        agent_dir = self.project / ".agent-context"
        agent_dir.mkdir()
        (agent_dir / "HANDOFF.md").write_text(FULL_HANDOFF)
        (agent_dir / "PROGRESS.md").write_text("# ledger\n")
        (agent_dir / "MEMORY.md").write_text("# memory\n")
        (self.project / "app.py").write_text("print('hi')\n")
        # Commit so the worktree starts clean: git collapses an untracked directory
        # into one entry, which would hide which file a turn actually touched.
        git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run([*git, "init", "-q"], cwd=self.project, check=True)
        subprocess.run([*git, "add", "-A"], cwd=self.project, check=True)
        subprocess.run([*git, "commit", "-qm", "base"], cwd=self.project, check=True)
        self.addCleanup(self.tmp.cleanup)

    def touch(self, relative, mtime):
        path = self.project / relative
        path.write_text(path.read_text() + "\n# edit\n")
        os.utime(path, (mtime, mtime))

    def test_fires_when_code_is_newer_than_the_handoff(self):
        self.touch(".agent-context/HANDOFF.md", 1_000_000)
        self.touch("app.py", 2_000_000)
        self.assertIn("followup_message", self.run_stop(self.project))

    def test_silent_when_only_memory_files_changed(self):
        """Bookkeeping must not ask for more bookkeeping."""
        self.touch(".agent-context/HANDOFF.md", 1_000_000)
        self.touch(".agent-context/PROGRESS.md", 3_000_000)
        self.touch(".agent-context/MEMORY.md", 3_000_000)
        self.assertEqual(self.run_stop(self.project), {})

    def test_silent_when_the_handoff_is_current(self):
        self.touch("app.py", 1_000_000)
        self.touch(".agent-context/HANDOFF.md", 2_000_000)
        self.assertEqual(self.run_stop(self.project), {})

    def test_silent_on_an_aborted_turn(self):
        self.touch(".agent-context/HANDOFF.md", 1_000_000)
        self.touch("app.py", 2_000_000)
        self.assertEqual(self.run_stop(self.project, status="aborted"), {})

    def test_fails_open_outside_a_project(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(self.run_stop(pathlib.Path(empty)), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
