# core/exceptions.py


class PolarisError(Exception):
    """Base exception for PolarisIQ."""

    pass


class PlanValidationError(PolarisError):
    """Raised when query plan fails validation."""

    pass


class ExecutionError(PolarisError):
    """Raised when execution engine fails."""

    pass


class ToolExecutionError(PolarisError):
    """Raised when a tool invocation fails."""

    pass


class LLMOutputError(PolarisError):
    """Raised when LLM output is malformed."""

    pass
