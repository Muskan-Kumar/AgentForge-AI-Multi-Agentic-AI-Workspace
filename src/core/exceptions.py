class AgentForgeException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AgentForgeException):
    def __init__(
        self,
        message: str = "Authentication failed",
    ):
        super().__init__(
            message=message,
            status_code=401,
        )


class ResourceNotFoundError(AgentForgeException):
    def __init__(
        self,
        message: str = "Resource not found",
    ):
        super().__init__(
            message=message,
            status_code=404,
        )


class AgentExecutionError(AgentForgeException):
    def __init__(
        self,
        message: str = "Agent execution failed",
    ):
        super().__init__(
            message=message,
            status_code=500,
        )
        