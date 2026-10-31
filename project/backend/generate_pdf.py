from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import qrcode
from io import BytesIO
from PIL import Image

def create_qr_image(text: str, size=200):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img = img.resize((size, size))
    return img

def create_pdf_bytes(data: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width/2, height - 30*mm, "KOMMUNAL TO'LOV KVITANSIYASI")

    c.setFont('Helvetica', 14)
    start_y = height - 50*mm
    line_h = 10*mm

    fields = [
        ("F.I.SH:", data.get('fio', '')),
        ("Manzil:", data.get('address', '')),
        ("Hisob raqam (LS):", data.get('ls', '')),
        ("To'lov turi:", data.get('service', '')),
        ("To'lov summasi:", data.get('amount', '')),
        ("Sana:", data.get('date', '')),
    ]

    x_label = 20*mm
    x_value = 70*mm
    y = start_y
    for label, val in fields:
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x_label, y, label)
        c.setFont('Helvetica', 12)
        c.drawString(x_value, y, str(val))
        y -= line_h

    qr_text = f"LS:{data.get('ls','')}|SUM:{data.get('amount','')}|DATE:{data.get('date','')}"
    qr_img = create_qr_image(qr_text, size=150)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    qr_x = width - 60*mm
    qr_y = start_y - 20*mm
    c.drawImage(qr_buffer, qr_x, qr_y, width=40*mm, height=40*mm)

    c.setFont('Helvetica', 12)
    c.drawString(20*mm, 30*mm, "Taqdim etuvchi: Kommunal xizmat")
    c.drawString(20*mm, 20*mm, "Imzo: ___________________")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
