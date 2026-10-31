from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .generate_pdf import create_pdf_bytes
from io import BytesIO
import os

app = FastAPI()

# Loyihaning asosiy papkasi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# Static fayllar va template papkasi
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# PDF saqlash papkasi
PDF_DIR = os.path.join(BASE_DIR, "generated")
os.makedirs(PDF_DIR, exist_ok=True)

# Asosiy sahifa (HTML forma)
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Formani yuborish va PDF yaratish
@app.post("/create_pdf")
async def create_pdf(
    request: Request,
    fio: str = Form(...),
    address: str = Form(...),
    ls: str = Form(...),
    service: str = Form(...),
    amount: str = Form(...),
    date: str = Form(...)
):
    data = {
        "fio": fio,
        "address": address,
        "ls": ls,
        "service": service,
        "amount": amount,
        "date": date
    }
    pdf_bytes = create_pdf_bytes(data)
    filename = f"KVITANSIYA_{ls}.pdf"
    file_path = os.path.join(PDF_DIR, filename)

    # PDFni saqlash
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    # PDFni brauzerga uzatish
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={filename}"})
