from fastapi import HTTPException


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Authenticaton failed. please log in!"):
        super().__init__(status_code=401, detail=detail)
