"""Agentlar, xabar shinasi, ruxsat tizimi va vositalar."""
import asyncio, json, re, subprocess, uuid
from pathlib import Path
from router import chat

TOOLS_DOC = """Har javobingiz FAQAT bitta JSON obyekt bo'lsin:
{"action": "list_dir", "path": "..."}
{"action": "read_file", "path": "..."}
{"action": "write_file", "path": "...", "content": "..."}
{"action": "run_cmd", "cmd": "..."}
{"action": "finish", "result": "yakuniy javob"}"""
BOSS_DOC = """Qo'shimcha (faqat komandir):
{"action": "create_agent", "name": "...", "role": "..."}
{"action": "delegate", "agent": "...", "task": "..."}
Ishni ishchi agentlarga bo'lib bering, natijani yig'ib finish qiling."""

class Hub:
    def __init__(self):
        self.agents = {}          # name -> {"role", "boss"}
        self.clients = set()
        self.pending = {}         # permission id -> Future
        self.stopped = False
        self.add_agent("komandir", "Vazifani rejalashtiradi, ishchi agentlarni yaratadi va boshqaradi", True)
        self.add_agent("ishchi1", "Fayl va kod bilan ishlaydi", False)

    def add_agent(self, name, role, boss=False):
        self.agents[name] = {"role": role, "boss": boss}
        try:
            asyncio.get_running_loop().create_task(self.emit({"type": "agents", "agents": self.agents}))
        except RuntimeError:
            pass  # server hali ishga tushmagan, ulanganda yuboriladi

    async def emit(self, ev):
        for ws in list(self.clients):
            try: await ws.send_json(ev)
            except Exception: self.clients.discard(ws)

    async def say(self, frm, to, text):
        await self.emit({"type": "message", "from": frm, "to": to, "text": text})

    async def ask(self, agent, what):
        pid = str(uuid.uuid4())[:8]
        fut = asyncio.get_running_loop().create_future()
        self.pending[pid] = fut
        await self.emit({"type": "permission", "id": pid, "agent": agent, "action": what})
        return await fut

    async def tool(self, agent, a):
        act = a.get("action")
        try:
            if act == "list_dir":
                return "\n".join(p.name for p in Path(a["path"]).iterdir())[:3000]
            if act == "read_file":
                return Path(a["path"]).read_text(errors="ignore")[:6000]
            if act == "write_file":
                if not await self.ask(agent, f"Faylga yozish: {a['path']}"): return "Foydalanuvchi rad etdi"
                Path(a["path"]).write_text(a["content"]); return "Yozildi"
            if act == "run_cmd":
                if not await self.ask(agent, f"Buyruq: {a['cmd']}"): return "Foydalanuvchi rad etdi"
                p = subprocess.run(a["cmd"], shell=True, capture_output=True, text=True, timeout=60)
                return (p.stdout + p.stderr)[:4000]
            if agent == "komandir" and act == "create_agent":
                self.add_agent(a["name"], a["role"]); return "Agent yaratildi"
            if agent == "komandir" and act == "delegate":
                if a["agent"] not in self.agents: return "Bunday agent yo'q"
                await self.say(agent, a["agent"], a["task"])
                res = await self.run(a["agent"], a["task"])
                await self.say(a["agent"], agent, res)
                return res
        except Exception as e:
            return f"Xato: {e}"
        return "Noma'lum amal"

    async def run(self, name, task, max_steps=12):
        ag = self.agents[name]
        system = f"Sen '{name}' agentsan. Rolingiz: {ag['role']}. Windows kompyuterda ishlaysan.\n{TOOLS_DOC}"
        if ag["boss"]: system += "\n" + BOSS_DOC
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": task}]
        await self.emit({"type": "status", "agent": name, "state": "ishlayapti"})
        try:
            for _ in range(max_steps):
                if self.stopped: return "To'xtatildi"
                reply = await chat(msgs, lambda t: self.say("tizim", name, t))
                m = re.search(r"\{.*\}", reply, re.S)
                try: a = json.loads(m.group(0))
                except Exception:
                    msgs += [{"role": "assistant", "content": reply}, {"role": "user", "content": "Faqat JSON yuboring."}]
                    continue
                if a.get("action") == "finish": return str(a.get("result", ""))
                await self.say(name, "tizim", json.dumps(a, ensure_ascii=False)[:300])
                obs = await self.tool(name, a)
                msgs += [{"role": "assistant", "content": reply}, {"role": "user", "content": f"Natija:\n{obs}"}]
            return "Qadamlar tugadi"
        finally:
            await self.emit({"type": "status", "agent": name, "state": "bo'sh"})
