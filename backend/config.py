# backend/config.py
import os

DEEP_DEBUG = os.getenv("DEEP_DEBUG", "false").lower() == "true"

DEBUG = os.getenv("DEBUG", "false").lower() == "true"