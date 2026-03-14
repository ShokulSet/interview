from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import os

app = FastAPI()

# โจทย์ 1: เชื่อมต่อ Supabase (ให้เขาเติมแค่บรรทัดเดียว)
# TODO: supabase = create_client(url, key)

@app.post("/shorten")
async def shorten(url: str):
    # โจทย์ 2: รับ URL มาแล้ว Generate code เก็บลง DB
    # (Hint: ให้เขาใช้ LLM ช่วยคิด Logic สั้นๆ ได้เลย)
    pass

@app.get("/{code}")
async def redirect(code: str):
    # โจทย์ 3: ดึงข้อมูลจาก DB แล้ว Redirect
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)