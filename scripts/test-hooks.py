#!/usr/bin/env python3
"""Stdlib regressions for single-record recovery, legacy input and host hooks."""

import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = REPO_ROOT / "plugins" / "agent-context"
SCRIPTS = PLUGIN / "hooks" / "scripts"
PROGRESS_SKILL = PLUGIN / "skills" / "update-progress" / "SKILL.md"
HOSTS = ("cursor", "codex", "codebuddy")


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load("session-context")
hp = load("hook_payload")
ws = load("work-signal")


def record(**sections):
    return "# Project Progress\n" + "".join(
        f"\n## {name.replace('_', ' ')}\n{value}\n" for name, value in sections.items()
    )


FULL_PROGRESS = record(
    Objective="Choose a retrieval method using measured recall and latency.",
    Constraints="Keep the dataset fixed; no external upload.",
    Current_State="Pilot implemented, but quality and latency remain unmeasured. No blocker.",
    Next_Check="Measure the pilot; select it only if both criteria pass, otherwise compare B.",
    Milestones="2026-09-16 — Pilot built; [evidence](worklog/2026-09-16.md#pilot).",
    Deferred="Broader survey; revisit only if both candidates fail.",
)
LEGACY_HANDOFF = record(
    Objective="Reduce waiting time.", Current_Task="Measure the pilot.",
    Status="Implementation complete; wait time unmeasured.", Next_Action="Run the pilot check.",
    Blockers="Waiting on approval.", User_Instructions="Never upload private samples.",
    Validation="Unit tests passed; outcome unknown.", Notes_for_Next_Agent="Compare with the baseline.",
)


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = pathlib.Path(self.tmp.name)
        self.folder = self.project / ".agent-context"
        self.folder.mkdir()

    def put(self, name, text):
        (self.folder / name).write_text(text, encoding="utf-8")

    def message(self, host="cursor"):
        return sc.build_message(host, self.project)


class SingleRecord(ProjectCase):
    def test_progress_alone_restores_goal_conclusion_and_next_check(self):
        text = FULL_PROGRESS + "\n" + "Historical experiment. " * 3000
        self.put("PROGRESS.md", text)
        message = self.message()
        for name in sc.CAPSULE_ORDER:
            self.assertIn(sc.split_sections(FULL_PROGRESS)[name], message)
        self.assertNotIn("Historical experiment.", message)
        self.assertNotIn("Broader survey", message)
        self.assertEqual((self.folder / "PROGRESS.md").read_text(encoding="utf-8"), text)
        self.assertFalse((self.folder / "HANDOFF.md").exists())

    def test_unified_progress_wins_over_stale_handoff(self):
        self.put("PROGRESS.md", record(Current_State="Current conclusion."))
        self.put("HANDOFF.md", record(Status="Obsolete conclusion."))
        with patch.object(sc, "read_record", wraps=sc.read_record) as reader:
            message = self.message()
        self.assertIn("Current conclusion.", message)
        self.assertNotIn("Obsolete conclusion.", message)
        self.assertEqual(reader.call_count, 1)

    def test_empty_unified_state_does_not_resurrect_legacy_task(self):
        self.put("PROGRESS.md", record(Current_State="", Work_Log="Finished earlier work."))
        self.put("HANDOFF.md", LEGACY_HANDOFF)
        self.assertNotIn("Measure the pilot", self.message())
        self.assertIn("No current-state content", self.message())

    def test_completed_task_keeps_objective_and_remaining_gap(self):
        self.put("PROGRESS.md", record(
            Objective="Reduce support wait time.",
            Current_State="No active task. Pilot complete; actual wait time still unknown.",
            Next_Check="(none)",
        ))
        message = self.message()
        self.assertIn("Reduce support wait time", message)
        self.assertIn("actual wait time still unknown", message)
        self.assertNotIn("## Next Check", message)

    def test_each_host_recovers_progress_with_correct_envelope(self):
        self.put("PROGRESS.md", FULL_PROGRESS)
        for host in HOSTS:
            with self.subTest(host=host):
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS / "session-context.py"), host],
                    input=json.dumps({"workspace_root": str(self.project), "cwd": str(self.project)}),
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                message = payload["additional_context"] if host == "cursor" else payload["hookSpecificOutput"]["additionalContext"]
                self.assertIn("Choose a retrieval method", message)
                self.assertIn("Source: .agent-context/PROGRESS.md", message)
                self.assertEqual("Operating protocol" in message, host == "codex")

    def test_missing_context_does_not_write_or_request_bootstrap(self):
        self.folder.rmdir()
        self.assertIn("No .agent-context/", self.message())
        self.assertNotIn("bootstrap-context", self.message())
        self.assertFalse(self.folder.exists())

    def test_missing_or_empty_records_report_state_only(self):
        for value in (None, "", "   "):
            if value is not None:
                self.put("PROGRESS.md", value)
            self.assertIn("no legacy work state", self.message())
            self.assertNotIn("Refresh", self.message())

    def test_unreadable_progress_fails_open(self):
        (self.folder / "PROGRESS.md").mkdir()
        self.assertIn("unreadable", self.message())

    def test_fence_diagnostic_uses_original_file_line_numbers(self):
        text = "\n\n## Current State\nPending.\n\n```text\nexample\n"
        self.put("PROGRESS.md", text)
        for host in HOSTS:
            self.assertIn("Unclosed code fence at source line 6", self.message(host))
        self.assertEqual((self.folder / "PROGRESS.md").read_text(), text)


class DailyLogRecovery(ProjectCase):
    def test_milestones_stay_on_demand_without_extra_section_warning(self):
        capsule, caveat = sc.build_capsule(record(
            Current_State="Resume the pilot.",
            Milestones="Pilot built; [evidence](worklog/2026-09-15.md#pilot).",
        ))
        self.assertIn("Resume the pilot.", capsule)
        self.assertNotIn("Pilot built", capsule)
        self.assertEqual(caveat, "")

    def test_resume_after_overnight_weekend_or_long_gap_needs_no_daily_file(self):
        for source_date, resume_date in (
            ("2026-09-15", "2026-09-16"),
            ("2026-09-11", "2026-09-14"),
            ("2026-08-01", "2026-09-16"),
        ):
            with self.subTest(source_date=source_date, resume_date=resume_date):
                link = f"worklog/{source_date}.md#pilot"
                text = record(
                    Objective="Choose a method within the latency limit.",
                    Current_State=f"Pilot latency passed; recall unknown. [Evidence]({link}).",
                    Next_Check="Measure recall before selecting the method.",
                )
                self.put("PROGRESS.md", text)
                before = set(self.folder.rglob("*"))
                for host in HOSTS:
                    with patch.object(sc, "read_record", wraps=sc.read_record) as reader:
                        message = self.message(host)
                    self.assertIn(link, message)
                    self.assertIn("recall unknown", message)
                    self.assertIn("Measure recall", message)
                    self.assertEqual([call.args[0] for call in reader.call_args_list], [self.folder / "PROGRESS.md"])
                self.assertFalse((self.folder / "worklog" / f"{resume_date}.md").exists())
                self.assertEqual(set(self.folder.rglob("*")), before)
                self.assertEqual((self.folder / "PROGRESS.md").read_text(), text)

    def test_interleaved_tasks_keep_the_relevant_link_not_the_latest_date(self):
        log = self.folder / "worklog"
        log.mkdir()
        (log / "2026-09-11.md").write_text("## Pilot\nTask A evidence.\n")
        (log / "2026-09-15.md").write_text("## Repair\nUnrelated task B evidence.\n")
        link = "worklog/2026-09-11.md#pilot"
        self.put("PROGRESS.md", record(
            Current_State=f"Resume task A; recall unknown. [A]({link}).",
            Next_Check="Measure A, not task B.",
        ))
        with patch.object(sc, "read_record", wraps=sc.read_record) as reader:
            message = self.message()
        self.assertIn(link, message)
        self.assertNotIn("2026-09-15.md", message)
        self.assertNotIn("Task A evidence", message)
        self.assertNotIn("Unrelated task B evidence", message)
        self.assertEqual(reader.call_count, 1)

    def test_history_growth_does_not_change_recovery_or_trigger_directory_scan(self):
        self.put("PROGRESS.md", FULL_PROGRESS)
        baseline = self.message()
        log = self.folder / "worklog"
        log.mkdir()
        for day in range(1, 29):
            (log / f"2026-08-{day:02}.md").write_text("Detailed evidence. " * 1000)
        with patch.object(pathlib.Path, "iterdir", side_effect=AssertionError("No daily-log scan")), \
             patch.object(pathlib.Path, "glob", side_effect=AssertionError("No daily-log glob")):
            self.assertEqual(self.message(), baseline)

    def test_orphan_logs_are_not_used_to_invent_current_state(self):
        log = self.folder / "worklog"
        log.mkdir()
        (log / "2026-09-15.md").write_text("Old completed task; not today's objective.")
        message = self.message()
        self.assertIn("PROGRESS.md is missing", message)
        self.assertNotIn("Old completed task", message)
        self.assertFalse((self.folder / "PROGRESS.md").exists())

    def test_embedded_legacy_work_log_still_loads_without_migration(self):
        text = record(Current_State="Recall unknown.", Work_Log="Historical evidence. " * 5000)
        self.put("PROGRESS.md", text)
        message = self.message()
        self.assertIn("Recall unknown.", message)
        self.assertNotIn("Historical evidence.", message)
        self.assertFalse((self.folder / "worklog").exists())
        self.assertEqual((self.folder / "PROGRESS.md").read_text(), text)


class LegacyRecovery(ProjectCase):
    def test_all_handoff_fields_remain_available(self):
        self.put("HANDOFF.md", LEGACY_HANDOFF)
        message = self.message()
        for value in sc.split_sections(LEGACY_HANDOFF).values():
            self.assertIn(value, message)
        self.assertIn("Legacy records", message)
        self.assertFalse((self.folder / "PROGRESS.md").exists())

    def test_old_progress_and_handoff_are_separate_not_silently_merged(self):
        self.put("PROGRESS.md", record(Objective="Durable goal.", Current_Focus="Older focus.", Completed="Archive." * 5000))
        self.put("HANDOFF.md", record(Status="Newer tactical result.", User_Instructions="No uploads."))
        message = self.message()
        for value in ("Durable goal.", "Older focus.", "Newer tactical result.", "No uploads.", "sources may disagree"):
            self.assertIn(value, message)
        self.assertNotIn("Archive.", message)

    def test_old_progress_alone_is_not_discarded(self):
        self.put("PROGRESS.md", record(Current_Focus="Evaluate options.", Blockers="Budget unknown."))
        self.assertIn("Evaluate options.", self.message())
        self.assertIn("Budget unknown.", self.message())

    def test_no_broader_goal_is_invented(self):
        self.put("HANDOFF.md", record(Current_Task="Fix the timeout."))
        self.assertIn("Fix the timeout.", self.message())
        self.assertNotIn("## Objective", self.message())

    def test_short_unstructured_notes_are_preserved(self):
        self.put("HANDOFF.md", "hand-typed notes, no headings at all")
        self.assertIn("hand-typed notes, no headings at all", self.message())

    def test_long_unstructured_notes_are_not_sliced_into_claims(self):
        self.put("HANDOFF.md", "Allowed only after " * 1000 + "approval.")
        message = self.message()
        self.assertIn("Unstructured record omitted", message)
        self.assertNotIn("Allowed only after", message)

    def test_history_only_record_stays_on_demand(self):
        self.put("PROGRESS.md", record(Completed="Historical result. " * 5000))
        self.assertNotIn("Historical result.", self.message())
        self.assertIn("No current-state content", self.message())


class ExcerptIntegrity(unittest.TestCase):
    def test_short_fields_are_unchanged(self):
        for value in ("No upload without approval.", "未验证，不代表通过。", "p95 < 80ms; recall >= 0.9"):
            self.assertEqual(sc.clip_field("Constraints", value), (value, False))

    def test_long_constraint_is_not_presented_as_complete_permission(self):
        value = "Allowed only with " + "required review " * 50 + "; never publish without approval."
        clipped, shortened = sc.clip_field("Constraints", value)
        self.assertTrue(shortened)
        self.assertNotIn("Allowed only", clipped)
        self.assertIn("omitted", clipped.lower())

    def test_overlong_fields_name_the_source_section(self):
        for name in sc.CAPSULE_ORDER:
            with self.subTest(name=name):
                capsule, caveat = sc.build_capsule(record(**{name: "前提。" * 2000}))
                self.assertIn(f"## {name}", capsule)
                self.assertNotIn("前提", capsule)
                self.assertIn(name, caveat)
                self.assertIn("Omitted source sections", caveat)

    def test_long_state_does_not_displace_goal_or_constraints(self):
        for goal in ("Select a useful method, not a larger survey.", "选择有用的方法，而不是扩大资料数量。"):
            capsule, caveat = sc.build_capsule(record(Objective=goal, Constraints="Do not change the dataset.", Current_State="x" * 5000))
            self.assertIn(goal, capsule)
            self.assertIn("Do not change the dataset.", capsule)
            self.assertIn("Current State", caveat)

    def test_placeholder_sections_are_skipped(self):
        capsule, caveat = sc.build_capsule(record(Current_State="No active task.", Constraints="(none)"))
        self.assertIn("No active task.", capsule)
        self.assertNotIn("## Constraints", capsule)
        self.assertEqual(caveat, "")

    def test_duplicate_heading_keeps_last_body(self):
        text = record(Current_State="Old.") + "\n## Current State\nNew.\n"
        capsule, _ = sc.build_capsule(text)
        self.assertIn("New.", capsule)
        self.assertNotIn("Old.", capsule)

    def test_unknown_sections_are_signalled_without_unbounded_heading_lists(self):
        text = FULL_PROGRESS + "".join(f"\n## Extra {n}\nunknown\n" for n in range(1000))
        capsule, caveat = sc.build_capsule(text)
        self.assertNotIn("unknown", capsule)
        self.assertIn("Additional source sections", caveat)
        self.assertLess(len(caveat), 100)

    def test_current_fields_fit_backstop_at_exact_caps(self):
        text = record(**{name: "x" * cap for name, cap in sc.FIELD_MAX_CHARS.items()})
        capsule, caveat = sc.build_capsule(text)
        self.assertLessEqual(len(capsule), sc.CAPSULE_MAX_CHARS)
        self.assertEqual(caveat, "")

    def test_fenced_history_cannot_override_current_state(self):
        for fence in ("```", "~~~~"):
            text = FULL_PROGRESS + f"\n{fence}markdown\n## Current State\nFake conclusion.\n{fence}\n"
            capsule, caveat = sc.build_capsule(text)
            self.assertNotIn("Fake conclusion.", capsule)
            self.assertIn("quality and latency remain unmeasured", capsule)
            self.assertEqual(caveat, "")

    def test_unclosed_fences_are_reported_without_inventing_headings(self):
        for fence in ("```", "~~~~"):
            for prefix in ("", "## Current State\nPending.\n", "## Milestones\nOld result.\n"):
                for fill in ("short", "x" * 3000):
                    with self.subTest(fence=fence, prefix=prefix, long=len(fill) > 100):
                        text = prefix + f"{fence}markdown\n{fill}\n## Next Check\nNot a real heading.\n"
                        capsule, caveat = sc.build_capsule(text)
                        self.assertIn("Unclosed code fence", caveat)
                        self.assertNotIn("Next Check", sc.split_sections(text))
                        self.assertNotIn("Not a real heading", caveat)
                        self.assertLess(len(caveat), 250)

    def test_only_a_matching_fence_closes_the_block(self):
        for opening, closing, closed in (
            ("```", "````", True),
            ("~~~~", "~~~~", True),
            ("~~~~", "~~~", False),
            ("```", "~~~", False),
            ("```", "``` trailing text", False),
        ):
            with self.subTest(opening=opening, closing=closing):
                text = f"## Current State\nPending.\n{opening}text\nexample\n{closing}\n## Next Check\nMeasure.\n"
                _, caveat = sc.build_capsule(text)
                self.assertEqual("Unclosed code fence" in caveat, not closed)
                self.assertEqual("Next Check" in sc.split_sections(text), closed)

    def test_unclosed_fence_diagnostic_reaches_each_host_and_legacy_source(self):
        for host in HOSTS:
            for name, text in (
                ("PROGRESS.md", "## Current State\nPending.\n## Milestones\n```\n## Next Check\nHidden.\n"),
                ("HANDOFF.md", "## Status\nPending.\n```\n## Next Action\nHidden.\n"),
            ):
                with self.subTest(host=host, source=name):
                    message = sc.record_excerpt(name, text)
                    output = io.StringIO()
                    with redirect_stdout(output):
                        sc.emit(host, message)
                    payload = json.loads(output.getvalue())
                    emitted = payload["additional_context"] if host == "cursor" else payload["hookSpecificOutput"]["additionalContext"]
                    self.assertIn(f"Source: .agent-context/{name}", emitted)
                    self.assertIn("Unclosed code fence", emitted)

    def test_history_growth_does_not_increase_excerpt(self):
        small = sc.build_capsule(FULL_PROGRESS)
        large = sc.build_capsule(FULL_PROGRESS + "\n" + "Deferred historical detail. " * 5000)
        self.assertEqual(small, large)


class Contracts(ProjectCase):
    def test_template_partitions_resume_and_history(self):
        skill = PROGRESS_SKILL.read_text(encoding="utf-8")
        template = skill.split("```markdown\n", 1)[1].split("```", 1)[0]
        headings = set(sc.split_sections(template))
        self.assertEqual(headings, set(sc.CAPSULE_ORDER) | {"Milestones", "Deferred"})
        self.assertEqual(sc.HISTORY_SECTIONS, {"Milestones", "Deferred", "Work Log"})
        self.assertNotIn("Work Log", headings)
        self.assertEqual(set(sc.CAPSULE_ORDER), set(sc.FIELD_MAX_CHARS))
        self.assertTrue(set(sc.CAPSULE_ORDER).isdisjoint(sc.HISTORY_SECTIONS))
        capsule, caveat = sc.build_capsule(template)
        self.assertEqual(set(sc.split_sections(capsule)), set(sc.CAPSULE_ORDER))
        self.assertEqual(caveat, "")

    def test_daily_template_is_evidence_not_a_second_state_map(self):
        skill = PROGRESS_SKILL.read_text(encoding="utf-8")
        templates = skill.split("```markdown\n")[1:]
        self.assertEqual(len(templates), 2)
        daily = templates[1].split("```", 1)[0]
        self.assertTrue(daily.startswith("# Work Log — YYYY-MM-DD"))
        self.assertIn("## Pilot", daily)
        self.assertTrue(set(sc.split_sections(daily)).isdisjoint(sc.CAPSULE_ORDER))

    def assert_codex_context_fits_limit(self):
        config = json.loads((PLUGIN / "hooks" / "codex-hooks.json").read_text())
        limit = config["hooks"]["SessionStart"][0]["hooks"][0]["additionalContextLimit"]
        self.assertIs(type(limit), int)
        self.assertGreater(limit, 0)
        # Codex approx_token_count: codex-rs/utils/string/src/truncate.rs (2026-09-17).
        approx_tokens = (len(self.message("codex").encode("utf-8")) + 3) // 4
        self.assertLessEqual(approx_tokens, limit)

    def test_worst_case_complete_codex_messages_fit_host_limit(self):
        for unified in (True, False):
            for fill in ("x", "中", "\U00020000"):
                with self.subTest(unified=unified, fill=fill):
                    caps = sc.FIELD_MAX_CHARS if unified else sc.LEGACY_PROGRESS_CAPS
                    self.put("PROGRESS.md", record(**{name: fill * cap for name, cap in caps.items()}))
                    self.put("HANDOFF.md", record(**{name: fill * cap for name, cap in sc.LEGACY_HANDOFF_CAPS.items()}))
                    self.assert_codex_context_fits_limit()

    def test_unstructured_legacy_pair_fits_codex_limit(self):
        for fill in ("x", "中", "\U00020000"):
            with self.subTest(fill=fill):
                self.put("PROGRESS.md", fill * 2200)
                self.put("HANDOFF.md", fill * 2200)
                self.assert_codex_context_fits_limit()

    def test_codex_limit_check_uses_utf8_bytes_and_rounds_up(self):
        config = json.loads((PLUGIN / "hooks" / "codex-hooks.json").read_text())
        limit = config["hooks"]["SessionStart"][0]["hooks"][0]["additionalContextLimit"]
        at_limit = "\U00020000" * limit
        with patch.object(sc, "build_message", return_value=at_limit):
            self.assert_codex_context_fits_limit()
        with patch.object(sc, "build_message", return_value=at_limit + "x"):
            with self.assertRaises(AssertionError):
                self.assert_codex_context_fits_limit()

    def test_retired_workflow_is_not_advertised(self):
        self.assertFalse((PLUGIN / "skills" / "handoff").exists())
        surfaces = list((PLUGIN / "skills").rglob("*.md")) + [REPO_ROOT / "README.md", PLUGIN / "README.md"]
        for path in surfaces:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/handoff", text, str(path))
            for line in text.splitlines():
                if "touched files" in line.lower():
                    self.assertIn("do not list touched files", line.lower(), str(path))
        for path in (PLUGIN / "hooks").glob("*.json"):
            self.assertNotIn("handoff", path.read_text(), str(path))

    def test_codebuddy_hook_commands_use_correct_host_and_root(self):
        data = json.loads((PLUGIN / "hooks" / "codebuddy-hooks.json").read_text())
        for matchers in data["hooks"].values():
            for matcher in matchers:
                for hook in matcher["hooks"]:
                    self.assertIn(" codebuddy", hook["command"])
                    self.assertIn("${CODEBUDDY_PLUGIN_ROOT}", hook["command"])


class StopSignal(ProjectCase):
    def setUp(self):
        super().setUp()
        self.put("PROGRESS.md", FULL_PROGRESS)
        self.put("MEMORY.md", "# Lessons\n")
        (self.project / "app.py").write_text("print('hi')\n")
        git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run([*git, "init", "-q"], cwd=self.project, check=True)
        subprocess.run([*git, "add", "-A"], cwd=self.project, check=True)
        subprocess.run([*git, "commit", "-qm", "base"], cwd=self.project, check=True)

    def run_stop(self, host="cursor", entry="work-signal.py", **payload):
        payload.setdefault("workspace_root", str(self.project))
        payload.setdefault("cwd", str(self.project))
        payload.setdefault("status", "completed")
        payload.setdefault("last_assistant_message", "done")
        command = [sys.executable, str(SCRIPTS / entry), host] if entry.endswith(".py") else [str(SCRIPTS / entry)]
        result = subprocess.run(
            command,
            input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def large_file(self):
        (self.project / "app.py").write_text("pass\n" * ws.LINE_THRESHOLD)

    def test_dirty_code_does_not_request_bookkeeping(self):
        os.utime(self.folder / "PROGRESS.md", (1, 1))
        (self.project / "app.py").write_text("print('new')\n")
        for host in HOSTS:
            self.assertEqual(self.run_stop(host), {})

    def test_missing_records_do_not_request_handoff(self):
        (self.folder / "PROGRESS.md").unlink()
        (self.project / "app.py").write_text("print('new')\n")
        self.assertEqual(self.run_stop(), {})

    def test_memory_only_turn_is_silent(self):
        self.put("PROGRESS.md", FULL_PROGRESS + "changed\n")
        self.put("MEMORY.md", "lessons\n" * 1000)
        for host in HOSTS:
            self.assertEqual(self.run_stop(host), {})

    def test_daily_log_only_turn_does_not_request_more_bookkeeping(self):
        log = self.folder / "worklog"
        log.mkdir()
        (log / "2026-09-16.md").write_text("## Pilot\nEvidence recorded.\n" * 1000)
        for host in HOSTS:
            self.assertEqual(self.run_stop(host), {})
        self.assertEqual((self.folder / "PROGRESS.md").read_text(), FULL_PROGRESS)

    def test_large_file_signal_survives_without_handoff_on_all_hosts(self):
        self.large_file()
        for host in HOSTS:
            result = self.run_stop(host)
            key = "followup_message" if host == "cursor" else "systemMessage"
            self.assertEqual(set(result), {key})
            self.assertIn("app.py", result[key])
            self.assertNotIn("HANDOFF", result[key])
            self.assertNotIn("PROGRESS", result[key])

    def test_cached_python_entry_matches_current_entry(self):
        for large in (False, True):
            if large:
                self.large_file()
            for host in HOSTS:
                with self.subTest(large=large, host=host):
                    expected = self.run_stop(host)
                    actual = self.run_stop(host, entry="handoff-signal.py")
                    self.assertEqual(actual, expected)
                    self.assertNotIn("HANDOFF", json.dumps(actual))
        self.assertFalse((self.folder / "HANDOFF.md").exists())
        self.assertEqual((self.folder / "PROGRESS.md").read_text(), FULL_PROGRESS)

    @unittest.skipIf(os.name == "nt", "Cursor shell entry is a POSIX executable")
    def test_cached_shell_entry_matches_current_entry(self):
        for large in (False, True):
            if large:
                self.large_file()
            with self.subTest(large=large):
                self.assertEqual(
                    self.run_stop(entry="stop-handoff-reminder.sh"),
                    self.run_stop(entry="stop-work-review.sh"),
                )

    def test_cached_entry_preserves_turn_guards(self):
        self.large_file()
        for host in HOSTS:
            self.assertEqual(self.run_stop(host, entry="handoff-signal.py", status="aborted"), {})
        for host in ("codex", "codebuddy"):
            self.assertEqual(self.run_stop(host, entry="handoff-signal.py", stop_hook_active=True), {})

    def test_aborted_and_error_turns_stay_silent(self):
        self.large_file()
        for host in HOSTS:
            for status in ("aborted", "error"):
                self.assertEqual(self.run_stop(host, status=status), {})

    def test_claude_hosts_respect_stop_loop_guard(self):
        self.large_file()
        for host in ("codex", "codebuddy"):
            self.assertEqual(self.run_stop(host, stop_hook_active=True), {})

    def test_codex_still_requires_assistant_output(self):
        self.large_file()
        self.assertEqual(self.run_stop("codex", last_assistant_message=""), {})

    def test_no_git_project_fails_open(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(self.run_stop(workspace_root=empty, cwd=empty), {})

    def test_detection_exception_fails_open(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["work-signal.py", "cursor"]), patch.object(ws, "run", side_effect=OSError), redirect_stdout(output):
            self.assertEqual(ws.main(), 0)
        self.assertEqual(json.loads(output.getvalue()), {})


class PackagingContracts(ProjectCase):
    def setUp(self):
        super().setUp()
        for directory in ("plugins", ".cursor-plugin", ".codebuddy-plugin", ".agents"):
            shutil.copytree(REPO_ROOT / directory, self.project / directory,
                            ignore=shutil.ignore_patterns("__pycache__"))
        self.package = self.project / "plugins" / "agent-context"
        self.marketplaces = [self.project / host / "marketplace.json"
                             for host in (".cursor-plugin", ".codebuddy-plugin", ".agents/plugins")]

    def validate(self):
        if not shutil.which("node"):
            self.skipTest("Node.js is required for packaging validation")
        result = subprocess.run(
            ["node", str(REPO_ROOT / "scripts" / "validate-template.mjs")],
            cwd=self.project, capture_output=True, text=True, timeout=30,
        )
        return result.returncode, result.stdout + result.stderr

    def test_marketplace_metadata_version_is_independent(self):
        for path in self.marketplaces:
            data = json.loads(path.read_text())
            data.setdefault("metadata", {})["version"] = "9.0.0"
            path.write_text(json.dumps(data))
        code, output = self.validate()
        self.assertEqual(code, 0, output)

    def test_rejects_each_host_manifest_version_drift(self):
        for host in HOSTS:
            path = self.package / f".{host}-plugin" / "plugin.json"
            original = path.read_text()
            with self.subTest(host=host):
                data = json.loads(original)
                data["version"] = "9.0.0"
                path.write_text(json.dumps(data))
                code, output = self.validate()
                self.assertNotEqual(code, 0, output)
                self.assertIn("version mismatch", output.lower())
            path.write_text(original)

    def test_rejects_marketplace_plugin_version_drift(self):
        for path in self.marketplaces:
            original = path.read_text()
            with self.subTest(marketplace=path.parent.name):
                data = json.loads(original)
                data["plugins"][0]["version"] = "9.0.0"
                path.write_text(json.dumps(data))
                code, output = self.validate()
                self.assertNotEqual(code, 0, output)
                self.assertIn("version mismatch", output.lower())
            path.write_text(original)

    def test_coordinated_plugin_version_change_passes(self):
        for host in HOSTS:
            path = self.package / f".{host}-plugin" / "plugin.json"
            data = json.loads(path.read_text())
            data["version"] = "0.2.1"
            path.write_text(json.dumps(data))
        for path in self.marketplaces:
            data = json.loads(path.read_text())
            for entry in data["plugins"]:
                if "version" in entry:
                    entry["version"] = "0.2.1"
            path.write_text(json.dumps(data))
        code, output = self.validate()
        self.assertEqual(code, 0, output)

    @unittest.skipIf(os.name == "nt", "Local installer requires Bash")
    def test_install_excludes_generated_files_without_touching_sources_or_other_plugins(self):
        scripts = self.project / "scripts"
        scripts.mkdir()
        installer = scripts / "install-local.sh"
        shutil.copy2(REPO_ROOT / "scripts" / "install-local.sh", installer)
        generated = ("hooks/scripts/__pycache__/old.pyc", "hooks/scripts/orphan.pyc",
                     "hooks/scripts/orphan.pyo", ".DS_Store", ".plugins-cache.json", ".plugins-cache.json.bak")
        for name in generated:
            path = self.package / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("generated fixture")
        home = self.project / "test home"
        unrelated = home / ".cursor/plugins/local/unrelated/keep.txt"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("keep")
        result = subprocess.run(
            ["bash", str(installer), "cursor"], cwd=self.project,
            env=dict(os.environ, HOME=str(home)), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed = home / ".cursor/plugins/local/agent-context"
        for name in generated:
            self.assertFalse((installed / name).exists(), name)
            self.assertEqual((self.package / name).read_text(), "generated fixture")
        self.assertFalse((installed / "hooks/scripts/__pycache__").exists())
        self.assertEqual(unrelated.read_text(), "keep")
        for name in ("rules/agent-context-core.mdc", "hooks/scripts/handoff-signal.py", "README.md"):
            self.assertEqual((installed / name).read_bytes(), (self.package / name).read_bytes())
        self.assertTrue(os.access(installed / "hooks/scripts/session-start.sh", os.X_OK))


class HostDispatch(unittest.TestCase):
    def test_unknown_host_is_rejected(self):
        with self.assertRaises(SystemExit):
            hp.parse_host(["session-context.py", "claude"])

    def test_all_hosts_are_known(self):
        for host in HOSTS:
            self.assertEqual(hp.parse_host(["x", host]), host)

    def test_session_envelopes(self):
        for host in HOSTS:
            output = io.StringIO()
            with redirect_stdout(output):
                sc.emit(host, "work state")
            payload = json.loads(output.getvalue())
            if host == "cursor":
                self.assertEqual(payload, {"additional_context": "work state"})
            else:
                self.assertEqual(payload["hookSpecificOutput"]["additionalContext"], "work state")
                self.assertEqual(payload["hookSpecificOutput"]["hookEventName"], "SessionStart")


if __name__ == "__main__":
    unittest.main(verbosity=2)
