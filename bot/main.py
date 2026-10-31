import asyncio
import json
import os
import re
import tempfile
import logging
from typing import Final

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

import requests
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Pt, Inches
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE


router = Router()
user_state: dict[int, dict] = {}


def _clean_query(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"[^\w\s\-’'`]", "", text, flags=re.UNICODE).strip()


def search_image(query: str, api_key: str) -> str | None:
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape",
        "size": "medium",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        photos = data.get("photos") or []
        if not photos:
            return None
        src = photos[0].get("src") or {}
        return src.get("large") or src.get("medium") or src.get("original")
    except Exception:
        return None


def download_image(image_url: str) -> str | None:
    try:
        resp = requests.get(image_url, stream=True, timeout=30)
        resp.raise_for_status()

        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "png" in content_type:
            suffix = ".png"
        else:
            suffix = ".jpg"

        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            for chunk in resp.iter_content(chunk_size=256 * 1024):
                if chunk:
                    f.write(chunk)
        return path
    except Exception:
        return None


def choose_theme(topic: str) -> dict[str, RGBColor]:
    t = topic.lower()

    tech_kw = ["ai", "sun'iy", "intellekt", "dastur", "python", "robot", "kompyuter", "internet", "texnolog", "data"]
    edu_kw = ["ta'lim", "maktab", "universitet", "o'quv", "dars", "o‘qit", "pedagog", "kurs", "imtihon"]
    nature_kw = ["tabiat", "o‘simlik", "hayvon", "ekolog", "iqlim", "o‘rmon", "tog", "daryo", "okean", "bio"]
    business_kw = ["biznes", "marketing", "sotuv", "moliya", "invest", "strateg", "startup", "reja", "bozor"]

    def has_any(keywords: list[str]) -> bool:
        return any(k in t for k in keywords)

    if has_any(tech_kw):
        return {
            "bg": RGBColor(11, 18, 32),
            "title": RGBColor(245, 245, 245),
            "text": RGBColor(229, 231, 235),
            "accent": RGBColor(34, 211, 238),
            "overlay": RGBColor(0, 0, 0),
        }
    if has_any(nature_kw):
        return {
            "bg": RGBColor(240, 253, 244),
            "title": RGBColor(6, 78, 59),
            "text": RGBColor(6, 95, 70),
            "accent": RGBColor(22, 163, 74),
            "overlay": RGBColor(0, 0, 0),
        }
    if has_any(edu_kw):
        return {
            "bg": RGBColor(255, 255, 255),
            "title": RGBColor(15, 23, 42),
            "text": RGBColor(17, 24, 39),
            "accent": RGBColor(37, 99, 235),
            "overlay": RGBColor(0, 0, 0),
        }
    if has_any(business_kw):
        return {
            "bg": RGBColor(255, 255, 255),
            "title": RGBColor(17, 24, 39),
            "text": RGBColor(55, 65, 81),
            "accent": RGBColor(17, 24, 39),
            "overlay": RGBColor(0, 0, 0),
        }
    return {
        "bg": RGBColor(255, 255, 255),
        "title": RGBColor(17, 24, 39),
        "text": RGBColor(55, 65, 81),
        "accent": RGBColor(59, 130, 246),
        "overlay": RGBColor(0, 0, 0),
    }


def set_slide_background(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_title_box(slide, text: str, left, top, width, height, color: RGBColor) -> None:
    title_box = slide.shapes.add_textbox(left, top, width, height)
    tf = title_box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = color


def add_bullets_box(slide, bullets: list[str], left, top, width, height, color: RGBColor) -> None:
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()

    for idx, bullet in enumerate(bullets):
        if idx == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = bullet
        p.level = 0
        p.font.size = Pt(20)
        p.font.color.rgb = color


def add_accent_bar(slide, left, top, width, height, color: RGBColor) -> None:
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()


def add_image_right_or_placeholder(slide, image_path: str | None, left, top, width, height, theme: dict[str, RGBColor]) -> None:
    if image_path:
        slide.shapes.add_picture(image_path, left, top, width=width)
        return

    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(230, 230, 230)
    shape.line.color.rgb = RGBColor(200, 200, 200)
    tf = shape.text_frame
    tf.text = "Rasm topilmadi"
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].font.size = Pt(16)
    tf.paragraphs[0].font.color.rgb = theme["text"]


def create_chart(slide, topic: str, theme: dict[str, RGBColor]) -> None:
    """
    Oddiy demо statistikani ko‘rsatish uchun ustunli, chiziqli yoki doiraviy diagramma chizadi.
    Hozircha demo ma'lumotlardan foydalanadi.
    """
    chart_data = CategoryChartData()
    chart_data.categories = ["Yil 1", "Yil 2", "Yil 3", "Yil 4"]
    values = (10, 25, 40, 55)
    chart_data.add_series("O‘sish", values)

    x, y, cx, cy = Inches(0.9), Inches(2.2), Inches(8.0), Inches(3.8)

    t = topic.lower()
    if any(k in t for k in ["taqsimot", "ulush", "segment"]):
        chart_type = XL_CHART_TYPE.PIE
    elif any(k in t for k in ["trend", "vaqt", "time", "dynamic"]):
        chart_type = XL_CHART_TYPE.LINE_MARKERS
    else:
        chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED

    chart_shape = slide.shapes.add_chart(chart_type, x, y, cx, cy, chart_data)
    chart = chart_shape.chart
    chart.has_legend = False
    chart.chart_title.text_frame.text = f"{topic} bo‘yicha demo ma'lumotlar"
    chart.chart_title.text_frame.paragraphs[0].font.size = Pt(18)
    chart.chart_title.text_frame.paragraphs[0].font.bold = True

    series = chart.series[0]
    fill = series.format.fill
    fill.solid()
    fill.fore_color.rgb = theme["accent"]


def _openai_generate_json(prompt: str, api_key: str) -> dict | list | None:
    """
    Oddiy OpenAI Chat Completions chaqiruvi (requests bilan).
    Output JSON bo‘lishi kerak.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You generate clean JSON only. No markdown, no extra text."},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = (
            (data.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if not content:
            return None
        # Ba'zan model JSON'ni ```json ... ``` ko‘rinishida qaytarishi mumkin.
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()
        return json.loads(content)
    except Exception:
        return None


def generate_slide_content(topic: str, content_slide_count: int, api_key: str) -> list[dict]:
    """
    AI yordamida slaydlar uchun sarlavha va 3–5 bullet generatsiya qiladi.
    Qaytadigan format: [{"title": "...", "bullets": ["...", "...", ...]}, ...]
    """
    example_sections = [
        "Kirish",
        "Ta'rifi",
        "Tarixi",
        "Qanday ishlaydi",
        "Turlari",
        "Afzalliklari",
        "Kamchiliklari",
        "Misollar",
        "Xulosa",
    ]

    prompt = (
        f"Mavzu: {topic}\n"
        f"Kontent slaydlar soni: {content_slide_count}\n\n"
        "Vazifa:\n"
        "- Uzbek tilida prezentatsiya uchun kontent yozing.\n"
        "- Har bir slayd uchun: aniq sarlavha va 3–5 ta qisqa bullet.\n"
        "- Bulletlar prezentatsiyaga mos, sodda va tushunarli bo‘lsin.\n"
        "- Strukturani mavzuga mos mantiqiy bo‘limlarga ajrating.\n"
        f"- Bo‘limlar misoli (yo‘l-yo‘riq): {', '.join(example_sections)}\n\n"
        "Chiqish formati:\n"
        "Faqat JSON massiv qaytaring (hech qanday izohsiz).\n"
        'Har bir element: {"title": "...", "bullets": ["...", "...", "..."]}\n'
        "Aniq talablar:\n"
        f"- Massiv uzunligi aynan {content_slide_count} bo‘lsin.\n"
        "- Har bir bullets uzunligi 3 dan 5 gacha bo‘lsin.\n"
    )

    raw = _openai_generate_json(prompt, api_key)
    if isinstance(raw, list):
        slides = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            bullets = item.get("bullets", [])
            if not title:
                continue
            if not isinstance(bullets, list):
                bullets = []
            bullets = [str(b).strip() for b in bullets if str(b).strip()]

            if len(bullets) < 3:
                bullets += ["Asosiy g‘oya.", "Muhim nuqta.", "Qisqa izoh."]
            # Har slaydda 3–4 ta bullet bo‘lishi uchun 4 tadan oshmasin
            bullets = bullets[:4]
            slides.append({"title": title, "bullets": bullets})

        if len(slides) == content_slide_count:
            return slides

    # Fallback: shablon bo‘limlar (AI ishlamasa ham bot ishlasin)
    base_titles = [
        "Kirish",
        "Ta'rifi",
        "Tarixi",
        "Qanday ishlaydi",
        "Turlari",
        "Afzalliklari",
        "Kamchiliklari",
        "Misollar",
        "Xulosa",
    ]
    out: list[dict] = []
    for i in range(content_slide_count):
        section = base_titles[i % len(base_titles)]
        out.append(
            {
                "title": f"{section} – {topic}",
                "bullets": [
                    f"{topic} bo‘yicha asosiy fikr.",
                    f"{section} bo‘limidagi muhim jihat.",
                    "Qisqa misol yoki izoh.",
                    "Amaliy ahamiyati.",
                ][:5],
            }
        )
    return out


def create_presentation(topic: str, slide_count: int, filepath: str = "presentation.pptx") -> str:
    """
    Berilgan mavzu bo‘yicha ixtiyoriy sondagi slaydli PowerPoint prezentatsiya yaratadi.
    1‑slayd: Mavzu nomi (title slide)
    Qolgan slaydlar: bo‘lim sarlavhasi va 3–5 ta bullet point.
    """
    prs = Presentation()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    pexels_key = os.getenv("PEXELS_API_KEY", "").strip()
    theme = choose_theme(topic)

    total_slides = max(slide_count, 1)
    content_slide_count = max(total_slides - 1, 0)
    ai_slides = generate_slide_content(topic, content_slide_count, openai_key) if content_slide_count else []

    slide_width = prs.slide_width
    slide_height = prs.slide_height

    margin_x = Inches(0.6)
    margin_top = Inches(0.5)
    margin_bottom = Inches(0.6)
    title_h = Inches(1.1)
    gap = Inches(0.35)

    # Katta vizual rasmlar: slaydning ~50% kengligini egallaydi
    image_w = int(slide_width * 0.5)
    image_left = int(slide_width - margin_x - image_w)
    content_top = margin_top + title_h
    content_h = slide_height - content_top - margin_bottom
    text_left = margin_x
    text_w = int(image_left - gap - text_left)

    blank_layout = prs.slide_layouts[6]

    # 1‑slayd: Title slide (background image + overlay + title + subtitle)
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide, theme["bg"])

    bg_tmp = None
    if pexels_key:
        bg_url = search_image(_clean_query(topic), pexels_key)
        if bg_url:
            bg_tmp = download_image(bg_url)

    if bg_tmp:
        slide.shapes.add_picture(bg_tmp, 0, 0, width=slide_width, height=slide_height)

    # overlay (matn o‘qilishi uchun)
    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, slide_width, slide_height)
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = theme["overlay"]
    overlay.fill.fore_color.transparency = 0.45
    overlay.line.fill.background()

    add_title_box(slide, topic, margin_x, Inches(2.2), slide_width - 2 * margin_x, Inches(1.2), theme["title"])

    subtitle_box = slide.shapes.add_textbox(margin_x, Inches(3.25), slide_width - 2 * margin_x, Inches(0.6))
    stf = subtitle_box.text_frame
    stf.clear()
    sp = stf.paragraphs[0]
    sp.text = "AI Generated Presentation"
    sp.alignment = PP_ALIGN.CENTER
    sp.font.size = Pt(20)
    sp.font.color.rgb = theme["text"]

    if bg_tmp:
        try:
            os.remove(bg_tmp)
        except OSError:
            pass

    # 2..N slaydlar (AI kontent + rasm + turli maketlar)
    # Ba'zi slaydlar: matn+rasm, ba'zilari full-image, ba'zilari "quote" va ba'zilari chart.
    stats_keywords = ["stat", "foiz", "growth", "o‘sish", "market", "sales", "analytics", "moliya"]
    has_stats_topic = any(k in topic.lower() for k in stats_keywords)

    for idx, slide_data in enumerate(ai_slides, start=2):
        slide_type_index = (idx - 2) % 4  # 0: text+image, 1: full image, 2: quote, 3: chart/image focus
        slide_title = slide_data["title"]
        bullets = slide_data["bullets"]

        img_tmp = None
        img_url = None
        if pexels_key:
            query = _clean_query(f"{topic} {slide_title}")
            img_url = search_image(query, pexels_key)
            if img_url:
                img_tmp = download_image(img_url)

        # 0) Klassik: text left + image right
        if slide_type_index == 0:
            slide = prs.slides.add_slide(blank_layout)
            set_slide_background(slide, theme["bg"])

            add_title_box(slide, slide_title, margin_x, margin_top, slide_width - 2 * margin_x, title_h, theme["title"])
            add_accent_bar(slide, margin_x, margin_top + title_h - Inches(0.15), Inches(1.8), Inches(0.08), theme["accent"])
            add_bullets_box(slide, bullets[:5], text_left, content_top, text_w, content_h, theme["text"])
            add_image_right_or_placeholder(slide, img_tmp, image_left, content_top, image_w, content_h, theme)

        # 1) Image-focus: katta fon rasm, pastda ozroq matn
        elif slide_type_index == 1 and img_tmp:
            slide = prs.slides.add_slide(blank_layout)
            set_slide_background(slide, theme["bg"])
            slide.shapes.add_picture(img_tmp, 0, 0, width=slide_width, height=slide_height)

            # Qoramtir overlay
            overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, slide_width, slide_height)
            overlay.fill.solid()
            overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
            overlay.fill.fore_color.transparency = 0.35
            overlay.line.fill.background()

            add_title_box(slide, slide_title, margin_x, Inches(0.7), slide_width - 2 * margin_x, Inches(1.0), theme["title"])
            add_bullets_box(
                slide,
                bullets[:3],
                margin_x,
                slide_height - Inches(2.3),
                slide_width - 2 * margin_x,
                Inches(1.8),
                theme["text"],
            )

        # 2) Quote / asosiy fikr slaydi
        elif slide_type_index == 2:
            slide = prs.slides.add_slide(blank_layout)
            set_slide_background(slide, theme["bg"])

            main_text = bullets[0] if bullets else slide_title
            quote_box = slide.shapes.add_textbox(
                margin_x,
                Inches(2.0),
                slide_width - 2 * margin_x,
                Inches(3.0),
            )
            qtf = quote_box.text_frame
            qtf.clear()
            qp = qtf.paragraphs[0]
            qp.text = f"“{main_text}”"
            qp.alignment = PP_ALIGN.CENTER
            qp.font.size = Pt(32)
            qp.font.bold = True
            qp.font.color.rgb = theme["title"]

            sub_box = slide.shapes.add_textbox(
                margin_x,
                Inches(5.1),
                slide_width - 2 * margin_x,
                Inches(1.0),
            )
            stf = sub_box.text_frame
            stf.clear()
            sp = stf.paragraphs[0]
            sp.text = slide_title
            sp.alignment = PP_ALIGN.CENTER
            sp.font.size = Pt(18)
            sp.font.color.rgb = theme["text"]

        # 3) Chart yoki image-focus text
        else:
            slide = prs.slides.add_slide(blank_layout)
            set_slide_background(slide, theme["bg"])

            add_title_box(slide, slide_title, margin_x, margin_top, slide_width - 2 * margin_x, Inches(0.9), theme["title"])

            if has_stats_topic:
                create_chart(slide, topic, theme)
            else:
                add_bullets_box(slide, bullets[:5], margin_x, Inches(1.8), slide_width - 2 * margin_x, Inches(3.0), theme["text"])

            if img_tmp:
                # Rasm slaydning pastki yarmida katta ko‘rinishda bo‘lsin
                bottom_img_h = int(slide_height * 0.48)
                bottom_img_top = int(slide_height - bottom_img_h - margin_bottom)
                add_image_right_or_placeholder(
                    slide,
                    img_tmp,
                    int(margin_x),
                    bottom_img_top,
                    int(slide_width - 2 * margin_x),
                    bottom_img_h,
                    theme,
                )

        if img_tmp:
            try:
                os.remove(img_tmp)
            except OSError:
                pass

    prs.save(filepath)
    return filepath


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else message.chat.id
    user_state[user_id] = {"stage": "awaiting_topic", "topic": None}

    text = (
        "Salom! 👋\n"
        "Men siz yuborgan mavzu bo‘yicha PowerPoint prezentatsiya tayyorlab bera olaman.\n\n"
        "Avval prezentatsiya mavzusini yuboring.\n\n"
        "*Prezentatsiya mavzusini yozing.*"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text)
async def handle_topic(message: Message) -> None:
    topic = message.text.strip()
    user_id = message.from_user.id if message.from_user else message.chat.id
    state = user_state.get(user_id, {"stage": "awaiting_topic", "topic": None})

    # 1‑bosqich: mavzuni qabul qilish
    if state["stage"] == "awaiting_topic":
        if not topic:
            await message.answer("Iltimos, bo‘sh bo‘lmagan mavzu yuboring.")
            return

        state["topic"] = topic
        state["stage"] = "awaiting_slide_count"
        user_state[user_id] = state

        await message.answer(
            "Prezentatsiya nechta slayddan iborat bo‘lsin?\n"
            "Masalan: 5, 8 yoki 10 sonini yuboring."
        )
        return

    # 2‑bosqich: slaydlar sonini qabul qilish
    if state["stage"] == "awaiting_slide_count":
        try:
            slide_count = int(topic)
        except ValueError:
            await message.answer("Iltimos, slaydlar sonini butun son ko‘rinishida yuboring (masalan: 5).")
            return

        if slide_count < 1:
            await message.answer("Slaydlar soni kamida 1 bo‘lishi kerak. Iltimos, yana urinib ko‘ring.")
            return

        if slide_count > 30:
            await message.answer("Juda katta son yubordingiz. Iltimos, 30 tadan kamroq slayd sonini kiriting.")
            return

        topic_text = state.get("topic") or "Mavzu"

        await message.answer(
            f"*{topic_text}* mavzusi bo‘yicha {slide_count} ta slaydli prezentatsiya yaratyapman...\n"
            "Iltimos, bir necha soniya kuting.",
            parse_mode="Markdown",
        )

        filepath = "presentation.pptx"
        create_presentation(topic_text, slide_count, filepath)

        document = FSInputFile(filepath, filename="presentation.pptx")
        await message.answer_document(
            document,
            caption=f"{topic_text} mavzusi bo‘yicha prezentatsiyangiz tayyor. ✅",
        )

        # Yangi prezentatsiya uchun holatni qayta tiklaymiz
        user_state[user_id] = {"stage": "awaiting_topic", "topic": None}
        await message.answer("Yana bir prezentatsiya uchun yangi mavzuni yuborishingiz mumkin.")
        return

    # Agar nimadir noto‘g‘ri bo‘lsa, boshidan boshlaymiz
    user_state[user_id] = {"stage": "awaiting_topic", "topic": None}
    await message.answer("Prezentatsiya mavzusini yozing.")


async def main() -> None:
    # Tokenni muhiti o‘zgaruvchisidan olamiz (kod ichida saqlamang)
    token: Final[str | None] = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN muhiti o‘zgaruvchisi o‘rnatilmagan.\n"
            "Botni ishga tushirishdan oldin uni Telegram bot tokeningizga tenglashtiring."
        )

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise RuntimeError(
            "OPENAI_API_KEY muhiti o‘zgaruvchisi o‘rnatilmagan.\n"
            "AI kontent uchun OpenAI API kalitini oling va OPENAI_API_KEY ga o‘rnating."
        )

    pexels_key = os.getenv("PEXELS_API_KEY")
    if not pexels_key:
        raise RuntimeError(
            "PEXELS_API_KEY muhiti o‘zgaruvchisi o‘rnatilmagan.\n"
            "Pexels API kalitini oling va PEXELS_API_KEY ga o‘rnating."
        )

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    print("Bot ishga tushdi. To‘xtatish uchun Ctrl+C bosing.")

    # Ba'zan tarmoq muammolari bo‘lib, Telegram server ulanishni uzib qo‘yishi mumkin.
    # Shunda bot to‘xtab qolmasligi uchun qayta urinib turamiz.
    while True:
        try:
            await dp.start_polling(bot)
            break  # polling normal to‘xtasa (masalan, signal orqali) loopdan chiqamiz
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.exception("Polling xatosi: %s", e)
            print("Tarmoq xatosi yuz berdi. 5 soniyadan keyin qayta urinaman...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to‘xtatildi.")

