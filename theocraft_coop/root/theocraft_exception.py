from fastapi import HTTPException, status


class TheocraftNotFoundException(HTTPException):

    def __init__(self, message=None, headers=None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=message, headers=headers
        )


class TheocraftBadRequestException(HTTPException):

    def __init__(self, message=None, headers=None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message, headers=headers
        )


class TheocraftReqPayloadException(HTTPException):

    def __init__(self, message=None, headers=None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
            headers=headers,
        )


class TheocraftPermissionException(HTTPException):
    def __init__(self, message=None, headers=None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            headers=headers,
        )


class TheocraftAuthException(HTTPException):
    def __init__(self, message=None, headers=None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers=headers,
        )
