import types

from fastapi.testclient import TestClient

import main


class _FakeQueryResult:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error


class _FakeQuery:
    def __init__(self, table_name: str, store: dict):
        self._table_name = table_name
        self._store = store
        self._code = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, _column: str, value: str):
        # จำค่า code ไว้สำหรับ maybe_single/single
        self._code = value
        return self

    def maybe_single(self):
        return self

    def single(self):
        return self

    def execute(self):
        if self._table_name == "urls":
            if self._code is None:
                return _FakeQueryResult(data=None, error=None)
            url = self._store.get(self._code)
            if url is None:
                return _FakeQueryResult(data=None, error=None)
            return _FakeQueryResult(data={"code": self._code, "url": url}, error=None)
        return _FakeQueryResult(data=None, error=None)


class _FakeTable:
    def __init__(self, name: str, store: dict):
        self._name = name
        self._store = store
        self._pending = None

    def select(self, *args, **kwargs):
        return _FakeQuery(self._name, self._store).select(*args, **kwargs)

    def eq(self, column: str, value: str):
        # ไม่ได้ใช้ path นี้ในโค้ดจริง (เราใช้ผ่าน _FakeQuery แทน)
        return self

    def maybe_single(self):
        return self

    def single(self):
        return self

    def execute(self):
        return _FakeQueryResult(data=None, error=None)

    def insert(self, row: dict):
        # เก็บ pending row แล้วให้ execute() มา commit
        self._pending = row
        return types.SimpleNamespace(execute=self._do_insert)

    def _do_insert(self):
        code = self._pending["code"]
        url = self._pending["url"]
        self._store[code] = url
        return _FakeQueryResult(data=self._pending, error=None)


class _FakeSupabase:
    def __init__(self):
        # ใช้ dict ง่าย ๆ จำลอง table urls
        self._urls = {}

    def table(self, name: str):
        return _FakeTable(name, self._urls)


def test_shorten_and_redirect(monkeypatch):
    # แทนที่ supabase จริงด้วยของปลอม
    fake = _FakeSupabase()
    monkeypatch.setattr(main, "supabase", fake)

    client = TestClient(main.app)

    # เรียก /shorten
    target_url = "https://example.com"
    response = client.post("/shorten", params={"url": target_url})

    assert response.status_code == 200
    body = response.json()
    assert "code" in body
    assert "short_url" in body

    code = body["code"]

    # ตรวจ redirect ด้วย code ที่ได้
    redirect_resp = client.get(f"/{code}", allow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers["location"] == target_url

