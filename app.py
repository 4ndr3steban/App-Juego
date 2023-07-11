from fastapi import FastAPI
import os
from settings import settings
from routers import router_user, router_products, router_challenge

app = FastAPI()

# API para usuarios
app.include_router(router_user.router)

# API para productos
app.include_router(router_products.router)

# API para challenge
app.include_router(router_challenge.router)
