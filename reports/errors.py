class ReportsError(Exception):
    """Parent class for app-specific exceptions."""


class AttachmentError(ReportsError):
    """Attachment size and type errors."""


class AlreadyExistsError(ReportsError):
    """Raise if a time entry report has already been saved."""
