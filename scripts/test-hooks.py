#!/usr/bin/env python3
"""Stdlib regressions for protocol delivery, record templates and host hooks."""

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
PLUGIN = REPO_ROOT / "plugins" / "agentic-protocol"
SCRIPTS = PLUGIN / "hooks" / "scripts"
PROGRESS_SKILL = PLUGIN / "skills" / "update-progress" / "SKILL.md"
RULE = PLUGIN / "rules" / "agentic-protocol-core.mdc"
HOSTS = ("cursor", "codex", "codebuddy")

# The agent reads PROGRESS.md itself, so these headings are a linking and resume
# convention rather than a hook contract. The template still has to name them
# consistently, or links and recovery guidance drift apart.
RESUME_SECTIONS = ("Objective", "Constraints", "Current State", "Next Check")
HISTORY_SECTIONS = ("Milestones", "Deferred")


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load("session-context")
hp = load("hook_payload")


def record(**sections):
    return "# Project Progress\n" + "".join(
        f"\n## {name.replace('_', ' ')}\n{value}\n" for name, value in sections.items()
    )


def headings(text):
    return {line[3:].strip() for line in text.splitlines() if line.startswith("## ")}


FULL_PROGRESS = record(
    Objective="Choose a retrieval method using measured recall and latency.",
    Constraints="Keep the dataset fixed; no external upload.",
    Current_State="Pilot implemented, but quality and latency remain unmeasured. No blocker.",
    Next_Check="Measure the pilot; select it only if both criteria pass, otherwise compare B.",
    Milestones="2026-09-16 — Pilot built; [evidence](worklog/2026-09-16.md#pilot).",
    Deferred="Broader survey; revisit only if both candidates fail.",
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

    def run_session(self, host, **payload):
        payload.setdefault("workspace_root", str(self.project))
        payload.setdefault("cwd", str(self.project))
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "session-context.py"), host],
            input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)


class ProtocolDelivery(ProjectCase):
    def test_only_codex_receives_the_protocol(self):
        self.put("PROGRESS.md", FULL_PROGRESS)
        for host in HOSTS:
            with self.subTest(host=host):
                payload = self.run_session(host)
                if host == "codex":
                    message = payload["hookSpecificOutput"]["additionalContext"]
                    self.assertIn("[Agentic 方法论]", message)
                    self.assertIn("# Agentic 方法论", message)
                else:
                    self.assertEqual(payload, {})

    def test_protocol_body_excludes_frontmatter(self):
        message = sc.build_message("codex")
        self.assertNotIn("alwaysApply", message)
        self.assertNotIn("description:", message)
        self.assertIn("## Project Memory", message)

    def test_work_record_is_never_injected(self):
        self.put("PROGRESS.md", FULL_PROGRESS)
        for host in HOSTS:
            with self.subTest(host=host):
                message = json.dumps(self.run_session(host))
                self.assertNotIn("Choose a retrieval method", message)
                self.assertNotIn("quality and latency remain unmeasured", message)
                self.assertNotIn("Source: .agent-context/", message)

    def test_hook_never_reads_or_writes_the_work_record(self):
        self.put("PROGRESS.md", FULL_PROGRESS)
        before = {path: path.read_bytes() for path in self.folder.rglob("*") if path.is_file()}
        for host in HOSTS:
            with patch.object(pathlib.Path, "iterdir", side_effect=AssertionError("No record scan")), \
                 patch.object(pathlib.Path, "glob", side_effect=AssertionError("No record glob")):
                sc.build_message(host)
        self.assertEqual({path: path.read_bytes() for path in self.folder.rglob("*") if path.is_file()}, before)

    def test_missing_context_directory_is_not_an_error(self):
        self.folder.rmdir()
        for host in HOSTS:
            with self.subTest(host=host):
                payload = self.run_session(host)
                self.assertEqual(payload == {}, host != "codex")
        self.assertFalse(self.folder.exists())

    def test_unreadable_rule_emits_a_no_op(self):
        with patch.object(sc, "PROTOCOL_PATH", self.project / "absent.mdc"):
            self.assertEqual(sc.build_message("codex"), "")
        output = io.StringIO()
        with redirect_stdout(output):
            sc.emit("")
        self.assertEqual(json.loads(output.getvalue()), {})


class HookRegistration(unittest.TestCase):
    def test_hosts_with_a_rules_slot_register_no_session_start(self):
        cursor = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
        codebuddy = json.loads((PLUGIN / "hooks" / "codebuddy-hooks.json").read_text())
        self.assertNotIn("sessionStart", cursor["hooks"])
        self.assertNotIn("SessionStart", codebuddy["hooks"])
        self.assertEqual(sc.INJECT_PROTOCOL_HOSTS, frozenset({"codex"}))

    def test_codex_registers_session_start_for_the_protocol(self):
        config = json.loads((PLUGIN / "hooks" / "codex-hooks.json").read_text())
        hooks = config["hooks"]["SessionStart"][0]["hooks"]
        self.assertEqual(len(hooks), 1)
        self.assertIn("session-context.py", hooks[0]["command"])

    def test_codebuddy_hook_commands_use_correct_host_and_root(self):
        data = json.loads((PLUGIN / "hooks" / "codebuddy-hooks.json").read_text())
        for matchers in data["hooks"].values():
            for matcher in matchers:
                for hook in matcher["hooks"]:
                    self.assertIn(" codebuddy", hook["command"])
                    self.assertIn("${CODEBUDDY_PLUGIN_ROOT}", hook["command"])


class Contracts(ProjectCase):
    def template(self, index=0):
        skill = PROGRESS_SKILL.read_text(encoding="utf-8")
        return skill.split("```markdown\n")[1:][index].split("```", 1)[0]

    def test_template_partitions_resume_and_history(self):
        self.assertEqual(headings(self.template()), set(RESUME_SECTIONS) | set(HISTORY_SECTIONS))

    def test_daily_template_is_evidence_not_a_second_state_map(self):
        skill = PROGRESS_SKILL.read_text(encoding="utf-8")
        self.assertEqual(len(skill.split("```markdown\n")[1:]), 2)
        daily = self.template(1)
        self.assertTrue(daily.startswith("# Work Log — YYYY-MM-DD"))
        self.assertIn("## Pilot", daily)
        self.assertTrue(headings(daily).isdisjoint(RESUME_SECTIONS))

    def test_protocol_tells_the_agent_to_read_the_record_itself(self):
        body = RULE.read_text(encoding="utf-8")
        self.assertIn("PROGRESS.md", body)
        for retired in ("resume budget", "Omitted source sections", "SessionStart carries"):
            self.assertNotIn(retired, body)

    def test_canonical_rule_keeps_the_expected_sections(self):
        self.assertEqual(
            headings(RULE.read_text(encoding="utf-8")),
            {
                "Startup",
                "Goal Alignment",
                "Execution",
                "Efficiency",
                "Evidence",
                "Response Style",
                "Project Memory",
            },
        )

    def test_skill_surfaces_do_not_promise_hook_injection(self):
        for path in list((PLUGIN / "skills").rglob("*.md")) + [PLUGIN / "README.md"]:
            text = path.read_text(encoding="utf-8")
            for retired in ("SessionStart carries", "resume budget", "Over-budget"):
                self.assertNotIn(retired, text, str(path))

    def test_codex_context_fits_host_limit(self):
        config = json.loads((PLUGIN / "hooks" / "codex-hooks.json").read_text())
        limit = config["hooks"]["SessionStart"][0]["hooks"][0]["additionalContextLimit"]
        self.assertIs(type(limit), int)
        self.assertGreater(limit, 0)
        # Codex approx_token_count: codex-rs/utils/string/src/truncate.rs (2026-09-17).
        approx_tokens = (len(sc.build_message("codex").encode("utf-8")) + 3) // 4
        self.assertLessEqual(approx_tokens, limit)

    def test_retired_workflow_is_not_advertised(self):
        self.assertFalse((PLUGIN / "skills" / "handoff").exists())
        surfaces = list((PLUGIN / "skills").rglob("*.md")) + [REPO_ROOT / "README.md", PLUGIN / "README.md"]
        for path in surfaces:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/handoff", text, str(path))
            for line in text.splitlines():
                if "touched files" in line.lower():
                    # The prohibition may be written in either language; what the
                    # contract requires is that any mention forbids the retired field
                    # rather than advertises it.
                    self.assertTrue(
                        "do not list touched files" in line.lower()
                        or "不列 touched files" in line,
                        str(path),
                    )
        for path in (PLUGIN / "hooks").glob("*.json"):
            self.assertNotIn("handoff", path.read_text(), str(path))


class PackagingContracts(ProjectCase):
    def setUp(self):
        super().setUp()
        for directory in ("plugins", ".cursor-plugin", ".codebuddy-plugin", ".agents"):
            shutil.copytree(REPO_ROOT / directory, self.project / directory,
                            ignore=shutil.ignore_patterns("__pycache__"))
        self.package = self.project / "plugins" / "agentic-protocol"
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

    def write_rule(self, total_chars, always_applied=True):
        """Rewrite the canonical rule to an exact whole-file character count."""
        path = self.package / "rules" / "agentic-protocol-core.mdc"
        original = path.read_text(encoding="utf-8")
        head = original[:original.index("---", 3) + 3]
        if not always_applied:
            head = head.replace("alwaysApply: true", "alwaysApply: false")
        head += "\n\n# Agentic 方法论\n\n"
        self.assertLess(len(head), total_chars)
        path.write_text(head + "x" * (total_chars - len(head)), encoding="utf-8")
        self.assertEqual(len(path.read_text(encoding="utf-8")), total_chars)

    def test_rejects_always_applied_rule_over_host_injection_limit(self):
        # CodeBuddy drops an over-budget rule silently (support, 2026-09-18), so
        # only a failing check can prevent shipping a protocol that never loads.
        self.write_rule(6001)
        code, output = self.validate()
        self.assertNotEqual(code, 0, output)
        self.assertIn("host injection limit", output.lower())

    def test_accepts_always_applied_rule_at_the_host_injection_limit(self):
        self.write_rule(6000)
        code, output = self.validate()
        self.assertEqual(code, 0, output)

    def test_warns_before_the_host_injection_limit_without_failing(self):
        self.write_rule(5900)
        code, output = self.validate()
        self.assertEqual(code, 0, output)
        self.assertIn("100 below", output)

    def test_on_demand_rule_is_not_bound_by_the_injection_limit(self):
        self.write_rule(9000, always_applied=False)
        code, output = self.validate()
        self.assertEqual(code, 0, output)
        self.assertNotIn("host injection limit", output.lower())

    def test_shipped_rules_stay_within_the_host_injection_limit(self):
        self.assertLessEqual(len(RULE.read_text(encoding="utf-8")), 6000)

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
        installed = home / ".cursor/plugins/local/agentic-protocol"
        for name in generated:
            self.assertFalse((installed / name).exists(), name)
            self.assertEqual((self.package / name).read_text(), "generated fixture")
        self.assertFalse((installed / "hooks/scripts/__pycache__").exists())
        self.assertEqual(unrelated.read_text(), "keep")
        for name in ("rules/agentic-protocol-core.mdc", "hooks/scripts/session-context.py", "README.md"):
            self.assertEqual((installed / name).read_bytes(), (self.package / name).read_bytes())


class HostDispatch(unittest.TestCase):
    def test_unknown_host_is_rejected(self):
        with self.assertRaises(SystemExit):
            hp.parse_host(["session-context.py", "claude"])

    def test_all_hosts_are_known(self):
        for host in HOSTS:
            self.assertEqual(hp.parse_host(["x", host]), host)

    def test_session_envelope_is_claude_style(self):
        output = io.StringIO()
        with redirect_stdout(output):
            sc.emit("protocol text")
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["hookSpecificOutput"]["additionalContext"], "protocol text")
        self.assertEqual(payload["hookSpecificOutput"]["hookEventName"], "SessionStart")

    def test_non_injecting_host_prints_a_no_op(self):
        """A host that loads the rule itself must get `{}` and exit 0, never an error."""
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "session-context.py"), "cursor"],
            input="", capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
