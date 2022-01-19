#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from app.routers.adding import add_device
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import fetch, update, adding, device_list

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fetch.router)
app.include_router(update.router)
app.include_router(adding.router)
app.include_router(device_list.router)
