from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
import os
import random
import string
from supabase import create_client, Client

app = FastAPI()


SUPABASE_URL = "https://zvylvgutldakkllihibb.supabase.co"
SUPABASE_KEY = ""

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.post("/shorten")
async def shorten(request: Request, url: str = Query(...)):
    charset = string.ascii_letters + string.digits
    
    # Generate a unique 6-character code
    while True:
        code = "".join(random.choices(charset, k=6))
        exists_resp = (
            supabase.table("urls")
            .select("short_code")
            .eq("short_code", code)
            .limit(1)
            .execute()
        )

        # If data is empty, the code is unique
        if not exists_resp.data:
            break

    try:
        # Attempt to insert into the database (match DB schema)
        supabase.table("urls").insert(
            {
                "short_code": code,
                "long_url": url,
            }
        ).execute()
    except Exception as e:
        # Catch exceptions rather than checking for an .error attribute
        raise HTTPException(status_code=500, detail=f"ไม่สามารถบันทึกข้อมูลได้: {str(e)}")

    short_url = str(request.base_url) + code
    return {"code": code, "short_url": short_url}


@app.get("/{code}")
async def redirect(code: str):
    try:
        # Use .maybe_single() so it doesn't crash if the code isn't found
        resp = (
            supabase.table("urls")
            .select("long_url")
            .eq("short_code", code)
            .maybe_single()
            .execute()
        )
        
        # Check if data returned is empty/None
        if not resp.data:
            raise HTTPException(status_code=404, detail="ไม่พบโค้ดนี้")

        destination_url = resp.data["long_url"]
        return RedirectResponse(url=destination_url, status_code=307)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดในการดึงข้อมูล")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)