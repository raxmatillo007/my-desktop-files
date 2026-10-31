import os
import tempfile
import logging

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from pptx import Presentation
from pptx.util import Inches

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_presentation(slides: list[tuple[str, str, str]], output_path: str) -> str:
    """Create a PPTX with multiple slides.

    Each slide is a tuple of (title, body, image_query).
    """

    prs = Presentation()

    for title, body, image_query in slides:
        slide_layout = prs.slide_layouts[5]
        slide = prs.slides.add_slide(slide_layout)

        slide.shapes.title.text = title or "Presentation"

        left = Inches(0.5)
        top = Inches(2)
        width = Inches(4)

        textbox = slide.shapes.add_textbox(left, top, width, Inches(2))
        text_frame = textbox.text_frame
        text_frame.text = body or ""

        # Download an image from Unsplash and add it to the slide.
        image_path = output_path + ".jpg"
        try:
            img_url = f"https://source.unsplash.com/800x600/?{image_query or 'technology'}"
            resp = requests.get(img_url, timeout=20)
            resp.raise_for_status()
            with open(image_path, "wb") as f:
                f.write(resp.content)

            slide.shapes.add_picture(image_path, Inches(5), Inches(2), width=Inches(4))
        except Exception as e:
            logger.warning("Unable to download or add image: %s", e)

    pptx_path = output_path + ".pptx"
    prs.save(pptx_path)
    return pptx_path


def generate_slides_from_topic(topic: str, image_query: str, count: int = 3) -> list[tuple[str, str, str]]:
    """Generate a simple presentation automatically from a topic.

    If `count` is provided, it will create that many slides with generic
    titles/body.
    """

    topic = topic.strip()
    if not topic:
        return [("Presentation", "", image_query)]

    slides = []
    for i in range(1, max(1, count) + 1):
        slides.append(
            (
                f"{topic} - slayd {i}",
                f"{topic} haqida ma'lumot (slayd {i}).\n\nBu erda izohlar yozilishi mumkin.",
                image_query,
            )
        )

    return slides


def parse_slides(text: str) -> list[tuple[str, str, str]]:
    """Parse a user's message into a list of slides.

    Slide separators:
    - Use a line with `---` to split into multiple slides.
    - Within each slide, the first line is the title and the rest is body.
    - A `/img <keyword>` line anywhere sets the image query for all slides.
    - A slide may also use `Title|Body` on a single line.

    If only a single short topic is provided, generate a small presentation
    automatically from that topic.
    """

    image_query = "technology"
    parts = []

    # Extract /img command if present
    lines = [l.rstrip() for l in text.splitlines()]
    for line in lines:
        if line.strip().lower().startswith("/img "):
            image_query = line.strip()[5:].strip() or image_query

    # If user just wrote one short line (topic), auto-generate slides.
    stripped = text.strip()
    if stripped and "\n" not in stripped and "---" not in stripped:
        # If they used `topic|count`, allow specifying number of slides.
        if "|" in stripped:
            topic, rest = stripped.split("|", 1)
            if rest.strip().isdigit():
                return generate_slides_from_topic(topic.strip(), image_query, int(rest.strip()))
        return generate_slides_from_topic(stripped, image_query)

    # Split slides by lines containing only '---'
    slide_chunks = []
    current = []
    for line in lines:
        if line.strip() == "---":
            if current:
                slide_chunks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        slide_chunks.append("\n".join(current))

    if not slide_chunks:
        slide_chunks = [""]

    for chunk in slide_chunks:
        text = chunk.strip()
        if not text:
            parts.append(("Presentation", "", image_query))
            continue

        if "|" in text and "\n" not in text:
            title, body = text.split("|", 1)
            parts.append((title.strip(), body.strip(), image_query))
            continue

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            parts.append(("Presentation", "", image_query))
            continue

        title = lines[0]
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
        parts.append((title, body, image_query))

    return parts


async def cmd_start(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Menga mavzu nomi yuboring va men sizga PPTX tayyorlayman.\n\n"
        "Agar faqat mavzu yozsangiz, men avtomatik kichik prezentatsiya yarataman.\n"
        "Rasm mavzusini o‘zgartirish uchun alohida qatorda `/img <keyword>` yozing.\n\n"
        "Agar bir nechta slayd kerak bo‘lsa, slaydlarni `---` bilan ajrating.\n"
        "Misol:\n"
        "Sarlavha 1\nIzoh 1\nIzoh 2\n---\n"
        "Sarlavha 2\nIzoh A\nIzoh B\n/img nature\n\n"
        "Yoki: /ppt Mavzu|3 (bu yerda 3 — slaydlar soni)"
    )


async def cmd_ppt(message: types.Message):
    # /ppt Title|Body|image_query
    text = (message.text or "").strip()
    if text.lower().startswith("/ppt"):
        text = text[4:].strip()  # remove command

    if not text:
        await message.answer("Please provide text after /ppt. Example: /ppt My title|My body|nature")
        return

    slides = parse_slides(text)
    await send_pptx(message, slides)


async def handle_message(message: types.Message):
    slides = parse_slides(message.text or "")
    await send_pptx(message, slides)


async def send_pptx(message: types.Message, slides: list[tuple[str, str, str]]):
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "presentation")
        pptx_path = make_presentation(slides, base_path)
        await message.answer_document(FSInputFile(pptx_path), caption="Here is your PPTX file.")


async def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN environment variable and restart.")

    bot = Bot(token)
    dp = Dispatcher()
    dp.message.register(cmd_start, Command(commands=["start", "help"]))
    dp.message.register(cmd_ppt, Command(commands=["ppt"]))
    dp.message.register(handle_message)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
