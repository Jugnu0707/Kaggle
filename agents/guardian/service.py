"""Guardian Agent service entry point."""

from __future__ import annotations

from agents.guardian.schemas import GuardianValidateInput, GuardianValidationResult
from agents.guardian.validator import GuardianValidator


class GuardianService:
    """Validates AI agent outputs through the Guardian pipeline."""

    def __init__(self) -> None:
        self.validator = GuardianValidator()

    def validate(self, request: GuardianValidateInput) -> GuardianValidationResult:
        """Validate an agent response."""
        return self.validator.validate(request)
