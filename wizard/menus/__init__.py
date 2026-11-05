"""Domain-first Wizard registry. P-stage identifiers remain stable CLI aliases.

Stage numbers describe roadmap/acceptance order; users navigate by functional
group and model/transition names instead of having to remember P1/P2/etc.
"""
from __future__ import annotations

from .models import flash_next, qwen_27b, orcarouter_flash_next
from .switching import flash_next_27b, orcarouter_27b
from .storage import flash_next_cleanup
from .operations import system

HANDLERS = {
    "p1": flash_next,
    "p2": qwen_27b,
    "p3": flash_next_27b,
    "p4": flash_next_cleanup,
    "p5": orcarouter_flash_next,
    "p6": orcarouter_27b,
    "p7": system,
}

# Canonical human-readable selection keys and CLI names; order matters.
GROUPS = {
    "model": {
        "flash-next": "p1",
        "27b": "p2",
        "orcarouter-flash-next": "p5",
    },
    "switch": {
        "flash-next-27b": "p3",
        "orcarouter-27b": "p6",
    },
    "storage": {"flash-next": "p4"},
    "operations": {"system": "p7"},
}

GROUP_TITLES = {
    "model": "Model management / 설치·기동·검증·벤치",
    "switch": "Model switching / 전환·원복",
    "storage": "Storage management / 용량·선택적 정리",
    "operations": "System operations / 서비스·프록시·게이트웨이",
}

GROUP_ALIASES = {
    "models": "model",
    "switching": "switch",
    "operation": "operations",
}

STAGE_LOCATIONS = {
    stage: (group, selection)
    for group, options in GROUPS.items()
    for selection, stage in options.items()
}
