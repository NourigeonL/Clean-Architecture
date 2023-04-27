from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import home
from starlette.requests import Request
from starlette.responses import Response
from traceback import print_exception

app = FastAPI()

app.include_router(home.router)