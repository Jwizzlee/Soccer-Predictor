class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class InsufficientDataError(AppError):
    def __init__(self, message: str = "Insufficient match data for analysis"):
        super().__init__(message, status_code=400)


class ExternalAPIError(AppError):
    def __init__(self, message: str = "External sports API error", *, rate_limited: bool = False):
        self.rate_limited = rate_limited
        super().__init__(message, status_code=502)


class SportsAPIRateLimitError(ExternalAPIError):
    def __init__(
        self,
        message: str = (
            "Sports data is temporarily rate-limited. "
            "Please wait about a minute and try again with Last N set to 5 or fewer."
        ),
    ):
        super().__init__(message, rate_limited=True)


class LLMError(AppError):
    def __init__(self, message: str = "LLM service error"):
        super().__init__(message, status_code=502)


class SubscriptionRequiredError(AppError):
    def __init__(
        self,
        message: str = "Active subscription required. Please subscribe to continue.",
    ):
        super().__init__(message, status_code=402)
