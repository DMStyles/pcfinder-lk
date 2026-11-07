"""
Hardware query classifier and strict relevance filtering utility for PCFinder LK.
Prevents common store search quirks where stores index sidebar categories or RAM speeds
and return unrelated products (e.g. monitors, power supplies, or laptop skins when searching CPUs).
"""

from __future__ import annotations

import re
from typing import Optional, Set

# Component keywords
CPU_TERMS = {
    "cpu", "processor", "processors", "ryzen", "core", "intel", "amd",
    "threadripper", "celeron", "pentium", "athlon", "xeon", "i3", "i5", "i7", "i9"
}

GPU_TERMS = {
    "gpu", "vga", "graphics", "graphic", "rtx", "gtx", "geforce", "radeon",
    "rx", "arc"
}

RAM_TERMS = {
    "ram", "memory", "ddr4", "ddr5", "ddr3", "dimm", "sodimm"
}

MOTHERBOARD_TERMS = {
    "motherboard", "mainboard", "mobo", "b650", "b550", "b450", "a520",
    "b760", "z790", "x670", "x870", "h610", "z690", "b660", "a620"
}

STORAGE_TERMS = {
    "ssd", "nvme", "hdd", "hard disk", "m.2"
}

MONITOR_TERMS = {
    "monitor", "display", "screen", "panel"
}

PSU_TERMS = {
    "psu", "power supply", "watt", "80+"
}

CASING_TERMS = {
    "casing", "case", "chassis"
}

COOLER_TERMS = {
    "cooler", "cooling", "aio", "liquid cooler", "air cooler", "fan", "fans"
}


def detect_intended_category(query: str) -> Optional[str]:
    """Detect what category of PC hardware the user is searching for."""
    tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    
    # Check for specific GPU patterns like rtx 3060, rx 6600, gtx 1660
    if any(g in tokens for g in ["rtx", "gtx", "radeon", "vga", "gpu"]):
        return "gpu"
    
    # Check for CPU patterns like ryzen 5, i5-12400, i7, core i5
    if any(c in tokens for c in ["ryzen", "threadripper", "athlon"]):
        # Note: if query also says motherboard or b650, prefer motherboard
        if any(m in tokens for m in ["motherboard", "mobo", "b650", "b550", "a520", "a620", "x670", "x870"]):
            return "motherboard"
        return "cpu"

    if any(tok in ["i3", "i5", "i7", "i9", "cpu", "processor", "processors"] for tok in tokens):
        if not any(m in tokens for m in ["motherboard", "cooler", "laptop"]):
            return "cpu"

    if any(r in tokens for r in ["ram", "ddr4", "ddr5", "ddr3", "dimm", "sodimm"]):
        return "ram"

    if any(m in tokens for m in ["motherboard", "mainboard", "mobo"]):
        return "motherboard"

    if any(s in tokens for s in ["ssd", "nvme", "hdd"]):
        return "storage"

    if any(p in tokens for p in ["psu", "powersupply"]) or ("power" in tokens and "supply" in tokens):
        return "psu"

    if any(mon in tokens for mon in ["monitor", "monitors"]):
        return "monitor"

    return None


def is_strictly_relevant(title: str, query: str) -> bool:
    """
    Check if a scraped product title is genuinely relevant to the user's query,
    filtering out unrelated category leaks, power supplies, skins, and monitors.
    """
    t_lower = title.lower()
    q_lower = query.lower()
    
    # Extract meaningful tokens (length > 1, ignoring basic stop words)
    q_tokens = [w for w in re.findall(r"[a-z0-9]+", q_lower) if w not in {"the", "and", "for", "with", "in", "of", "to"}]
    if not q_tokens:
        return True

    category = detect_intended_category(query)

    # 1. If searching for CPU/Processor:
    if category == "cpu":
        # Discard clear non-CPU products unless explicitly queried
        unrelated_cpu_terms = [
            "monitor", "power supply", "psu", "casing", "skin", "screen protector",
            "bluetooth adapter", "mouse", "keyboard", "headset", "speaker", "toner",
            "ups battery", "thermal paste", "charger", "cable"
        ]
        if any(bad in t_lower for bad in unrelated_cpu_terms):
            return False

        # If user searched "Ryzen", discard products that do not mention "ryzen" in title
        if "ryzen" in q_tokens and "ryzen" not in t_lower:
            return False

        # If user searched specific model like "5600" or "7600" or "13700", title must contain that number
        for tok in q_tokens:
            if tok.isdigit() and len(tok) >= 4:
                # Must appear as standalone model number (e.g. 5600, 5600x, 5600gt)
                if not re.search(rf"\b{tok}[a-z]*\b", t_lower):
                    return False

        # If user searched for general CPU or processor:
        if q_lower in ["cpu", "processor", "processors"]:
            cpu_identifiers = ["processor", "cpu", "ryzen", "core i3", "core i5", "core i7", "core i9", "ultra 5", "ultra 7", "ultra 9", "pentium", "athlon", "xeon"]
            if not any(ident in t_lower for ident in cpu_identifiers):
                return False

    # 2. If searching for GPU:
    elif category == "gpu":
        unrelated_gpu_terms = ["headset", "mouse", "keyboard", "skin", "toner", "cable", "monitor"]
        if any(bad in t_lower for bad in unrelated_gpu_terms) and not any(bad in q_lower for bad in unrelated_gpu_terms):
            return False
        # Must match specific GPU tier if specified (e.g. 5060, 4060, 3060, 6600)
        for tok in q_tokens:
            if tok.isdigit() and len(tok) >= 4:
                if not re.search(rf"\b{tok}\b", t_lower):
                    return False

    # 3. If searching for RAM:
    elif category == "ram":
        if not any(r in t_lower for r in ["ram", "ddr4", "ddr5", "ddr3", "memory", "dimm"]):
            return False
        unrelated_ram_terms = ["motherboard", "casing", "psu", "power supply", "monitor", "headset"]
        if any(bad in t_lower for bad in unrelated_ram_terms) and not any(bad in q_lower for bad in unrelated_ram_terms):
            return False

    # 4. General match rule: at least one key identifier must match
    # For queries like "Ryzen 5 5600" or "RTX 3060 12GB"
    key_terms = [t for t in q_tokens if len(t) >= 3 or t.isdigit()]
    if key_terms:
        # At least half of the key query terms should be present in title
        matches = sum(1 for term in key_terms if term in t_lower)
        if matches == 0:
            return False

    return True
