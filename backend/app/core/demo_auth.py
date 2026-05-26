from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import html
import json
import secrets
import time
from urllib.parse import parse_qs, quote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from app.core.config import settings

LOCAL_ENVS = {"local", "dev", "development", "test"}


def add_demo_auth(app: FastAPI) -> None:
    @app.middleware("http")
    async def demo_auth_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        if not settings.DEMO_AUTH_ENABLED or is_public_path(request.url.path):
            return await call_next(request)

        if is_valid_session(request):
            return await call_next(request)

        if is_api_path(request.url.path):
            return JSONResponse(
                {"detail": "Authentication required."},
                status_code=401,
            )

        next_path = sanitize_next_path(
            request.url.path + (f"?{request.url.query}" if request.url.query else "")
        )
        return RedirectResponse(
            url=f"/login?next={quote(next_path, safe='/?:=&')}",
            status_code=303,
        )

    @app.get("/login", response_class=HTMLResponse, include_in_schema=False)
    async def login_page(request: Request) -> Response:
        if not settings.DEMO_AUTH_ENABLED:
            return RedirectResponse(url="/projects", status_code=303)

        if is_valid_session(request):
            return RedirectResponse(
                url=sanitize_next_path(request.query_params.get("next")),
                status_code=303,
            )

        return HTMLResponse(
            build_login_page(next_path=sanitize_next_path(request.query_params.get("next")))
        )

    @app.post("/login", response_class=HTMLResponse, include_in_schema=False)
    async def login(request: Request) -> Response:
        if not settings.DEMO_AUTH_ENABLED:
            return RedirectResponse(url="/projects", status_code=303)

        form = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
        username = first_form_value(form, "username")
        password = first_form_value(form, "password")
        next_path = sanitize_next_path(first_form_value(form, "next") or "/projects")

        if not is_auth_configured():
            return HTMLResponse(
                build_login_page(
                    error="Demo-auth не настроен. Проверьте переменные окружения.",
                    next_path=next_path,
                ),
                status_code=500,
            )

        if not credentials_match(username, password):
            return HTMLResponse(
                build_login_page(error="Неверный логин или пароль.", next_path=next_path),
                status_code=401,
            )

        response = RedirectResponse(url=next_path, status_code=303)
        set_session_cookie(response, create_session_token(username))
        return response

    @app.post("/logout", include_in_schema=False)
    async def logout() -> Response:
        response = RedirectResponse(url="/login", status_code=303)
        clear_session_cookie(response)
        return response

    @app.get("/logout", include_in_schema=False)
    async def logout_get() -> Response:
        response = RedirectResponse(url="/login", status_code=303)
        clear_session_cookie(response)
        return response


def is_public_path(path: str) -> bool:
    return (
        path == "/login"
        or path == "/logout"
        or path == f"{settings.API_V1_PREFIX}/health"
        or path == "/favicon.ico"
        or path.startswith("/assets/")
    )


def is_api_path(path: str) -> bool:
    return path.startswith(settings.API_V1_PREFIX) or path == "/openapi.json"


def is_valid_session(request: Request) -> bool:
    return get_session_username(request) is not None


def get_session_username(request: Request) -> str | None:
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token or not is_auth_configured():
        return None

    try:
        payload_part, signature = token.split(".", 1)
    except ValueError:
        return None

    expected_signature = sign_value(payload_part)
    if not secrets.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(base64url_decode(payload_part))
        expires_at = int(payload.get("exp", 0))
    except (binascii.Error, UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError):
        return None

    username = str(payload.get("sub", ""))
    if not secrets.compare_digest(username, settings.DEMO_AUTH_USERNAME):
        return None

    if expires_at < int(time.time()):
        return None

    return username


def create_session_token(username: str) -> str:
    now = int(time.time())
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + settings.SESSION_TTL_SECONDS,
    }
    payload_part = base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    return f"{payload_part}.{sign_value(payload_part)}"


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        secure=use_secure_cookie(),
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=use_secure_cookie(),
        path="/",
    )


def credentials_match(username: str, password: str) -> bool:
    return secrets.compare_digest(
        username, settings.DEMO_AUTH_USERNAME
    ) and secrets.compare_digest(password, settings.DEMO_AUTH_PASSWORD)


def is_auth_configured() -> bool:
    return bool(
        settings.DEMO_AUTH_USERNAME
        and settings.DEMO_AUTH_PASSWORD
        and settings.SECRET_KEY
        and settings.SESSION_COOKIE_NAME
        and settings.SESSION_TTL_SECONDS > 0
    )


def sign_value(value: str) -> str:
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64url_encode(digest)


def base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def base64url_decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}").decode("utf-8")


def use_secure_cookie() -> bool:
    return settings.ENV.strip().lower() not in LOCAL_ENVS


def first_form_value(form: dict[str, list[str]], name: str) -> str:
    values = form.get(name)
    return values[0] if values else ""


def sanitize_next_path(value: str | None) -> str:
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/projects"

    if value in {"/login", "/logout"}:
        return "/projects"

    return value


def build_login_page(error: str = "", next_path: str = "/projects") -> str:
    safe_error = html.escape(error)
    safe_next = html.escape(sanitize_next_path(next_path), quote=True)
    error_block = (
        f'<div class="error" role="alert">{safe_error}</div>' if safe_error else ""
    )

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>OPEN Project Risk - вход</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: Inter, Segoe UI, Arial, sans-serif;
        background: #f3f6f9;
        color: #0f172a;
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: 24px;
      }}
      main {{
        width: min(420px, 100%);
        border: 1px solid #dbe3ee;
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
        padding: 28px;
      }}
      .brand {{
        color: #64748b;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}
      h1 {{
        margin: 10px 0 6px;
        font-size: 26px;
        line-height: 1.2;
      }}
      p {{
        margin: 0 0 22px;
        color: #64748b;
        font-size: 14px;
        line-height: 1.6;
      }}
      label {{
        display: block;
        margin-top: 14px;
        color: #334155;
        font-size: 13px;
        font-weight: 700;
      }}
      input {{
        box-sizing: border-box;
        width: 100%;
        margin-top: 7px;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 12px 13px;
        font: inherit;
        outline: none;
      }}
      input:focus {{
        border-color: #0f172a;
        box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.08);
      }}
      button {{
        width: 100%;
        margin-top: 22px;
        border: 0;
        border-radius: 10px;
        background: #020617;
        color: #fff;
        padding: 12px 14px;
        font: inherit;
        font-weight: 700;
        cursor: pointer;
      }}
      .error {{
        margin: 18px 0 0;
        border: 1px solid #fecdd3;
        border-radius: 10px;
        background: #fff1f2;
        color: #be123c;
        padding: 11px 12px;
        font-size: 14px;
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="brand">OPEN Project Risk</div>
      <h1>Вход в OPEN Project Risk</h1>
      <p>Введите demo-доступ для просмотра клиентской карты проекта.</p>
      <form method="post" action="/login" autocomplete="on">
        <input type="hidden" name="next" value="{safe_next}" />
        <label for="username">Логин</label>
        <input id="username" name="username" autocomplete="username" required />
        <label for="password">Пароль</label>
        <input id="password" name="password" type="password" autocomplete="current-password" required />
        {error_block}
        <button type="submit">Войти</button>
      </form>
    </main>
  </body>
</html>"""
