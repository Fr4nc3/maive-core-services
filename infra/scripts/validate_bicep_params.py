"""Validate Bicep templates against matching parameters files.

Checks:
1. Parameter names in JSON have no leading/trailing whitespace.
2. Parameter names exactly match Bicep declarations, including casing.
3. Required Bicep params without defaults are present in JSON.
4. azd variable references use approved Azure env-var names.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_PARAM_RE = re.compile(
    r"^(?!//)[ \t]*param\s+(?P<name>[A-Za-z_]\w*)\s+(?P<type>\S+)(?P<rest>.*)",
    re.MULTILINE,
)
_AZD_VAR_RE = re.compile(r"\$\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?:=[^}]*)?\}")
_ENV_VAR_ALLOWLIST = {
    "AZURE_ENV_NAME",
    "AZURE_LOCATION",
    "AZURE_PRINCIPAL_ID",
    "AZURE_SUBSCRIPTION_ID",
}


@dataclass(frozen=True)
class BicepParam:
    name: str
    has_default: bool


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    param_file: str
    bicep_file: str
    param_name: str
    message: str


@dataclass
class ValidationResult:
    pair: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "ERROR" for issue in self.issues)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_bicep_params(path: Path) -> list[BicepParam]:
    params: list[BicepParam] = []
    for match in _PARAM_RE.finditer(_read_text(path)):
        param_type = match.group("type")
        rest = match.group("rest")
        params.append(
            BicepParam(
                name=match.group("name"),
                has_default="=" in rest or param_type.endswith("?"),
            )
        )
    return params


def _sanitize_azd_placeholders(text: str) -> str:
    return re.sub(r'"\$\{[^}]+\}"', '"__azd_placeholder__"', text)


def _extract_keys_regex(text: str) -> list[str]:
    keys: list[str] = []
    in_parameters = False
    for line in text.splitlines():
        if '"parameters"' in line:
            in_parameters = True
            continue
        if in_parameters:
            match = re.match(r'\s*"([^"]+)"\s*:', line)
            if match:
                keys.append(match.group(1))
    return keys


def parse_parameters_json(path: Path) -> list[str]:
    text = _read_text(path)
    try:
        data = json.loads(_sanitize_azd_placeholders(text))
    except json.JSONDecodeError:
        return _extract_keys_regex(text)
    return list(data.get("parameters", {}).keys())


def parse_parameters_env_vars(path: Path) -> dict[str, list[str]]:
    text = _read_text(path)
    return {"azd-env": [match.group("name") for match in _AZD_VAR_RE.finditer(text)]}


def validate_pair(bicep_path: Path, params_path: Path) -> ValidationResult:
    result = ValidationResult(pair=f"{params_path.name} -> {bicep_path.name}")
    bicep_params = parse_bicep_params(bicep_path)
    bicep_names = {param.name for param in bicep_params}
    bicep_names_lower = {param.name.lower(): param.name for param in bicep_params}
    required_bicep = {param.name for param in bicep_params if not param.has_default}
    json_keys = parse_parameters_json(params_path)
    seen_json_keys: set[str] = set()

    for raw_key in json_keys:
        stripped = raw_key.strip()
        if raw_key != stripped:
            result.issues.append(
                ValidationIssue(
                    severity="ERROR",
                    param_file=str(params_path),
                    bicep_file=str(bicep_path),
                    param_name=repr(raw_key),
                    message=f"Parameter has leading/trailing whitespace; expected {stripped!r}.",
                )
            )
        if stripped not in bicep_names:
            suggestion = bicep_names_lower.get(stripped.lower())
            message = (
                f"Case mismatch; Bicep declares '{suggestion}'."
                if suggestion
                else "Parameter has no matching Bicep declaration."
            )
            result.issues.append(
                ValidationIssue(
                    severity="ERROR",
                    param_file=str(params_path),
                    bicep_file=str(bicep_path),
                    param_name=stripped,
                    message=message,
                )
            )
        seen_json_keys.add(stripped)

    for param_name in sorted(required_bicep - seen_json_keys):
        result.issues.append(
            ValidationIssue(
                severity="WARNING",
                param_file=str(params_path),
                bicep_file=str(bicep_path),
                param_name=param_name,
                message="Required Bicep parameter is not supplied in the parameters file.",
            )
        )

    env_vars = parse_parameters_env_vars(params_path)
    for param_name, var_names in sorted(env_vars.items()):
        for var_name in var_names:
            if not var_name.startswith("AZURE_ENV_") and var_name not in _ENV_VAR_ALLOWLIST:
                result.issues.append(
                    ValidationIssue(
                        severity="WARNING",
                        param_file=str(params_path),
                        bicep_file=str(bicep_path),
                        param_name=param_name,
                        message=f"azd variable ${{{var_name}}} is not in the approved allowlist.",
                    )
                )

    return result


def discover_pairs(infra_dir: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for params_path in sorted(infra_dir.rglob("*.parameters.json")):
        stem = params_path.name.removesuffix(".parameters.json")
        bicep_path = params_path.parent / f"{stem}.bicep"
        if not bicep_path.exists():
            bicep_path = params_path.parent / f"{stem.split('.')[0]}.bicep"
        if bicep_path.exists():
            pairs.append((bicep_path, params_path))
        else:
            print(f"[SKIP] No matching Bicep file for {params_path}")
    return pairs


def print_report(results: list[ValidationResult], *, no_color: bool) -> None:
    colors = {
        "ERROR": "" if no_color else "\033[91m",
        "WARNING": "" if no_color else "\033[93m",
        "OK": "" if no_color else "\033[92m",
        "RESET": "" if no_color else "\033[0m",
    }
    total_errors = 0
    total_warnings = 0
    for result in results:
        errors = [issue for issue in result.issues if issue.severity == "ERROR"]
        warnings = [issue for issue in result.issues if issue.severity == "WARNING"]
        total_errors += len(errors)
        total_warnings += len(warnings)
        if errors:
            status = f"{colors['ERROR']}FAIL{colors['RESET']}"
        elif warnings:
            status = f"{colors['WARNING']}WARN{colors['RESET']}"
        else:
            status = f"{colors['OK']}PASS{colors['RESET']}"
        print(f"[{status}] {result.pair}")
        for issue in result.issues:
            print(f"  {issue.severity}: {issue.param_name}: {issue.message}")
    print(f"Total: {total_errors} error(s), {total_warnings} warning(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Bicep parameter mappings.")
    parser.add_argument("--bicep", type=Path, help="Specific Bicep file to validate.")
    parser.add_argument("--params", type=Path, help="Specific parameters JSON file to validate.")
    parser.add_argument("--dir", type=Path, help="Directory to scan for *.parameters.json.")
    parser.add_argument("--strict", action="store_true", help="Fail on errors.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    args = parser.parse_args(argv)

    if args.bicep and args.params:
        pairs = [(args.bicep, args.params)]
    elif args.dir:
        pairs = discover_pairs(args.dir)
    else:
        parser.error("Provide either --bicep/--params or --dir.")

    results = [validate_pair(bicep_path, params_path) for bicep_path, params_path in pairs]
    print_report(results, no_color=args.no_color)
    return 1 if args.strict and any(result.has_errors for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())