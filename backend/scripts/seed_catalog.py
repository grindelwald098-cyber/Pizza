"""Очистка и заполнение каталога реалистичными данными пиццерии."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select, text

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


def uid() -> uuid.UUID:
    return uuid.uuid4()


def clear_catalog(session) -> None:
    session.execute(delete(ProductAddon))
    session.execute(delete(ProductIngredient))
    session.execute(delete(ProductDough))
    session.execute(delete(ProductSize))
    session.execute(delete(Product))
    session.execute(delete(Category))
    session.execute(delete(Size))
    # ингредиенты и типы теста пересоздаём тоже, чтобы цены/названия были консистентными
    session.execute(delete(Ingredient))
    session.execute(delete(DoughType))
    session.commit()


def seed_reference(session) -> dict:
    categories = [
        Category(
            id=uid(),
            name="Пицца",
            slug="pizza",
            description="Классические и фирменные пиццы на выбор",
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
        DoughType(id=uid(), name="Пышное", sort_order=3, is_active=True),
    ]
    session.add_all(dough_types)

    ingredient_rows = [
        ("Томатный соус", "Классический томатный соус", "70.00"),
        ("Сливочный соус", "Нежный сливочный соус", "90.00"),
        ("Соус BBQ", "Копчёный барбекю-соус", "80.00"),
        ("Соус Цезарь", "Сливочный соус Цезарь", "80.00"),
        ("Моцарелла", "Свежая моцарелла", "120.00"),
        ("Пармезан", "Тёртый пармезан", "150.00"),
        ("Чеддер", "Выдержанный чеддер", "130.00"),
        ("Горгонзола", "Пикантная голубая горгонзола", "180.00"),
        ("Пепперони", "Острая колбаса пепперони", "170.00"),
        ("Салями", "Классическая салями", "160.00"),
        ("Ветчина", "Копчёная ветчина", "140.00"),
        ("Бекон", "Хрустящий бекон", "160.00"),
        ("Говядина", "Тушёная говядина", "190.00"),
        ("Куриное филе", "Сочное куриное филе", "150.00"),
        ("Шампиньоны", "Свежие шампиньоны", "90.00"),
        ("Помидоры", "Свежие помидоры", "80.00"),
        ("Болгарский перец", "Сладкий перец", "80.00"),
        ("Красный лук", "Маринованный красный лук", "60.00"),
        ("Маслины", "Чёрные маслины", "90.00"),
        ("Кукуруза", "Сладкая кукуруза", "70.00"),
        ("Ананасы", "Консервированные ананасы", "100.00"),
        ("Халапеньо", "Острый перец халапеньо", "70.00"),
        ("Чеснок", "Свежий чеснок", "50.00"),
        ("Базилик", "Свежий базилик", "60.00"),
        ("Руккола", "Свежая руккола", "80.00"),
        ("Орегано", "Сушёный орегано", "40.00"),
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
    session.flush()

    return {
        "categories": {c.slug: c for c in categories},
        "sizes": {s.name: s for s in sizes},
        "doughs": {d.name: d for d in dough_types},
        "ingredients": {i.name: i for i in ingredients},
    }


def pizza_sizes(ref: dict, small: str, medium: str, large: str) -> list[ProductSize]:
    return [
        ProductSize(
            id=uid(),
            size_id=ref["sizes"]["Маленькая"].id,
            price=Decimal(small),
            is_available=True,
        ),
        ProductSize(
            id=uid(),
            size_id=ref["sizes"]["Средняя"].id,
            price=Decimal(medium),
            is_available=True,
        ),
        ProductSize(
            id=uid(),
            size_id=ref["sizes"]["Большая"].id,
            price=Decimal(large),
            is_available=True,
        ),
    ]


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
        ProductDough(
            id=uid(),
            dough_type_id=ref["doughs"]["Пышное"].id,
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
    addons = []
    for name in names:
        ing = ref["ingredients"][name]
        addons.append(
            ProductAddon(
                id=uid(),
                ingredient_id=ing.id,
                is_available=True,
                additional_price=ing.price,
            )
        )
    return addons


def seed_products(session, ref: dict) -> None:
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
        "Ананасы",
        "Маслины",
        "Пармезан",
    ]

    pizzas = [
        {
            "name": "Маргарита",
            "slug": "margherita",
            "description": "Томатный соус, моцарелла, свежие помидоры и базилик",
            "base": "449.00",
            "prices": ("449.00", "599.00", "749.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Базилик", "1.00", True),
            ],
        },
        {
            "name": "Пепперони",
            "slug": "pepperoni",
            "description": "Томатный соус, моцарелла и много пепперони",
            "base": "549.00",
            "prices": ("549.00", "699.00", "849.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Пепперони", "1.00", True),
            ],
        },
        {
            "name": "Четыре сыра",
            "slug": "quatro-formaggi",
            "description": "Сливочный соус, моцарелла, пармезан, чеддер и горгонзола",
            "base": "599.00",
            "prices": ("599.00", "749.00", "899.00"),
            "ingredients": [
                ("Сливочный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Пармезан", "1.00", True),
                ("Чеддер", "1.00", True),
                ("Горгонзола", "1.00", True),
            ],
        },
        {
            "name": "Гавайская",
            "slug": "hawaiian",
            "description": "Томатный соус, моцарелла, ветчина и ананасы",
            "base": "529.00",
            "prices": ("529.00", "679.00", "829.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Ветчина", "1.00", True),
                ("Ананасы", "1.00", True),
            ],
        },
        {
            "name": "Мясная",
            "slug": "meat",
            "description": "Томатный соус, моцарелла, пепперони, бекон, говядина и ветчина",
            "base": "649.00",
            "prices": ("649.00", "799.00", "949.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Пепперони", "1.00", True),
                ("Бекон", "1.00", True),
                ("Говядина", "1.00", True),
                ("Ветчина", "1.00", True),
            ],
        },
        {
            "name": "Грибная",
            "slug": "mushroom",
            "description": "Сливочный соус, моцарелла и шампиньоны",
            "base": "499.00",
            "prices": ("499.00", "649.00", "799.00"),
            "ingredients": [
                ("Сливочный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Шампиньоны", "1.00", True),
            ],
        },
        {
            "name": "BBQ Курица",
            "slug": "bbq-chicken",
            "description": "Соус BBQ, моцарелла, курица, красный лук и кукуруза",
            "base": "579.00",
            "prices": ("579.00", "729.00", "879.00"),
            "ingredients": [
                ("Соус BBQ", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Куриное филе", "1.00", True),
                ("Красный лук", "1.00", True),
                ("Кукуруза", "1.00", True),
            ],
        },
        {
            "name": "Цезарь",
            "slug": "caesar",
            "description": "Соус Цезарь, моцарелла, курица, помидоры и пармезан",
            "base": "589.00",
            "prices": ("589.00", "739.00", "889.00"),
            "ingredients": [
                ("Соус Цезарь", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Куриное филе", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Пармезан", "1.00", True),
            ],
        },
        {
            "name": "Диабло",
            "slug": "diablo",
            "description": "Томатный соус, моцарелла, салями, халапеньо и чеснок",
            "base": "569.00",
            "prices": ("569.00", "719.00", "869.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Салями", "1.00", True),
                ("Халапеньо", "1.00", True),
                ("Чеснок", "1.00", True),
            ],
        },
        {
            "name": "Вегетарианская",
            "slug": "vegetarian",
            "description": "Томатный соус, моцарелла, овощи и маслины",
            "base": "519.00",
            "prices": ("519.00", "669.00", "819.00"),
            "ingredients": [
                ("Томатный соус", "1.00", True),
                ("Моцарелла", "1.00", True),
                ("Болгарский перец", "1.00", True),
                ("Шампиньоны", "1.00", True),
                ("Помидоры", "1.00", True),
                ("Кукуруза", "1.00", True),
                ("Маслины", "1.00", True),
            ],
        },
    ]

    products: list[Product] = []
    for item in pizzas:
        products.append(
            Product(
                id=uid(),
                category_id=pizza_cat,
                name=item["name"],
                slug=item["slug"],
                description=item["description"],
                image_url=None,
                base_price=Decimal(item["base"]),
                is_active=True,
                is_available=True,
                sizes=pizza_sizes(ref, *item["prices"]),
                doughs=pizza_doughs(ref),
                ingredients=make_ingredients(ref, item["ingredients"]),
                addons=make_addons(ref, common_addons),
            )
        )

    snacks = [
        ("Картофель фри", "fries", "Хрустящий картофель фри", "199.00"),
        ("Наггетсы", "nuggets", "Куриные наггетсы, 9 шт.", "249.00"),
        ("Чесночные палочки", "garlic-breadsticks", "Сырные палочки с чесноком", "229.00"),
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
                    )
                ],
            )
        )

    drinks = [
        ("Кола", "cola", "Классическая кола", ("99.00", "129.00", "179.00")),
        ("Апельсиновый сок", "orange-juice", "Свежий апельсиновый сок", ("119.00", "149.00", "199.00")),
        ("Вода негазированная", "still-water", "Питьевая вода без газа", ("69.00", "89.00", "119.00")),
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
                    )
                    for size_name, price in zip(drink_size_names, prices)
                ],
            )
        )

    desserts = [
        ("Тирамису", "tiramisu", "Классический тирамису", "279.00"),
        ("Чизкейк", "cheesecake", "Нью-йоркский чизкейк", "299.00"),
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
                    )
                ],
            )
        )

    sauces = [
        ("Томатный соус", "tomato-sauce-dip", "70.00"),
        ("Сливочный соус", "cream-sauce-dip", "80.00"),
        ("Соус BBQ", "bbq-sauce-dip", "80.00"),
        ("Соус Цезарь", "caesar-sauce-dip", "80.00"),
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
                    )
                ],
            )
        )

    session.add_all(products)
    session.flush()


def seed_roles_and_promocodes(session) -> None:
    existing_roles = session.scalars(select(Role)).all()
    if not existing_roles:
        session.add_all(
            [
                Role(id=uid(), name="admin", description="Администратор", is_active=True),
                Role(id=uid(), name="customer", description="Клиент", is_active=True),
                Role(id=uid(), name="courier", description="Курьер", is_active=True),
            ]
        )

    existing_promos = session.scalars(select(Promocode)).all()
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


def print_summary(session) -> None:
    rows = session.execute(
        text(
            """
            SELECT 'categories' AS t, count(*) FROM categories
            UNION ALL SELECT 'sizes', count(*) FROM sizes
            UNION ALL SELECT 'dough_types', count(*) FROM dough_types
            UNION ALL SELECT 'ingredients', count(*) FROM ingredients
            UNION ALL SELECT 'products', count(*) FROM products
            UNION ALL SELECT 'product_sizes', count(*) FROM product_sizes
            UNION ALL SELECT 'product_doughs', count(*) FROM product_doughs
            UNION ALL SELECT 'product_ingredients', count(*) FROM product_ingredients
            UNION ALL SELECT 'product_addons', count(*) FROM product_addons
            UNION ALL SELECT 'roles', count(*) FROM roles
            UNION ALL SELECT 'promocodes', count(*) FROM promocodes
            ORDER BY 1
            """
        )
    ).all()
    print("Seed complete:")
    for name, count in rows:
        print(f"  {name}: {count}")


def main() -> None:
    session = SessionLocal()
    try:
        clear_catalog(session)
        ref = seed_reference(session)
        seed_products(session, ref)
        seed_roles_and_promocodes(session)
        session.commit()
        print_summary(session)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
