from functools import wraps

import requests
import discord
from discord.ext import commands
from flask import (Flask, render_template_string, request, redirect,
                   url_for, session, abort, g)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ------------------------------------------------------------------
# Config (সব সিক্রেট এনভায়রনমেন্ট ভেরিয়েবল থেকে আসবে)
# ------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

DB_FILE = os.environ.get("DB_FILE", "iss.db")
OWNER_EMAIL = os.environ["OWNER_EMAIL"]
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "owner")
OWNER_PASSWORD = os.environ["OWNER_PASSWORD"]