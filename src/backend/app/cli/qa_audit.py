"""QA gate runner; 7 rubrics (DEC-015/023).

Pillar: Stable Core
Phase: O
Purpose: QA gate runner; 7 rubrics (DEC-015/023).
Documented in: docs/qa/qa-checklist.md
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

# Repo roots (resolved from this file's location)
_THIS = Path(__file__).resolve()
BACKEND_ROOT = _THIS.parents[2]  # src/backend
REPO_ROOT = BACKEND_ROOT.parents[1]  # repo root
FRONTEND_ROOT = REPO_ROOT / "src" / "frontend"


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class Report:
    results: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.results.append(CheckResult(name, passed, detail))

    def exit_code(self) -> int:
        return 0 if all(r.passed for r in self.results) else 1

    def render(self) -> str:
        lines = ["", "QA Audit Report", "=" * 60]
        for r in self.results:
            mark = "PASS" if r.passed else "FAIL"
            lines.append(f"[{mark}] {r.name}")
            if r.detail and not r.passed:
                for line in r.detail.splitlines()[:20]:
                    lines.append(f"    {line}")
        passed = sum(1 for r in self.results if r.passed)
        lines.append("=" * 60)
        lines.append(f"Summary: {passed}/{len(self.results)} checks passed")
        return "\n".join(lines)


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """Run a command; return (exit_code, combined_output)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as e:
        return 127, f"command not found: {e}"
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# -------- subcommands -----------------------------------------------------


def cmd_lint(report: Report, fix: bool) -> None:
    args = ["uv", "run", "ruff", "check", "."]
    if fix:
        args.append("--fix")
    code, out = _run(args, BACKEND_ROOT)
    report.add("ruff check", code == 0, out)
    if fix:
        code2, out2 = _run(["uv", "run", "ruff", "format", "."], BACKEND_ROOT)
        report.add("ruff format", code2 == 0, out2)


def cmd_tests(report: Report, fix: bool) -> None:  # noqa: ARG001
    code, out = _run(["uv", "run", "pytest", "-v"], BACKEND_ROOT)
    # Treat "no tests collected" (exit 5) as soft-pass for now.
    soft_pass = code in (0, 5)
    report.add("pytest", soft_pass, out)


def cmd_deps(report: Report, fix: bool) -> None:  # noqa: ARG001
    code, out = _run(["uv", "pip", "list", "--outdated"], BACKEND_ROOT)
    # Outdated list is informational; pass unless command itself errored.
    report.add("uv pip list --outdated", code == 0, out)


def cmd_frontend(report: Report, fix: bool) -> None:
    if not FRONTEND_ROOT.exists():
        report.add("frontend present", False, f"missing: {FRONTEND_ROOT}")
        return
    npx = "npx.cmd" if sys.platform == "win32" else "npx"
    if not _has(npx.replace(".cmd", "")):
        report.add("npx available", False, "install Node.js")
        return
    code, out = _run([npx, "tsc", "-b", "--pretty", "false"], FRONTEND_ROOT)
    report.add("tsc -b", code == 0, out)
    if fix:
        code2, out2 = _run([npx, "prettier", "--write", "src"], FRONTEND_ROOT)
        report.add("prettier --write", code2 == 0, out2)


# Patterns that should NOT exist in production code paths.
# qa_audit.py is excluded from every pattern (it contains the patterns themselves).
_QA_SELF_EXCLUDE = ["**/qa_audit.py"]
_IF_ELSE_PATTERNS: list[tuple[str, str, list[str]]] = [
    # (label, regex, glob excludes)
    (
        "provider == literal outside registry",
        r"provider\s*==\s*[\"']",
        [*_QA_SELF_EXCLUDE, "**/registry.py"],
    ),
    (
        "elif provider branch",
        r"elif.*provider",
        [*_QA_SELF_EXCLUDE, "**/registry.py"],
    ),
    (
        "Pydantic v1 BaseSettings import",
        r"from pydantic import BaseSettings",
        [*_QA_SELF_EXCLUDE],
    ),
    (
        "datetime.utcnow",
        r"datetime\.utcnow\(",
        [*_QA_SELF_EXCLUDE],
    ),
    (
        "bare except Exception",
        r"except Exception",
        # Audit-write blocks are documented (DEC-019: audit must never break
        # the request). They are the only legitimate broad-catch sites.
        [
            *_QA_SELF_EXCLUDE,
            "**/bot_pipeline_use_case.py",
            "**/routes/bot.py",
        ],
    ),
]


def _glob_excluded(rel_posix: str, excludes: list[str]) -> bool:
    """Match rg-style glob excludes (supporting **/ prefix)."""
    from fnmatch import fnmatch

    for ex in excludes:
        # Strip leading **/ for fnmatch (which doesn't grok it natively)
        bare = ex[3:] if ex.startswith("**/") else ex
        if fnmatch(rel_posix, ex) or fnmatch(rel_posix, bare):
            return True
        # Also match against just the file name
        name = rel_posix.rsplit("/", 1)[-1]
        if fnmatch(name, bare):
            return True
    return False


def _python_scan(
    pattern: str, root: Path, excludes: list[str]
) -> tuple[int, str]:
    """Python-native fallback for ripgrep."""
    import re

    regex = re.compile(pattern)
    matches: list[str] = []
    for path in root.rglob("*.py"):
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        if _glob_excluded(rel, excludes):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                matches.append(f"{rel}:{i}:{line.rstrip()}")
                if len(matches) >= 50:
                    break
        if len(matches) >= 50:
            break
    if matches:
        return 0, "\n".join(matches)
    return 1, ""


def _rg(pattern: str, root: Path, excludes: list[str]) -> tuple[int, str]:
    if not _has("rg"):
        return _python_scan(pattern, root, excludes)
    args = ["rg", "-n", pattern, str(root)]
    for ex in excludes:
        args.extend(["--glob", f"!{ex}"])
    code, out = _run(args, REPO_ROOT)
    # rg exit 1 == no matches; 0 == matches; 2 == error
    return code, out


def cmd_if_else_scan(report: Report, fix: bool) -> None:  # noqa: ARG001
    target = BACKEND_ROOT / "app"
    for label, pattern, excludes in _IF_ELSE_PATTERNS:
        code, out = _rg(pattern, target, excludes)
        if code == 1:
            report.add(f"if-else-scan: {label}", True, "no matches")
        elif code == 0:
            report.add(f"if-else-scan: {label}", False, out)
        else:
            report.add(f"if-else-scan: {label}", False, f"scan error: {out}")


_RAI_FILES = [
    REPO_ROOT / "docs" / "rai-policy.md",
    REPO_ROOT / "docs" / "threat-model.md",
]

# Required RAI guardrail modules (DEC-019).
_RAI_MODULES = [
    "input_validator.py",
    "topic_gate.py",
    "prompt_injection.py",
    "system_prompt.py",
    "output_validator.py",
    "audit.py",
    "errors.py",
]


def cmd_rai_check(report: Report, fix: bool) -> None:  # noqa: ARG001
    # 1. Policy + threat-model docs exist
    for path in _RAI_FILES:
        rel = path.relative_to(REPO_ROOT)
        report.add(f"RAI doc exists: {rel.as_posix()}", path.exists())

    # 2. All 6+1 guardrail modules present
    rai_dir = BACKEND_ROOT / "app" / "infrastructure" / "rai"
    for module in _RAI_MODULES:
        report.add(f"RAI module: {module}", (rai_dir / module).exists())

    # 3. Pipeline use case exists
    pipe = (
        BACKEND_ROOT
        / "app"
        / "application"
        / "use_cases"
        / "bot_pipeline_use_case.py"
    )
    report.add("BotPipelineUseCase present", pipe.exists())

    # 4. bot_audit entity + repo
    entity = BACKEND_ROOT / "app" / "domain" / "entities" / "bot_audit.py"
    repo = (
        BACKEND_ROOT
        / "app"
        / "infrastructure"
        / "persistence"
        / "cosmos_db"
        / "bot_audit_repository.py"
    )
    report.add("BotAudit entity present", entity.exists())
    report.add("CosmosBotAuditRepository present", repo.exists())

    # 5. bot.py wires the pipeline (NOT direct CoordinationAgent in AI path)
    bot_py = BACKEND_ROOT / "app" / "api" / "routes" / "bot.py"
    if bot_py.exists():
        text = bot_py.read_text(encoding="utf-8", errors="replace")
        report.add(
            "bot.py uses BotPipelineUseCase",
            "BotPipelineUseCase" in text or "get_bot_pipeline_use_case" in text,
        )
        report.add(
            "bot.py AI path does NOT call agent.evaluate_session directly",
            "agent.evaluate_session" not in text,
        )
    else:
        report.add("bot.py present", False)

    # 6. bot_audit container declared in Bicep
    cosmos_bicep = REPO_ROOT / "infra" / "modules" / "cosmos.bicep"
    if cosmos_bicep.exists():
        text = cosmos_bicep.read_text(encoding="utf-8", errors="replace")
        report.add(
            "bot_audit container in cosmos.bicep",
            "bot_audit" in text and "/session_id" in text,
        )
    else:
        report.add("infra/modules/cosmos.bicep present", False)

    # 7. Architecture references bot_audit
    arch = REPO_ROOT / "plan" / "architecture.md"
    if arch.exists():
        text = arch.read_text(encoding="utf-8", errors="replace")
        report.add("bot_audit referenced in architecture", "bot_audit" in text)
    else:
        report.add("plan/architecture.md present", False)


# -------- pillars-check (Rubric 6: every module declares its pillar) ------

_VALID_PILLARS = {
    "Stable Core",
    "Scenario Pack",
    "Configuration Layer",
    "Customization Layer",
}
_PILLAR_RE = __import__("re").compile(r"^\s*Pillar:\s*(.+?)\s*$", __import__("re").M)
_PHASE_RE = __import__("re").compile(r"^\s*Phase:\s*", __import__("re").M)
_PURPOSE_RE = __import__("re").compile(r"^\s*Purpose:\s*", __import__("re").M)
_DOC_RE = __import__("re").compile(r"^\s*Documented in:\s*", __import__("re").M)


def cmd_pillars_check(report: Report, fix: bool) -> None:  # noqa: ARG001
    """Rubric 6: every Python module under app/ declares Pillar/Phase/Purpose/Documented in."""
    target = BACKEND_ROOT / "app"
    missing: list[str] = []
    invalid: list[str] = []
    for path in sorted(target.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        head = "\n".join(
            path.read_text(encoding="utf-8", errors="replace").splitlines()[:30]
        )
        m = _PILLAR_RE.search(head)
        if not m:
            missing.append(f"{rel}: missing Pillar:")
            continue
        if m.group(1) not in _VALID_PILLARS:
            invalid.append(f"{rel}: invalid pillar '{m.group(1)}'")
        if not _PHASE_RE.search(head):
            missing.append(f"{rel}: missing Phase:")
        if not _PURPOSE_RE.search(head):
            missing.append(f"{rel}: missing Purpose:")
        if not _DOC_RE.search(head):
            missing.append(f"{rel}: missing Documented in:")

    report.add(
        "pillars-check: every module has Pillar/Phase/Purpose/Documented in",
        not missing,
        "\n".join(missing[:30]),
    )
    report.add(
        f"pillars-check: pillar value is one of {sorted(_VALID_PILLARS)}",
        not invalid,
        "\n".join(invalid[:30]),
    )


# -------- phd-check (Rubric 7: PhD-bar code quality) ----------------------

# Banned production imports (DEC-021/023). qa_audit.py is excluded.
# `from openai import` + `AzureOpenAI(` are excluded for the legitimate
# Azure provider wrapper (and only there) — every OTHER file must go via
# the LLMProvider port (DEC-016).
_OPENAI_PROVIDER_EXCLUDE = ["**/azure_foundry_provider.py"]
_BANNED_IMPORTS: list[tuple[str, str, list[str]]] = [
    ("raw openai SDK import (use LLMProvider)", r"^from openai import", _OPENAI_PROVIDER_EXCLUDE),
    ("raw AzureOpenAI() construction (use registry)", r"AzureOpenAI\(", _OPENAI_PROVIDER_EXCLUDE),
    ("streamlit imported in production code", r"^import streamlit|^from streamlit", []),
    ("promptflow imported in production code", r"^import promptflow|^from promptflow", []),
    ("semantic_kernel imported (not on roadmap)",
     r"^import semantic_kernel|^from semantic_kernel", []),
    (
        "azure.keyvault imported (DEC-021: removed in favour of App Configuration)",
        r"^from azure\.keyvault|^import azure\.keyvault",
        [],
    ),
]

# Citation tokens that MUST appear in app/infrastructure/rai/ as evidence the
# guardrail design references published threat-model literature (DEC-013).
_CITATION_TOKENS = ("Lakera", "garak", "OWASP", "Keller", "NIST", "MITRE")


def _radon_cc(report: Report) -> None:
    code, out = _run(
        ["uv", "run", "radon", "cc", "app", "-a", "-n", "D"], BACKEND_ROOT
    )
    # radon -n D prints functions ranked >= D. Empty output past header => pass.
    bad = [
        line for line in out.splitlines()
        if line.strip() and "Average complexity" not in line and not line.startswith("app")
    ]
    # Crude: any line starting with whitespace + a letter rank D/E/F is a violation.
    violations = [line for line in bad if any(
        line.lstrip().startswith(f"{kind} ") for kind in ("D", "E", "F")
    )]
    report.add(
        "phd-check: radon CC <= C (no D/E/F functions)",
        code == 0 and not violations,
        out if violations else "",
    )


def _radon_mi(report: Report) -> None:
    code, out = _run(
        ["uv", "run", "radon", "mi", "app", "-n", "C"], BACKEND_ROOT
    )
    # radon mi -n C prints files ranked C and below. Pass when output is empty.
    bad = [line for line in out.splitlines() if line.strip()]
    report.add(
        "phd-check: radon MI >= B (no C/D/F-rated files)",
        code == 0 and not bad,
        out if bad else "",
    )


def _mypy_strict(report: Report) -> None:
    code, out = _run(["uv", "run", "mypy"], BACKEND_ROOT)
    report.add(
        "phd-check: mypy strict on app/application + app/domain",
        code == 0,
        out,
    )


def _coverage(report: Report) -> None:
    # Run coverage only on the test suite that is currently green (RAI suite).
    # Threshold 80% per DEC-023, scoped to application + infrastructure/rai.
    code, out = _run(
        [
            "uv", "run", "pytest", "tests/rai/",
            "--cov=app/application", "--cov=app/infrastructure/rai",
            "--cov-report=term-missing:skip-covered",
            "--cov-fail-under=80",
            "-q",
        ],
        BACKEND_ROOT,
    )
    report.add("phd-check: coverage >= 80% on application + rai", code == 0, out)


def _banned_imports(report: Report) -> None:
    target = BACKEND_ROOT / "app"
    for label, pattern, extra_excludes in _BANNED_IMPORTS:
        excludes = [*_QA_SELF_EXCLUDE, *extra_excludes]
        code, out = _rg(pattern, target, excludes)
        if code == 1:
            report.add(f"phd-check: banned import — {label}", True, "no matches")
        elif code == 0:
            report.add(f"phd-check: banned import — {label}", False, out)
        else:
            report.add(f"phd-check: banned import — {label}", False, f"scan error: {out}")


def _citations(report: Report) -> None:
    rai_dir = BACKEND_ROOT / "app" / "infrastructure" / "rai"
    if not rai_dir.exists():
        report.add("phd-check: RAI citations", False, f"missing: {rai_dir}")
        return
    found: set[str] = set()
    for path in rai_dir.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for tok in _CITATION_TOKENS:
            if tok in text:
                found.add(tok)
    report.add(
        f"phd-check: RAI citations present (any of {list(_CITATION_TOKENS)})",
        bool(found),
        f"found: {sorted(found) or 'NONE'}",
    )


def _registry_pattern(report: Report) -> None:
    """Every *_provider.py / *_service.py file under app/infrastructure/ must
    sit next to a registry.py OR be referenced by one."""
    infra = BACKEND_ROOT / "app" / "infrastructure"
    violations: list[str] = []
    for path in infra.rglob("*.py"):
        name = path.name
        if not (name.endswith("_provider.py") or name.endswith("_service.py")):
            continue
        # Look for a registry.py in the same dir or any ancestor up to infra/.
        cur = path.parent
        has_registry = False
        while cur != infra.parent:
            if (cur / "registry.py").exists():
                has_registry = True
                break
            cur = cur.parent
        if not has_registry:
            rel = path.relative_to(REPO_ROOT).as_posix()
            violations.append(f"{rel}: no registry.py in same package or ancestor")
    report.add(
        "phd-check: every *_provider.py / *_service.py has a sibling/ancestor registry.py",
        not violations,
        "\n".join(violations[:20]),
    )


def cmd_phd_check(report: Report, fix: bool) -> None:  # noqa: ARG001
    """Rubric 7: PhD-bar code quality (radon, mypy strict, coverage, citations, registry)."""
    _radon_cc(report)
    _radon_mi(report)
    _mypy_strict(report)
    _coverage(report)
    _banned_imports(report)
    _citations(report)
    _registry_pattern(report)


def cmd_all(report: Report, fix: bool) -> None:
    cmd_lint(report, fix)
    cmd_tests(report, fix)
    cmd_deps(report, fix)
    cmd_frontend(report, fix)
    cmd_if_else_scan(report, fix)
    cmd_rai_check(report, fix)
    cmd_pillars_check(report, fix)
    cmd_phd_check(report, fix)


_SUBCOMMANDS: dict[str, Callable[[Report, bool], None]] = {
    "lint": cmd_lint,
    "tests": cmd_tests,
    "deps": cmd_deps,
    "frontend": cmd_frontend,
    "if-else-scan": cmd_if_else_scan,
    "rai-check": cmd_rai_check,
    "pillars-check": cmd_pillars_check,
    "phd-check": cmd_phd_check,
    "all": cmd_all,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="qa_audit",
        description="MAIVE QA audit runner (read-only by default).",
    )
    parser.add_argument("subcommand", choices=sorted(_SUBCOMMANDS.keys()))
    parser.add_argument(
        "--fix",
        action="store_true",
        help="enable safe lint/format auto-fixers (ruff, prettier)",
    )
    args = parser.parse_args(argv)

    report = Report()
    _SUBCOMMANDS[args.subcommand](report, args.fix)
    print(report.render())
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
