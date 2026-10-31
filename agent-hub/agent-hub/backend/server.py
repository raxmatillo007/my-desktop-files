import asyncio, os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from fastapi import FastAPI, WebSocket
import uvicorn
from hub import Hub

app = FastAPI()
hub = Hub()

@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()
    hub.clients.add(sock)
    await sock.send_json({"type": "agents", "agents": hub.agents})
    try:
        while True:
            d = await sock.receive_json()
            if d["type"] == "task":
                hub.stopped = False
                await hub.say("siz", "komandir", d["text"])
                async def go():
                    try: res = await hub.run("komandir", d["text"])
                    except Exception as e: res = f"Xato: {e}"
                    await hub.say("komandir", "siz", res)
                asyncio.create_task(go())
            elif d["type"] == "permission_reply":
                f = hub.pending.pop(d["id"], None)
                if f: f.set_result(bool(d["allow"]))
            elif d["type"] == "stop":
                hub.stopped = True
                for f in hub.pending.values(): f.set_result(False)
                hub.pending.clear()
    except Exception:
        hub.clients.discard(sock)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
