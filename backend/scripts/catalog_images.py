"""Генерация иллюстративных фото пиццы под размер и загрузка в S3."""

from __future__ import annotations

from io import BytesIO
from math import cos, pi, sin
from random import Random

from PIL import Image, ImageDraw, ImageFont

from app.services.storage import StorageService

# Диаметр «пиццы» на холсте 800x800 для каждого размера
SIZE_DIAMETERS = {
    "Маленькая": 420,
    "Средняя": 560,
    "Большая": 700,
    "Стандарт": 520,
}

TOPPING_PALETTES = {
    "pepperoni-fresh": [(196, 52, 52), (240, 120, 80)],
    "pepperoni": [(180, 40, 40), (220, 90, 70)],
    "cheese": [(245, 210, 90), (255, 230, 140)],
    "ham-cheese": [(220, 140, 150), (245, 210, 90)],
    "ham-mushrooms": [(220, 140, 150), (180, 150, 120)],
    "ham-pickles": [(220, 140, 150), (90, 160, 80)],
    "double-chicken": [(230, 190, 140), (245, 210, 90)],
    "bbq-chicken": [(140, 70, 40), (230, 190, 140)],
    "carbonara": [(120, 80, 60), (245, 210, 90)],
    "arriva": [(196, 52, 52), (230, 190, 140), (90, 160, 80)],
    "four-seasons": [(220, 140, 150), (196, 52, 52), (180, 150, 120), (230, 90, 70)],
    "meat-mix": [(120, 80, 60), (196, 52, 52), (180, 40, 40)],
    "margherita": [(220, 60, 50), (70, 140, 70)],
    "diablo": [(196, 52, 52), (60, 140, 60)],
    "chicken-teriyaki": [(140, 70, 40), (230, 190, 140)],
    "default": [(220, 90, 70), (245, 210, 90)],
}


def _font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def render_pizza_image(
    *,
    title: str,
    slug: str,
    size_name: str,
    size_label: str,
) -> bytes:
    canvas = 800
    image = Image.new("RGB", (canvas, canvas), (245, 239, 230))
    draw = ImageDraw.Draw(image)
    rng = Random(f"{slug}:{size_name}")

    diameter = SIZE_DIAMETERS.get(size_name, 560)
    margin = (canvas - diameter) // 2
    crust = (margin - 18, margin - 18, margin + diameter + 18, margin + diameter + 18)
    pizza = (margin, margin, margin + diameter, margin + diameter)

    draw.ellipse(crust, fill=(194, 140, 70))
    draw.ellipse(pizza, fill=(220, 70, 45))
    draw.ellipse(
        (margin + 28, margin + 28, margin + diameter - 28, margin + diameter - 28),
        fill=(245, 205, 95),
    )

    colors = TOPPING_PALETTES.get(slug, TOPPING_PALETTES["default"])
    cx = cy = canvas / 2
    radius = diameter / 2 - 55
    for index in range(28):
        angle = (2 * pi * index / 28) + rng.random()
        distance = radius * (0.25 + 0.7 * rng.random())
        x = cx + distance * cos(angle)
        y = cy + distance * sin(angle)
        spot = 14 + rng.randint(0, 16)
        color = colors[index % len(colors)]
        draw.ellipse((x - spot, y - spot, x + spot, y + spot), fill=color)

    title_font = _font(34)
    label_font = _font(28)
    draw.rectangle((0, canvas - 110, canvas, canvas), fill=(30, 30, 30))
    draw.text((28, canvas - 95), title, fill=(255, 255, 255), font=title_font)
    draw.text((28, canvas - 52), size_label, fill=(255, 210, 120), font=label_font)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()


def upload_pizza_size_image(
    storage: StorageService,
    *,
    title: str,
    slug: str,
    size_name: str,
    size_cm: int,
) -> str:
    payload = render_pizza_image(
        title=title,
        slug=slug,
        size_name=size_name,
        size_label=f"{size_cm} см · {size_name}",
    )
    uploaded = storage.upload(
        data=payload,
        filename=f"{slug}-{size_cm}.jpg",
        content_type="image/jpeg",
        folder=f"products/{slug}",
    )
    return uploaded.url
