"""
Rilevamento hardware per suggerire il modello Ollama più adatto.

Idea adattata da OpenJarvis (src/openjarvis/core/config.py - detect_hardware,
recommend_model). Versione minimale: niente vLLM/MLX, solo Ollama.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GpuInfo:
    vendor: str = ""
    name: str = ""
    vram_gb: float = 0.0
    count: int = 1


@dataclass
class HardwareInfo:
    platform: str = ""
    cpu_brand: str = ""
    cpu_count: int = 0
    ram_gb: float = 0.0
    gpu: Optional[GpuInfo] = None


def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=8,
        )
        return (out.stdout or "").strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ""


def _ram_gb() -> float:
    sysname = platform.system()
    try:
        if sysname == "Darwin":
            raw = _run(["sysctl", "-n", "hw.memsize"])
            return round(int(raw) / (1024 ** 3), 1) if raw else 0.0
        if sysname == "Linux":
            mem = Path("/proc/meminfo")
            if mem.exists():
                for line in mem.read_text().splitlines():
                    if line.startswith("MemTotal"):
                        return round(int(line.split()[1]) / (1024 ** 2), 1)
        if sysname == "Windows":
            try:
                import ctypes

                class _MS(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                ms = _MS()
                ms.dwLength = ctypes.sizeof(_MS)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
                return round(ms.ullTotalPhys / (1024 ** 3), 1)
            except Exception:
                return 0.0
    except (OSError, ValueError):
        pass
    return 0.0


def _cpu_brand() -> str:
    sysname = platform.system()
    if sysname == "Darwin":
        b = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        if b:
            return b
    if sysname == "Windows":
        return os.environ.get("PROCESSOR_IDENTIFIER", platform.processor() or "unknown")
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        try:
            for line in cpuinfo.read_text().splitlines():
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
    return platform.processor() or "unknown"


def _nvidia_gpu() -> Optional[GpuInfo]:
    if not shutil.which("nvidia-smi"):
        return None
    raw = _run([
        "nvidia-smi",
        "--query-gpu=name,memory.total,count",
        "--format=csv,noheader,nounits",
    ])
    if not raw:
        return None
    try:
        parts = [p.strip() for p in raw.splitlines()[0].split(",")]
        return GpuInfo(
            vendor="nvidia",
            name=parts[0],
            vram_gb=round(float(parts[1]) / 1024, 1),
            count=int(parts[2]),
        )
    except (IndexError, ValueError):
        return None


def _apple_gpu(ram_gb: float) -> Optional[GpuInfo]:
    if platform.system() != "Darwin":
        return None
    raw = _run(["system_profiler", "SPDisplaysDataType"])
    if "Apple" not in raw:
        return None
    name = "Apple Silicon"
    for line in raw.splitlines():
        line = line.strip()
        if "Chipset Model" in line:
            name = line.split(":")[-1].strip()
            break
    return GpuInfo(vendor="apple", name=name, vram_gb=ram_gb, count=1)


def detect_hardware() -> HardwareInfo:
    ram = _ram_gb()
    gpu = _nvidia_gpu() or _apple_gpu(ram)
    return HardwareInfo(
        platform=platform.system().lower(),
        cpu_brand=_cpu_brand(),
        cpu_count=os.cpu_count() or 1,
        ram_gb=ram,
        gpu=gpu,
    )


_TIERS = [
    (8,  "qwen3:1.7b"),
    (16, "qwen3:4b"),
    (32, "qwen3:8b"),
    (64, "qwen3:14b"),
]
_FALLBACK = "qwen3:32b"


def _available_gb(hw: HardwareInfo) -> float:
    if hw.gpu and hw.gpu.vram_gb > 0:
        return hw.gpu.vram_gb * max(hw.gpu.count, 1) * 0.9
    if hw.ram_gb > 0:
        return max(hw.ram_gb - 4, 0) * 0.8
    return 0.0


def recommend_model(hw: Optional[HardwareInfo] = None) -> str:
    """Restituisce il model id Ollama suggerito dato l'hardware."""
    hw = hw or detect_hardware()
    avail = _available_gb(hw)
    if avail <= 0:
        return _TIERS[0][1]
    for max_ram, model in _TIERS:
        if avail <= max_ram:
            return model
    return _FALLBACK


def summary(hw: Optional[HardwareInfo] = None) -> str:
    hw = hw or detect_hardware()
    g = hw.gpu
    gpu_str = f"{g.vendor} {g.name} ({g.vram_gb} GB, x{g.count})" if g else "nessuna"
    return (
        f"Piattaforma: {hw.platform}\n"
        f"CPU: {hw.cpu_brand} ({hw.cpu_count} core)\n"
        f"RAM: {hw.ram_gb} GB\n"
        f"GPU: {gpu_str}\n"
        f"Modello suggerito: {recommend_model(hw)}"
    )


if __name__ == "__main__":
    print(summary())
