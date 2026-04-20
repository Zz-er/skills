"""ZenTao legacy `.json` client (session-cookie auth).

Works against open-source ZenTao instances that respond to `/<entry>.json`
URLs (any version with the web UI; no REST v1 required).

Flow:
    POST /user-login.json   (form-urlencoded)
      -> { status, user: { token, ... } }
    GET  /<entry>.json      (Cookie: zentaosid=<token>)
      -> { status, data: <dict|string>, md5 }
    If `data` is a string, it's a nested JSON blob — parse again.

Collections (`projects`, `bugs`, `users`) may be either a **list** or an
**object keyed by id**, depending on entry + ZenTao version; use
`as_list()` to normalize.

Usage:
    from zentao import Client
    c = Client.from_config()
    data = c.get_json('my-project')         # dict
    bugs, users = c.get_bugs(project_id=790)

Token is cached at ~/.claude/.cache/zentao_token.json and auto-refreshed
if the next call redirects to login.
"""
from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


# ---------- config / cache paths ----------

def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except ImportError:
        return _tiny_yaml(path.read_text(encoding='utf-8'))


def _tiny_yaml(text: str) -> dict:
    out: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].rstrip()
        if not line.strip() or ':' not in line or line[0] in (' ', '\t'):
            continue
        k, _, v = line.partition(':')
        v = v.strip()
        if v.lower() in ('true', 'false'):
            out[k.strip()] = (v.lower() == 'true')
        elif v.isdigit():
            out[k.strip()] = int(v)
        elif v.startswith(('"', "'")) and v.endswith(v[0]):
            out[k.strip()] = v[1:-1]
        else:
            out[k.strip()] = v
    return out


def _default_config_path() -> Path:
    env = os.environ.get('ZENTAO_CONFIG')
    if env:
        return Path(os.path.expanduser(env))
    user_path = Path.home() / '.claude' / 'zentao' / 'config.yaml'
    if user_path.exists():
        return user_path
    return Path(__file__).resolve().parent.parent / 'config.yaml'


def _default_cache_path() -> Path:
    return Path.home() / '.claude' / '.cache' / 'zentao_token.json'


# ---------- errors ----------

class ZentaoError(RuntimeError):
    def __init__(self, status: int, message: str, payload: Any = None):
        super().__init__(f'HTTP {status}: {message}')
        self.status = status
        self.message = message
        self.payload = payload


# ---------- helpers ----------

def as_list(coll: Any) -> list:
    """Normalize a collection that may be list, dict-by-id, or None → list."""
    if coll is None:
        return []
    if isinstance(coll, list):
        return coll
    if isinstance(coll, dict):
        return list(coll.values())
    return [coll]


_HTML_IMG_RE = re.compile(r'\{[^}]+\}')
_HTML_BR_RE = re.compile(r'<br\s*/?>', re.I)
_HTML_TAG_RE = re.compile(r'<[^>]+>')


def clean_html(s: str | None) -> str:
    """Strip ZenTao rich-text (HTML + {image.png} placeholders) to plain text."""
    if not s:
        return ''
    s = _HTML_BR_RE.sub('\n', s)
    s = _HTML_TAG_RE.sub('', s)
    s = _HTML_IMG_RE.sub('[图片]', s)
    return s.strip()


# ---------- client ----------

class Client:
    def __init__(
        self,
        url: str,
        account: str,
        password: str,
        *,
        token_cache: Path | None = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        defaults: dict | None = None,
    ) -> None:
        self.url = url.rstrip('/')
        # ZenTao stores account as a string server-side. Coerce defensively here
        # because YAML parsers (both PyYAML and our _tiny_yaml) turn numeric-
        # looking account names like `4224` into ints, which then fails to
        # compare against the string `assignedTo` field on bug records.
        self.account = str(account)
        self.password = str(password)
        self.token_cache = token_cache or _default_cache_path()
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.defaults = defaults or {}
        self._token: str | None = None

    @classmethod
    def from_config(cls, path: Path | None = None) -> 'Client':
        path = path or _default_config_path()
        if not path.exists():
            raise SystemExit(
                f'Missing config: {path}\n'
                f'Copy {path.parent / "config.example.yaml"} and fill in your credentials.'
            )
        cfg = _load_yaml(path)
        missing = [k for k in ('url', 'account', 'password') if not cfg.get(k)]
        if missing:
            raise SystemExit(f'Config {path} missing required keys: {", ".join(missing)}')
        defaults = {k: cfg[k] for k in ('default_project', 'default_product', 'default_execution') if k in cfg}
        tok = cfg.get('token_cache')
        return cls(
            url=cfg['url'],
            account=cfg['account'],
            password=cfg['password'],
            token_cache=Path(os.path.expanduser(tok)) if tok else None,
            timeout=int(cfg.get('timeout', 30)),
            verify_ssl=bool(cfg.get('verify_ssl', True)),
            defaults=defaults,
        )

    # ---------- auth ----------

    def _load_cached_token(self) -> str | None:
        try:
            data = json.loads(self.token_cache.read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        if data.get('url') != self.url or data.get('account') != self.account:
            return None
        if data.get('exp', 0) < time.time():
            return None
        return data.get('token')

    def _save_token(self, token: str) -> None:
        self.token_cache.parent.mkdir(parents=True, exist_ok=True)
        self.token_cache.write_text(
            json.dumps({
                'url': self.url,
                'account': self.account,
                'token': token,
                'exp': time.time() + 60 * 60 * 2,
            }),
            encoding='utf-8',
        )

    def login(self, force: bool = False) -> str:
        if not force:
            cached = self._load_cached_token()
            if cached:
                self._token = cached
                return cached
        body = urllib.parse.urlencode({
            'account': self.account,
            'password': self.password,
        }).encode('utf-8')
        req = urllib.request.Request(
            f'{self.url}/user-login.json',
            data=body,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'User-Agent': 'claude-zentao-skill/2.0',
            },
            method='POST',
        )
        ctx = None if self.verify_ssl else ssl._create_unverified_context()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                raw = resp.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            raw = (e.read() or b'').decode('utf-8', errors='replace')
            raise ZentaoError(e.code, f'Login HTTP {e.code}: {raw[:200]}')
        except urllib.error.URLError as e:
            raise ZentaoError(0, f'Network error: {e.reason}')
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ZentaoError(0, f'Login returned non-JSON: {raw[:200]}')
        if data.get('status') != 'success' or not data.get('user', {}).get('token'):
            reason = data.get('reason') or data.get('message') or data
            raise ZentaoError(401, f'Login failed: {reason}')
        token = data['user']['token']
        self._token = token
        self._save_token(token)
        return token

    def token(self) -> str:
        return self._token or self.login()

    def whoami(self) -> dict:
        """Force re-login and return user profile dict."""
        body = urllib.parse.urlencode({
            'account': self.account,
            'password': self.password,
        }).encode('utf-8')
        req = urllib.request.Request(
            f'{self.url}/user-login.json',
            data=body,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
        )
        ctx = None if self.verify_ssl else ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('status') != 'success':
            raise ZentaoError(401, f'Login failed: {data}')
        user = data.get('user', {})
        self._token = user.get('token')
        if self._token:
            self._save_token(self._token)
        return user

    # ---------- core HTTP ----------

    def _raw_get(self, entry: str, cookies: dict | None = None) -> dict:
        """GET /<entry>.json with auth; return outer response dict."""
        path = entry if entry.endswith('.json') else f'{entry}.json'
        if not path.startswith('/'):
            path = '/' + path
        url = f'{self.url}{path}'
        cookie_parts = [f'zentaosid={self.token()}']
        for k, v in (cookies or {}).items():
            cookie_parts.append(f'{k}={v}')
        req = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'claude-zentao-skill/2.0',
            'Cookie': '; '.join(cookie_parts),
        })
        ctx = None if self.verify_ssl else ssl._create_unverified_context()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                raw = resp.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            raw = (e.read() or b'').decode('utf-8', errors='replace')
            raise ZentaoError(e.code, f'HTTP {e.code} on {path}: {raw[:200]}')
        except urllib.error.URLError as e:
            raise ZentaoError(0, f'Network error: {e.reason}')
        try:
            outer = json.loads(raw)
        except json.JSONDecodeError:
            raise ZentaoError(0, f'Non-JSON response on {path}: {raw[:200]}')
        return outer

    def get_json(self, entry: str, cookies: dict | None = None) -> dict:
        """Fetch an entry and return the unwrapped inner dict.

        Handles ZenTao's outer `{status, data, md5}` envelope plus the
        common case where `data` is itself a JSON string. Auto-retries
        once if the server replies with a login-redirect locate.
        """
        outer = self._raw_get(entry, cookies=cookies)
        inner = self._unwrap(outer)
        if self._is_login_redirect(inner):
            # session expired — refresh and retry once
            self.login(force=True)
            outer = self._raw_get(entry, cookies=cookies)
            inner = self._unwrap(outer)
            if self._is_login_redirect(inner):
                raise ZentaoError(401, f'Session rejected after re-login on {entry}')
        return inner

    @staticmethod
    def _unwrap(outer: dict) -> dict:
        data = outer.get('data') if isinstance(outer, dict) else outer
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return {'_raw': data}
        return data if isinstance(data, dict) else {'value': data}

    @staticmethod
    def _is_login_redirect(inner: dict) -> bool:
        locate = inner.get('locate') if isinstance(inner, dict) else None
        return bool(locate and 'user-login' in str(locate))

    # ---------- high-level helpers ----------

    def get_projects(self, include_closed: bool = False) -> list[dict]:
        inner = self.get_json('my-project')
        projects = as_list(inner.get('projects'))
        if not include_closed:
            projects = [p for p in projects if p.get('status') != 'closed']
        return projects

    def get_bugs(
        self,
        project_id: int | str,
        *,
        page_size: int = 1000,
    ) -> tuple[list[dict], dict[str, str]]:
        inner = self.get_json(
            f'project-bug-{project_id}',
            cookies={'pagerProjectBug': str(page_size)},
        )
        bugs = as_list(inner.get('bugs'))
        users = inner.get('users') or {}
        return bugs, users

    def get_my_bugs(self, *, page_size: int = 500) -> tuple[list[dict], dict[str, str]]:
        """Bugs assigned to the current account — server-filtered."""
        inner = self.get_json('my-bug', cookies={'pagerMyBug': str(page_size)})
        bugs = as_list(inner.get('bugs'))
        users = inner.get('users') or {}
        return bugs, users


if __name__ == '__main__':
    c = Client.from_config()
    c.login(force=True)
    print(json.dumps({'ok': True, 'token_prefix': c.token()[:8] + '...'}))
