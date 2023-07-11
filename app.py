from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from settings import settings
from routers import router_user, router_products, router_challenge

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API para usuarios
app.include_router(router_user.router)

# API para productos
app.include_router(router_products.router)

# API para challenge
app.include_router(router_challenge.router)
