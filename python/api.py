import asyncio
import httpx
import datetime as dt
from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
async def ping():
    await asyncio.sleep(1)
    return f"Hello: {dt.datetime.now()}"


@app.get("/github")
async def get_github():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com")
        _ = response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text
        }


