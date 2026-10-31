import os
import tempfile
import logging

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InputFile
from pptx import Presentation
from pptx.util import Inches

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_presentation(title: str, body: str, image_query: str, output_path: str) -> str:
    """Create a simple PPTX with a title slide, text, and an image.

    Args:
        title: Slide title.
        body: Slide body text.
        image_query: Query string for Unsplash (e.g., "technology").
        output_path: File path without extension (the function will add .pptx).

    Returns:
        The full path to the generated .pptx file.
    """

    prs = Presentation()
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


def parse_message(text: str) -> tuple[str, str, str]:
    """Parse a user's text message into title, body, and image query.

    Supported formats:
    - "Title|Body" (split on first |)
    - "Title\nBody..."
    - If the text contains "/img <query>", that query is used for the image.
    """

    image_query = "technology"
    # Extract /img command if present
    for part in text.splitlines():
        if part.strip().lower().startswith("/img "):
            image_query = part.strip()[5:].strip() or image_query
            break

    if "|" in text:
        title, body = text.split("|", 1)
        return title.strip(), body.strip(), image_query

    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return "Presentation", "", image_query

    title = lines[0]
    body = "\n".join(lines[1:]) if len(lines) > 1 else ""
    return title, body, image_query


async def cmd_start(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Send me some text and I'll build a simple PPTX for you.\n\n"
        "Use the first line as the title and the rest as slide body.\n"
        "You can also include `/img <keyword>` on a separate line to change the image topic.\n\n"
        "Example:\n"
        "My title\nMy bullet 1\nMy bullet 2\n/img nature\n\n"
        "Or: /ppt My title|My body|nature"
    )


async def cmd_ppt(message: types.Message):
    # /ppt Title|Body|image_query
    text = (message.text or "").strip()
    if text.lower().startswith("/ppt"):
        text = text[4:].strip()  # remove command

    if not text:
        await message.answer("Please provide text after /ppt. Example: /ppt My title|My body|nature")
        return

    title, body, image_query = parse_message(text)
    await send_pptx(message, title, body, image_query)


async def handle_message(message: types.Message):
    title, body, image_query = parse_message(message.text or "")
    await send_pptx(message, title, body, image_query)


async def send_pptx(message: types.Message, title: str, body: str, image_query: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "presentation")
        pptx_path = make_presentation(title, body, image_query, base_path)
        await message.answer_document(InputFile(pptx_path), caption="Here is your PPTX file.")


async def main() -> None:
    token = os.getenv("8250720996:AAHFXtJdalLj_G14urjd0fOltwWkmG-pskw")
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
