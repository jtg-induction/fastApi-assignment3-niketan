from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.user import router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []

    for error in exc.errors():
        field_name = error["loc"][-1] if error["loc"] else "body"

        message = error["msg"]
        if error["type"] == "missing":
            message = f"The '{field_name}' field is required."

        formatted_errors.append(
            {
                "field": field_name,
                "location": error["loc"][0] if len(error["loc"]) > 0 else "body",
                "message": message,
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "errors": formatted_errors},
    )


app.include_router(router)


@app.get("/")
def root():
    return {"message": f"hlo fast API and id"}
