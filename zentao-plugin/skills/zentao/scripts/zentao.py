"""ZenTao REST v1 client.

Minimal dependency: only `requests` from stdlib-adjacent. PyYAML optional
(falls back to JSON config).

Usage:
    from zentao import Client
    c = Client.from_config()
    c.get('/products')
    c.post('/bugs/1', json={'title': ...})

Auth: POST /api.php/v1/tokens returns {token} which is the PHP session id.
Subsequent calls send it in the `Token` header. Cached to disk so CLI calls
don't re-login every time.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import urllib.request
import urllib.parse
import urllib.error
import ssl


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except ImportError:
        text = path.read_text(encoding='utf-8')
        return _tiny_yaml(text)


def _tiny_yaml(text: str) -> dict:
    """Parse a *very* restricted YAML subset: `key: value` lines, `#` comments.
    Good enough for our config file. Falls back if PyYAML is missing.
    """
    out: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].rstrip()
        if not line.strip() or ':' not in line:
            continue
        if line[0] in (' ', '\t'):
            continue  # no nested maps in our config
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


class ZentaoError(RuntimeError):
    def __init__(self, status: int, message: str, payload: Any = None):
        super().__init__(f'HTTP {status}: {message}')
        self.status = status
        self.message = message
        self.payload = payload


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
        self.account = account
        self.password = password
        self.token_cache = token_cache or _default_cache_path()
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.defaults = defaults or {}
        self._token: str | None = None

    # ---------- construction ----------

    @classmethod
    def from_config(cls, path: Path | None = None) -> 'Client':
        path = path or _default_config_path()
        if not path.exists():
            raise SystemExit(
                f'Missing config: {path}\n'
                f'Copy {path.parent / "config.example.yaml"} and fill in your credentials.'
            )
        cfg = _load_yaml(path)
        required = ('url', 'account', 'password')
        missing = [k for k in required if not cfg.get(k)]
        if missing:
            raise SystemExit(f'Config {path} missing required keys: {", ".join(missing)}')
        defaults = {k: cfg[k] for k in ('default_product', 'default_project', 'default_execution') if k in cfg}
        tok = cfg.get('token_cache')
        return cls(
            url=cfg['url'],
            account=cfg['account'],
            password=str(cfg['password']),
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
                'exp': time.time() + 60 * 60 * 2,  # 2h cache; session can live longer
            }),
            encoding='utf-8',
        )

    def login(self, force: bool = False) -> str:
        if not force:
            cached = self._load_cached_token()
            if cached:
                self._token = cached
                return cached
        resp = self._raw_request(
            'POST', '/tokens',
            body=json.dumps({'account': self.account, 'password': self.password}).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            authed=False,
        )
        token = resp.get('token') if isinstance(resp, dict) else None
        if not token:
            raise ZentaoError(401, f'Login failed: {resp}')
        self._token = token
        self._save_token(token)
        return token

    def token(self) -> str:
        return self._token or self.login()

    # ---------- core HTTP ----------

    def _raw_request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: bytes | None = None,
        headers: dict | None = None,
        authed: bool = True,
    ) -> Any:
        qs = ''
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                qs = '?' + urllib.parse.urlencode(clean, doseq=True)
        url = f'{self.url}/api.php/v1{path}{qs}'
        hdrs = {
            'Accept': 'application/json',
            'User-Agent': 'claude-zentao-skill/1.0',
        }
        if headers:
            hdrs.update(headers)
        if authed:
            hdrs['Token'] = self.token()

        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        ctx = None if self.verify_ssl else ssl._create_unverified_context()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                status = resp.status
                raw = resp.read()
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read() or b''
        except urllib.error.URLError as e:
            raise ZentaoError(0, f'Network error: {e.reason}')

        text = raw.decode('utf-8', errors='replace')
        try:
            data = json.loads(text) if text else None
        except json.JSONDecodeError:
            data = {'_raw': text}

        if status == 401 and authed:
            # token expired; retry once with fresh login
            self.login(force=True)
            hdrs['Token'] = self._token
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                status = resp.status
                raw = resp.read()
            try:
                data = json.loads(raw.decode('utf-8'))
            except json.JSONDecodeError:
                data = {'_raw': raw.decode('utf-8', errors='replace')}

        if status >= 400:
            msg = data.get('error') if isinstance(data, dict) else str(data)
            raise ZentaoError(status, str(msg or text[:200]), payload=data)
        return data

    # ---------- public helpers ----------

    def get(self, path: str, **params) -> Any:
        return self._raw_request('GET', path, params=params)

    def post(self, path: str, json_body: Any = None, **params) -> Any:
        body = json.dumps(json_body).encode('utf-8') if json_body is not None else None
        return self._raw_request(
            'POST', path,
            params=params,
            body=body,
            headers={'Content-Type': 'application/json'} if body else None,
        )

    def put(self, path: str, json_body: Any = None, **params) -> Any:
        body = json.dumps(json_body or {}).encode('utf-8')
        return self._raw_request(
            'PUT', path,
            params=params,
            body=body,
            headers={'Content-Type': 'application/json'},
        )

    def delete(self, path: str, **params) -> Any:
        return self._raw_request('DELETE', path, params=params)


if __name__ == '__main__':
    c = Client.from_config()
    c.login()
    print(json.dumps({'ok': True, 'token_prefix': c.token()[:8] + '...'}))
