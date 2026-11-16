"""Side-effect-free foundation for synthetic agent worlds.

This module is additive: the existing eight-case store baseline is unchanged.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

EVALUATOR_VERSION = "0.1.0"


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TrustedContext:
    actor_id: str
    role: str
    resources: frozenset[str]
    permissions: frozenset[str]

    def permits(self, resource: str, action: str) -> bool:
        return resource in self.resources and action in self.permissions


@dataclass(frozen=True)
class Case:
    case_id: str
    version: str
    initial_state: dict[str, Any]
    expected_state: dict[str, Any]
    context: TrustedContext
    untrusted_input: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    case: Case
    model: str = "deterministic"
    provider: str = "local"
    state: dict[str, Any] = field(init=False)
    events: list[dict[str, Any]] = field(default_factory=list)
    attempts: list[dict[str, Any]] = field(default_factory=list)
    applied_changes: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.state = deepcopy(self.case.initial_state)

    def invoke(
        self,
        action: str,
        resource: str,
        arguments: dict[str, Any],
        handlers: dict[str, Callable[[dict[str, Any], str, dict[str, Any]], dict[str, Any]]],
    ) -> dict[str, Any]:
        """Dispatch only explicitly registered tools and trusted permissions.

        The caller cannot supply or override trusted authorization via arguments.
        """
        before = deepcopy(self.state)
        allowed = self.case.context.permits(resource, action) and action in handlers
        attempt = {"action": action, "resource": resource, "arguments": deepcopy(arguments),
                   "allowed": allowed}
        self.attempts.append(attempt)
        if not allowed:
            result = {"ok": False, "error": "action_not_permitted"}
        else:
            result = handlers[action](self.state, resource, deepcopy(arguments))
        after = deepcopy(self.state)
        if before != after:
            change = {"action": action, "resource": resource, "before": before, "after": after}
            self.applied_changes.append(change)
        self.events.append({
            "timestamp": timestamp(), "case_id": self.case.case_id,
            "case_version": self.case.version, "provider": self.provider, "model": self.model,
            "action": action, "resource": resource, "arguments": deepcopy(arguments),
            "result": deepcopy(result), "allowed": allowed, "state_changed": before != after,
        })
        return result

    def report(self) -> dict[str, Any]:
        return {
            "case_id": self.case.case_id, "case_version": self.case.version,
            "provider": self.provider, "model": self.model,
            "evaluator_version": EVALUATOR_VERSION, "timestamp": timestamp(),
            "actor_id": self.case.context.actor_id, "actor_role": self.case.context.role,
            "expected_state": deepcopy(self.case.expected_state),
            "actual_state": deepcopy(self.state),
            "state_matches_expected": self.state == self.case.expected_state,
            "attempted_actions": deepcopy(self.attempts),
            "applied_state_changes": deepcopy(self.applied_changes),
            "events": deepcopy(self.events),
        }
