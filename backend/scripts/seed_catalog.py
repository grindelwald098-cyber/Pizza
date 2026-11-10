"""Очистка и заполнение каталога данными в стиле Додо Пицца + фото по размерам."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import SessionLocal
from app.database.models import (
    Category,
    DoughType,
    Ingredient,
    Product,
    ProductAddon,
    ProductDough,
    ProductIngredient,
    ProductSize,
    Promocode,
    Role,
    Size,
)
from app.database.models.cart_item_added_ingredients import CartItemAddedIngredient
from app.database.models.cart_items import CartItem
from app.database.models.favorites import Favorite
from app.database.models.order_item_added_ingredients import OrderItemAddedIngredient
from app.database.models.order_items import OrderItem
from app.database.models.reviews import Review
from app.services.storage import get_storage_service
from scripts.catalog_images import upload_pizza_size_image


def uid() -> uuid.UUID:
    return uuid.uuid4()


async def clear_catalog(session: AsyncSession) -> None:
    # Сначала зависимости от products / ingredients
    await session.execute(delete(CartItemAddedIngredient))
    await session.execute(delete(CartItem))
    await session.execute(delete(OrderItemAddedIngredient))
    await session.execute(delete(OrderItem))
    await session.execute(delete(Favorite))
    await session.execute(delete(Review))
    await session.execute(delete(ProductAddon))
    await session.execute(delete(ProductIngredient))
    await session.execute(delete(ProductDough))
    await session.execute(delete(ProductSize))
    await session.execute(delete(Product))
    await session.execute(delete(Category))
    await session.execute(delete(Size))
    await session.execute(delete(Ingredient))
    await session.execute(delete(DoughType))
    await session.commit()


async def seed_reference(session: AsyncSession) -> dict:
    categories = [
        Category(
            id=uid(),
            name="Пицца",
            slug="pizza",
            description="Пиццы 25 / 30 / 35 см",
            sort_order=1,
            is_active=True,
        ),
        Category(
            id=uid(),
            name="Закуски",
            slug="snacks",
            description="Картофель, наггетсы и закуски к пицце",
            sort_order=2,
            is_active=True,
        ),
        Category(
            id=uid(),
            name="Напитки",
            slug="drinks",
            description="Газировка, соки и вода",
            sort_order=3,
            is_active=True,
        ),
        Category(
            id=uid(),
            name="Десерты",
            slug="desserts",
            description="Сладкое к заказу",
            sort_order=4,
            is_active=True,
        ),
        Category(
            id=uid(),
            name="Соусы",
            slug="sauces",
            description="Дополнительные соусы",
            sort_order=5,
            is_active=True,
        ),
    ]
    session.add_all(categories)

    sizes = [
        Size(id=uid(), name="Маленькая", value=25, unit="cm", sort_order=1),
        Size(id=uid(), name="Средняя", value=30, unit="cm", sort_order=2),
        Size(id=uid(), name="Большая", value=35, unit="cm", sort_order=3),
        Size(id=uid(), name="Стандарт", value=1, unit="pcs", sort_order=4),
        Size(id=uid(), name="330 мл", value=330, unit="ml", sort_order=5),
        Size(id=uid(), name="500 мл", value=500, unit="ml", sort_order=6),
        Size(id=uid(), name="1 л", value=1000, unit="ml", sort_order=7),
    ]
    session.add_all(sizes)

    dough_types = [
        DoughType(id=uid(), name="Традиционное", sort_order=1, is_active=True),
        DoughType(id=uid(), name="Тонкое", sort_order=2, is_active=True),
    ]
    session.add_all(dough_types)

    ingredient_rows = [
        ("Томатный соус", "Фирменный томатный соус", "70.00"),
        ("Соус альфредо", "Фирменный сливочный соус альфредо", "90.00"),
        ("Соус BBQ", "Соус барбекю", "80.00"),
        ("Соус ранч", "Сливочный соус ранч", "80.00"),
        ("Соус бургер", "Соус бургер", "80.00"),
        ("Соус терияки", "Соус терияки", "80.00"),
        ("Соус песто", "Соус песто", "90.00"),
        ("Соус сладкий чили", "Сладкий чили", "80.00"),
        ("Моцарелла", "Сыр моцарелла", "120.00"),
        ("Пармезан", "Сыр пармезан", "150.00"),
        ("Чеддер", "Сыр чеддер", "130.00"),
        ("Брынза", "Кубики брынзы", "140.00"),
        ("Пепперони", "Пикантная пепперони", "170.00"),
        ("Ветчина", "Ветчина", "140.00"),
        ("Бекон", "Бекон", "160.00"),
        ("Говядина", "Пряная говядина", "190.00"),
        ("Свиная шейка", "Сочная свиная шейка", "180.00"),
        ("Куриное филе", "Цыплёнок", "150.00"),
        ("Чоризо", "Острые колбаски чоризо", "170.00"),
        ("Шампиньоны", "Шампиньоны", "90.00"),
        ("Помидоры", "Томаты", "80.00"),
        ("Болгарский перец", "Сладкий перец", "80.00"),
        ("Красный лук", "Красный лук", "60.00"),
        ("Маринованные огурчики", "Маринованные огурчики", "70.00"),
        ("Ананасы", "Ананасы", "100.00"),
        ("Халапеньо", "Острый халапеньо", "70.00"),
        ("Чеснок", "Чеснок", "50.00"),
        ("Итальянские травы", "Итальянские травы", "40.00"),
    ]
    ingredients = [
        Ingredient(
            id=uid(),
            name=name,
            description=description,
            price=Decimal(price),
            is_available=True,
        )
        for name, description, price in ingredient_rows
    ]
    session.add_all(ingredients)
    await session.flush()

    return {
        "categories": {c.slug: c for c in categories},
        "sizes": {s.name: s for s in sizes},
        "doughs": {d.name: d for d in dough_types},
        "ingredients": {i.name: i for i in ingredients},
    }


def pizza_doughs(ref: dict) -> list[ProductDough]:
    return [
        ProductDough(
            id=uid(),
            dough_type_id=ref["doughs"]["Традиционное"].id,
            is_default=True,
        ),
        ProductDough(
            id=uid(),
            dough_type_id=ref["doughs"]["Тонкое"].id,
            is_default=False,
        ),
    ]


def make_ingredients(ref: dict, items: list[tuple[str, str, bool]]) -> list[ProductIngredient]:
    return [
        ProductIngredient(
            id=uid(),
            ingredient_id=ref["ingredients"][name].id,
            quantity=Decimal(qty),
            is_default=is_default,
            is_active=True,
        )
        for name, qty, is_default in items
    ]


def make_addons(ref: dict, names: list[str]) -> list[ProductAddon]:
    return [
        ProductAddon(
            id=uid(),
            ingredient_id=ref["ingredients"][name].id,
            is_available=True,
            additional_price=ref["ingredients"][name].price,
        )
        for name in names
    ]


def pizza_sizes_with_images(
    ref: dict,
    *,
    title: str,
    slug: str,
    prices: tuple[str, str, str],
) -> tuple[list[ProductSize], str]:
    """Создаёт размеры 25/30/35 с отдельным фото на каждый размер."""
    storage = get_storage_service()
    rows: list[ProductSize] = []
    default_image_url = ""

    size_specs = [
        ("Маленькая", prices[0], True),
        ("Средняя", prices[1], False),
        ("Большая", prices[2], False),
    ]
    for size_name, price, is_default in size_specs:
        size = ref["sizes"][size_name]
        image_url = upload_pizza_size_image(
            storage,
            title=title,
            slug=slug,
            size_name=size_name,
            size_cm=size.value,
        )
        if is_default:
            default_image_url = image_url
        rows.append(
            ProductSize(
                id=uid(),
                size_id=size.id,
                price=Decimal(price),
                is_available=True,
                is_default=is_default,
                image_url=image_url,
            )
        )
    return rows, default_image_url


async def seed_products(session: AsyncSession, ref: dict) -> None:
    pizza_cat = ref["categories"]["pizza"].id
    snacks_cat = ref["categories"]["snacks"].id
    drinks_cat = ref["categories"]["drinks"].id
    desserts_cat = ref["categories"]["desserts"].id
    sauces_cat = ref["categories"]["sauces"].id

    common_addons = [
        "Моцарелла",
        "Пепперони",
        "Ветчина",
        "Бекон",
        "Куриное филе",
        "Шампиньоны",
        "Халапеньо",
        "Чеддер",
        "Пармезан",
        "Брынза",
    ]

    # Меню в стиле Додо: названия/составы/порядок цен 25→30→35
    pizzas = [
        {
            "name": "Пепперони фреш",
            "slug": "pepperoni-fresh",
            "description": "Пикантная пепперони, увеличенная порция моцареллы, томаты, фирменный томатный соус",
            "base": "299.00",
            "prices": ("299.00", "469.00", "629.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Пепперони", "1.00", True),
                ("Помидоры", "1.00", True),
            ],
        },
        {
            "name": "Пепперони",
            "slug": "pepperoni",
            "description": "Пикантная пепперони, увеличенная порция моцареллы, фирменный томатный соус",
            "base": "379.00",
            "prices": ("379.00", "569.00", "749.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Пепперони", "1.00", True),
            ],
        },
        {
            "name": "Сырная",
            "slug": "cheese",
            "description": "Моцарелла, сыры чеддер и пармезан, фирменный соус альфредо",
            "base": "299.00",
            "prices": ("299.00", "469.00", "629.00"),
            "ingredients": [
                ("Соус альфредо", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Чеддер", "1.00", True),
                ("Пармезан", "1.00", True),
            ],
        },
        {
            "name": "Ветчина и сыр",
            "slug": "ham-cheese",
            "description": "Ветчина, моцарелла, фирменный соус альфредо",
            "base": "349.00",
            "prices": ("349.00", "529.00", "699.00"),
            "ingredients": [
                ("Соус альфредо", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Ветчина", "1.00", True),
            ],
        },
        {
            "name": "Ветчина и грибы",
            "slug": "ham-mushrooms",
            "description": "Ветчина, шампиньоны, увеличенная порция моцареллы, фирменный томатный соус",
            "base": "379.00",
            "prices": ("379.00", "569.00", "749.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Ветчина", "1.00", True),
                ("Шампиньоны", "1.00", True),
            ],
        },
        {
            "name": "Ветчина и огурчики",
            "slug": "ham-pickles",
            "description": "Ветчина, маринованные огурчики, красный лук, соус ранч, моцарелла",
            "base": "329.00",
            "prices": ("329.00", "499.00", "669.00"),
            "ingredients": [
                ("Соус ранч", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Ветчина", "1.00", True),
                ("Маринованные огурчики", "1.00", True),
                ("Красный лук", "1.00", True),
            ],
        },
        {
            "name": "Двойной цыплёнок",
            "slug": "double-chicken",
            "description": "Двойная порция цыплёнка, моцарелла, фирменный соус альфредо",
            "base": "369.00",
            "prices": ("369.00", "549.00", "729.00"),
            "ingredients": [
                ("Соус альфредо", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Куриное филе", "2.00", True),
            ],
        },
        {
            "name": "Цыплёнок барбекю",
            "slug": "bbq-chicken",
            "description": "Двойная порция цыплёнка, бекон, соус барбекю, красный лук, моцарелла",
            "base": "429.00",
            "prices": ("429.00", "629.00", "819.00"),
            "ingredients": [
                ("Соус BBQ", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Куриное филе", "2.00", True),
                ("Бекон", "1.00", True),
                ("Красный лук", "1.00", True),
            ],
        },
        {
            "name": "Цыплёнок терияки",
            "slug": "chicken-teriyaki",
            "description": "Цыплёнок, красный лук, сладкий перец, соус терияки, моцарелла и соус альфредо",
            "base": "389.00",
            "prices": ("389.00", "579.00", "759.00"),
            "ingredients": [
                ("Соус альфредо", "1.00", True),
                ("Соус терияки", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Куриное филе", "1.00", True),
                ("Красный лук", "1.00", True),
                ("Болгарский перец", "1.00", True),
            ],
        },
        {
            "name": "Карбонара",
            "slug": "carbonara",
            "description": "Бекон, сыры чеддер и пармезан, моцарелла, томаты, красный лук, чеснок, соус альфредо",
            "base": "499.00",
            "prices": ("499.00", "719.00", "919.00"),
            "ingredients": [
                ("Соус альфредо", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Бекон", "1.00", True),
                ("Чеддер", "1.00", True),
                ("Пармезан", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Красный лук", "1.00", True),
                ("Чеснок", "1.00", True),
            ],
        },
        {
            "name": "Аррива!",
            "slug": "arriva",
            "description": "Цыплёнок, чоризо, соус бургер, сладкий перец, красный лук, томаты, моцарелла, соус ранч, чеснок",
            "base": "489.00",
            "prices": ("489.00", "709.00", "909.00"),
            "ingredients": [
                ("Соус бургер", "1.00", True),
                ("Соус ранч", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Куриное филе", "1.00", True),
                ("Чоризо", "1.00", True),
                ("Болгарский перец", "1.00", True),
                ("Красный лук", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Чеснок", "1.00", True),
            ],
        },
        {
            "name": "Четыре сезона",
            "slug": "four-seasons",
            "description": "Увеличенная порция моцареллы, ветчина, пепперони, брынза, томаты, шампиньоны, итальянские травы, томатный соус",
            "base": "529.00",
            "prices": ("529.00", "749.00", "949.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Ветчина", "1.00", True),
                ("Пепперони", "1.00", True),
                ("Брынза", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Шампиньоны", "1.00", True),
                ("Итальянские травы", "1.00", True),
            ],
        },
        {
            "name": "Мясной микс",
            "slug": "meat-mix",
            "description": "Свиная шейка, пряная говядина, пепперони, бекон, моцарелла и фирменный томатный соус",
            "base": "649.00",
            "prices": ("649.00", "879.00", "1099.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Свиная шейка", "1.00", True),
                ("Говядина", "1.00", True),
                ("Пепперони", "1.00", True),
                ("Бекон", "1.00", True),
            ],
        },
        {
            "name": "Маргарита",
            "slug": "margherita",
            "description": "Увеличенная порция моцареллы, томаты, итальянские травы, фирменный томатный соус",
            "base": "389.00",
            "prices": ("389.00", "579.00", "759.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Итальянские травы", "1.00", True),
            ],
        },
        {
            "name": "Диабло",
            "slug": "diablo",
            "description": "Острая пицца: пепперони, халапеньо, томатный соус и моцарелла",
            "base": "449.00",
            "prices": ("449.00", "659.00", "849.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Пепперони", "1.00", True),
                ("Халапеньо", "1.00", True),
                ("Чеснок", "1.00", True),
            ],
        },
    ]

    products: list[Product] = []
    for item in pizzas:
        sizes, default_image = pizza_sizes_with_images(
            ref,
            title=item["name"],
            slug=item["slug"],
            prices=item["prices"],
        )
        products.append(
            Product(
                id=uid(),
                category_id=pizza_cat,
                name=item["name"],
                slug=item["slug"],
                description=item["description"],
                image_url=default_image,
                base_price=Decimal(item["base"]),
                is_active=True,
                is_available=True,
                sizes=sizes,
                doughs=pizza_doughs(ref),
                ingredients=make_ingredients(ref, item["ingredients"]),
                addons=make_addons(ref, common_addons),
            )
        )

    snacks = [
        ("Картофель из печи", "baked-potato", "Запечённый картофель", "199.00"),
        ("Куриные наггетсы", "nuggets", "Куриные наггетсы", "249.00"),
        ("Додстер", "dodster", "Горячая закуска в тортилье", "229.00"),
    ]
    for name, slug, description, price in snacks:
        products.append(
            Product(
                id=uid(),
                category_id=snacks_cat,
                name=name,
                slug=slug,
                description=description,
                base_price=Decimal(price),
                is_active=True,
                is_available=True,
                sizes=[
                    ProductSize(
                        id=uid(),
                        size_id=ref["sizes"]["Стандарт"].id,
                        price=Decimal(price),
                        is_available=True,
                        is_default=True,
                    )
                ],
            )
        )

    drinks = [
        ("Добрый Кола", "cola", "Классическая кола", ("99.00", "129.00", "179.00")),
        ("Сок яблочный", "apple-juice", "Яблочный сок", ("119.00", "149.00", "199.00")),
        ("Вода", "still-water", "Питьевая вода", ("69.00", "89.00", "119.00")),
    ]
    drink_size_names = ["330 мл", "500 мл", "1 л"]
    for name, slug, description, prices in drinks:
        products.append(
            Product(
                id=uid(),
                category_id=drinks_cat,
                name=name,
                slug=slug,
                description=description,
                base_price=Decimal(prices[0]),
                is_active=True,
                is_available=True,
                sizes=[
                    ProductSize(
                        id=uid(),
                        size_id=ref["sizes"][size_name].id,
                        price=Decimal(price),
                        is_available=True,
                        is_default=size_name == "330 мл",
                    )
                    for size_name, price in zip(drink_size_names, prices)
                ],
            )
        )

    desserts = [
        ("Сырники", "cheesecakes", "Нежные сырники", "279.00"),
        ("Фондан", "fondant", "Шоколадный фондан", "299.00"),
    ]
    for name, slug, description, price in desserts:
        products.append(
            Product(
                id=uid(),
                category_id=desserts_cat,
                name=name,
                slug=slug,
                description=description,
                base_price=Decimal(price),
                is_active=True,
                is_available=True,
                sizes=[
                    ProductSize(
                        id=uid(),
                        size_id=ref["sizes"]["Стандарт"].id,
                        price=Decimal(price),
                        is_available=True,
                        is_default=True,
                    )
                ],
            )
        )

    sauces = [
        ("Сырный соус", "cheese-sauce-dip", "70.00"),
        ("Чесночный соус", "garlic-sauce-dip", "70.00"),
        ("Соус барбекю", "bbq-sauce-dip", "70.00"),
        ("Соус ранч", "ranch-sauce-dip", "70.00"),
    ]
    for name, slug, price in sauces:
        products.append(
            Product(
                id=uid(),
                category_id=sauces_cat,
                name=name,
                slug=slug,
                description=f"Порция соуса «{name}»",
                base_price=Decimal(price),
                is_active=True,
                is_available=True,
                sizes=[
                    ProductSize(
                        id=uid(),
                        size_id=ref["sizes"]["Стандарт"].id,
                        price=Decimal(price),
                        is_available=True,
                        is_default=True,
                    )
                ],
            )
        )

    session.add_all(products)
    await session.flush()


async def seed_roles_and_promocodes(session: AsyncSession) -> None:
    existing_roles = (await session.scalars(select(Role))).all()
    if not existing_roles:
        session.add_all(
            [
                Role(id=uid(), name="admin", description="Администратор", is_active=True),
                Role(id=uid(), name="customer", description="Клиент", is_active=True),
                Role(id=uid(), name="courier", description="Курьер", is_active=True),
            ]
        )

    existing_promos = (await session.scalars(select(Promocode))).all()
    if not existing_promos:
        now = datetime.now()
        session.add_all(
            [
                Promocode(
                    id=uid(),
                    code="WELCOME10",
                    discount_type="percent",
                    discount_value=Decimal("10.00"),
                    min_order_amount=Decimal("500.00"),
                    max_discount_amount=Decimal("300.00"),
                    is_active=True,
                    usage_count=0,
                    usage_limit=1000,
                    starts_at=now,
                    expires_at=now + timedelta(days=365),
                ),
                Promocode(
                    id=uid(),
                    code="PIZZA150",
                    discount_type="fixed",
                    discount_value=Decimal("150.00"),
                    min_order_amount=Decimal("1000.00"),
                    max_discount_amount=Decimal("150.00"),
                    is_active=True,
                    usage_count=0,
                    usage_limit=500,
                    starts_at=now,
                    expires_at=now + timedelta(days=180),
                ),
            ]
        )


async def print_summary(session: AsyncSession) -> None:
    rows = (
        await session.execute(
            text(
                """
                SELECT 'categories' AS t, count(*) FROM categories
                UNION ALL SELECT 'sizes', count(*) FROM sizes
                UNION ALL SELECT 'dough_types', count(*) FROM dough_types
                UNION ALL SELECT 'ingredients', count(*) FROM ingredients
                UNION ALL SELECT 'products', count(*) FROM products
                UNION ALL SELECT 'product_sizes', count(*) FROM product_sizes
                UNION ALL SELECT 'product_sizes_with_image', count(*) FROM product_sizes WHERE image_url IS NOT NULL
                UNION ALL SELECT 'product_doughs', count(*) FROM product_doughs
                UNION ALL SELECT 'product_ingredients', count(*) FROM product_ingredients
                UNION ALL SELECT 'product_addons', count(*) FROM product_addons
                UNION ALL SELECT 'roles', count(*) FROM roles
                UNION ALL SELECT 'promocodes', count(*) FROM promocodes
                ORDER BY 1
                """
            )
        )
    ).all()
    print("Seed complete:")
    for name, count in rows:
        print(f"  {name}: {count}")


async def main() -> None:
    async with SessionLocal() as session:
        try:
            await clear_catalog(session)
            ref = await seed_reference(session)
            await seed_products(session, ref)
            await seed_roles_and_promocodes(session)
            await session.commit()
            await print_summary(session)
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
