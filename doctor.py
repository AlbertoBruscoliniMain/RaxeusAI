"""
Diagnostica del sistema RaxeusAI.

Idea adattata da OpenJarvis (src/openjarvis/cli/doctor_cmd.py).
Verifica: versione Python, raggiungibilità Ollama, presenza modelli, dipendenze.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

from config import MODEL, OLLAMA_URL, VISION_MODEL
from hardware import detect_hardware, recommend_model


@dataclass
class CheckResult:
    name: str
    status: str  # "ok", "warn", "fail"
    message: str


def _check_python() -> CheckResult:
    v = sys.version_info
    s = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= (3, 10):
        return CheckResult("Python", "ok", s)
    return CheckResult("Python", "fail", f"{s} (richiesto >= 3.10)")


def _check_ollama() -> CheckResult:
    import urllib.error
    import urllib.request

    base = OLLAMA_URL.rstrip("/").removesuffix("/v1")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=4) as r:
            if r.status == 200:
                return CheckResult("Ollama", "ok", base)
    except (urllib.error.URLError, OSError) as e:
        return CheckResult("Ollama", "fail", f"non raggiungibile: {e}")
    return CheckResult("Ollama", "fail", "risposta inattesa")


def _check_models() -> list[CheckResult]:
    import json
    import urllib.error
    import urllib.request

    base = OLLAMA_URL.rstrip("/").removesuffix("/v1")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=4) as r:
            data = json.loads(r.read())
    except (urllib.error.URLError, OSError):
        return [CheckResult("Modelli", "warn", "Impossibile elencare (Ollama down)")]

    installed = {m.get("name", "").split(":")[0]: m.get("name", "")
                 for m in data.get("models", [])}
    installed_full = {m.get("name", "") for m in data.get("models", [])}

    out: list[CheckResult] = []
    for label, target in (("MODEL", MODEL), ("VISION_MODEL", VISION_MODEL)):
        base_name = target.split(":")[0]
        if target in installed_full:
            out.append(CheckResult(f"{label} ({target})", "ok", "installato"))
        elif base_name in installed:
            out.append(CheckResult(
                f"{label} ({target})", "warn",
                f"manca tag esatto, presente {installed[base_name]}",
            ))
        else:
            out.append(CheckResult(
                f"{label} ({target})", "fail",
                f"non installato — esegui: ollama pull {target}",
            ))
    return out


def _check_deps() -> list[CheckResult]:
    deps = [
        ("openai", "openai"),
        ("flask", "flask"),
        ("ddgs", "ddgs"),
        ("googlesearch-python", "googlesearch"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("pypdf", "pypdf"),
        ("chromadb", "chromadb"),
        ("pywebview", "webview"),
        ("yt-dlp", "yt_dlp"),
    ]
    out: list[CheckResult] = []
    for pkg, mod in deps:
        try:
            __import__(mod)
            out.append(CheckResult(f"dep {pkg}", "ok", "ok"))
        except ImportError:
            out.append(CheckResult(f"dep {pkg}", "warn", f"mancante (pip install {pkg})"))
    return out


def _check_hardware() -> CheckResult:
    hw = detect_hardware()
    suggested = recommend_model(hw)
    note = "" if suggested == MODEL else f" (suggerito: {suggested})"
    return CheckResult(
        "Hardware",
        "ok",
        f"{hw.platform} {hw.cpu_brand} {hw.ram_gb}GB RAM{note}",
    )


_ICON = {"ok": "✓", "warn": "!", "fail": "✗"}


def run() -> int:
    print("=== RaxeusAI Doctor ===\n")
    checks: list[CheckResult] = []
    checks.append(_check_python())
    checks.append(_check_hardware())
    checks.append(_check_ollama())
    checks.extend(_check_models())
    checks.extend(_check_deps())

    fail = warn = 0
    for c in checks:
        icon = _ICON.get(c.status, "?")
        print(f"  [{icon}] {c.name}: {c.message}")
        if c.status == "fail":
            fail += 1
        elif c.status == "warn":
            warn += 1

    print()
    if fail:
        print(f"× {fail} problemi critici, {warn} avvisi.")
        return 1
    if warn:
        print(f"! {warn} avvisi (ma il sistema è utilizzabile).")
        return 0
    print("✓ Tutti i controlli OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
