# Руководство: как упростить бэкенд

Это не разбор твоего текущего кода. Разбор лежит в `docs/razbor-korziny.md`.

Здесь — **правила и абстрактные примеры**. Их можно перенести на любой магазин: пицца, одежда, билеты. Цель: прочитать, понять паттерн, потом самому поправить проект.

Каждый раздел устроен так:

1. зачем правило;
2. как обычно ломается;
3. абстрактный пример «было / стало»;
4. как это звучит в твоём проекте одной фразой.

---

## Оглавление

1. [Две разные сущности: товар в меню и строка корзины](#1-две-разные-сущности)
2. [Кто за что отвечает: api / service / repository / mapper](#2-кто-за-что-отвечает)
3. [Один HTTP-запрос = одна транзакция](#3-один-http-запрос--одна-транзакция)
4. [Не спрашивай БД о том, что уже в памяти](#4-не-спрашивай-бд-о-том-что-уже-в-памяти)
5. [N+1: грузи пачкой, не в цикле](#5-n1-грузи-пачкой)
6. [Грузи только то, что отдаёшь](#6-грузи-только-то-что-отдаёшь)
7. [Маппер копирует, а не «подгоняет под другой экран»](#7-маппер-копирует)
8. [Валидация говорит «нет», а не подставляет запасной вариант](#8-валидация-говорит-нет)
9. [Слияние списков через словарь, не через цикл в цикле](#9-слияние-списков)
10. [Целевой флоу «добавить в корзину»](#10-целевой-флоу)
11. [Чеклист](#11-чеклист)

---

## 1. Две разные сущности

### Зачем

В голове это кажется одним и тем же: «пицца». В API это **две разные правды**.

| Сущность | Вопрос, на который она отвечает |
| --- | --- |
| Товар в каталоге | Что вообще можно купить? Какие размеры, теста, состав? |
| Строка корзины | Что человек **уже выбрал**? Сколько штук? По какой цене? |

Если отдать в корзину ту же форму, что и в каталог, придётся врать: выкидывать лишние размеры, подменять состав на допы, прятать поля.

### Как ломается

Одна схема `ProductResponse` используется везде. Чтобы корзина выглядела «почти как продукт», в маппер добавляют флаги: «оставь только этот размер», «ingredients на самом деле допы».

Поле начинает значить разное в разных экранах. Фронт и бэкенд начинают угадывать.

### Было (абстрактно)

```python
class ProductOut(BaseModel):
    id: UUID
    name: str
    sizes: list[SizeOut]          # в каталоге — все, в корзине — один
    ingredients: list[IngredientOut]  # в каталоге — рецепт, в корзине — допы


def to_product_out(product, size_id=None, extras=None):
    sizes = product.sizes
    if size_id is not None:
        sizes = [s for s in product.sizes if s.id == size_id]

    if extras is not None:
        ingredients = extras
    else:
        ingredients = product.recipe

    return ProductOut(id=product.id, name=product.name, sizes=sizes, ingredients=ingredients)
```

Это работает. Это каст: одна функция обслуживает два смысла.

### Стало (абстрактно)

```python
class CatalogProductOut(BaseModel):
    id: UUID
    name: str
    sizes: list[SizeOut]              # все доступные
    doughs: list[DoughOut]            # все доступные
    recipe: list[IngredientOut]       # состав
    addons: list[AddonOut]            # что можно добавить сверху


class CartLineOut(BaseModel):
    product_id: UUID
    name: str
    image_url: str | None
    size: SizeOut | None              # уже выбранный
    dough: DoughOut | None            # уже выбранное
    extras: list[AddonOut]            # уже выбранные допы
    quantity: int
    unit_price: Decimal


class CartOut(BaseModel):
    id: UUID
    items: list[CartLineOut]
```

Каталог больше не знает про корзину. Корзина больше не обрезает каталог.

Мапперы становятся тупыми и короткими:

```python
def to_catalog_product(product) -> CatalogProductOut:
    return CatalogProductOut(
        id=product.id,
        name=product.name,
        sizes=[to_size(s) for s in product.sizes],
        doughs=[to_dough(d) for d in product.doughs],
        recipe=[to_ingredient(i) for i in product.ingredients],
        addons=[to_addon(a) for a in product.addons],
    )


def to_cart_line(item) -> CartLineOut:
    return CartLineOut(
        product_id=item.product_id,
        name=item.product.name,
        image_url=item.product.image_url,
        size=to_size(item.size) if item.size else None,
        dough=to_dough(item.dough_type) if item.dough_type else None,
        extras=[to_extra(e) for e in item.added_ingredients],
        quantity=item.quantity,
        unit_price=item.unit_price,
    )
```

Нет `if extras is not None`. Нет фильтра «оставь один размер».

### У тебя

Сейчас `ProductResponse` + параметры `size_id` / `dough_type_id` / `added_extras` в `mapper.py` — это как раз «было». Корзине нужна своя схема, каталогу — своя.

Если боишься ломать фронт: сначала добавь новые поля рядом, потом переключи фронт, потом удали старую форму. Не обязательно менять контракт в один день.

---

## 2. Кто за что отвечает

Слои нужны не «по учебнику», а чтобы не дублировать работу.

| Слой | Делает | Не делает |
| --- | --- | --- |
| **API** (роутер) | Принять HTTP, отдать схему, код ошибки | Считать цену, писать SQL |
| **Service** | Сценарий: проверить, найти, создать, решить «та же позиция или новая» | Знать про `selectinload` |
| **Repository** | Достать / сохранить объекты | `commit()` на каждую мелочь, собирать JSON для фронта |
| **Mapper** | Объект БД → ответ API | Решать, какой размер «выбран», ходить в БД |
| **Pricing / validation** | Чистые функции: цена, «можно ли такую конфигурацию» | Сами писать в БД |

Абстрактный скелет запроса:

```text
HTTP POST /cart/items
        ↓
   CartService.add(...)
        ↓
   repository: взять корзину
   repository: взять товар
   validation: размер/тесто/допы разрешены?
   pricing: посчитать цену
   память: найти такую же строку или создать
   session.commit() один раз
        ↓
   mapper: Cart → CartOut
        ↓
   JSON
```

Если mapper начинает фильтровать продукт «как в корзине» — слой уже смешался.
Если repository считает цену — слой смешался.
Если service делает `get_by_id` сразу после `add`, хотя объект уже в руках — слой не сломан, просто лишняя работа.

---

## 3. Один HTTP-запрос = одна транзакция

### Зачем

Один клик «добавить в корзину» — это одна история. Либо всё записалось, либо ничего. Не «позиция сохранилась, а допы нет».

В FastAPI сессия БД обычно живёт **на весь запрос**. Её дают через `Depends`. Значит, `commit` должен быть **в конце запроса**, а не внутри каждого `repository.add`.

### Как ломается

Репозиторий делает так:

```python
class ItemRepository:
    async def add(self, item):
        self.session.add(item)
        await self.session.commit()      # рано
        await self.session.refresh(item)
        return item
```

После этого сервис уже не может добавить ещё что-то в ту же транзакцию. Приходится:

1. сохранить кусок;
2. заново читать весь мир из БД, чтобы собрать ответ.

Если в середине упадёт второе действие — первая часть уже закоммичена. Откатить нельзя.

### Было

```python
# зависимость отдаёт сессию и в конце просто закрывает её
async def get_session():
    async with SessionLocal() as session:
        yield session   # commit никто не делает → репозитории коммитят сами


class CartRepo:
    async def add_item(self, item):
        self.session.add(item)
        await self.session.commit()
```

### Стало

Сессия коммитит один раз, если запрос дошёл до конца без исключения:

```python
async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

Репозиторий только кладёт объект в сессию. Если нужен `id` сразу (UUID часто уже есть с `default=uuid4`) — `flush`, не `commit`:

```python
class CartRepo:
    async def add_item(self, item):
        self.session.add(item)
        await self.session.flush()   # SQL ушёл, транзакция ещё открыта
        return item
```

Сервис после этого **не обязан** заново грузить корзину из БД. Он меняет объекты в памяти и в конце запроса `get_session` сам сделает `commit`.

### Важная ловушка именно у тебя

Сейчас `get_session` **не коммитит**. Поэтому репозитории коммитят сами — иначе при выходе из `async with` изменения откатились бы.

Если уберёшь `commit` из репозиториев, **обязательно** добавь `commit` в `get_session` (как в примере выше). Иначе «упростил» = «ничего не сохраняется».

Делай это парой: сначала сессия, потом репозитории. Не наоборот.

---

## 4. Не спрашивай БД о том, что уже в памяти

### Зачем

SQLAlchemy после `select` держит объекты в identity map. Если корзина уже загружена с `items`, эти `items` — те же строки, что в таблице. Второй `SELECT` тех же позиций ничего нового не даёт, только тратит время.

### Как ломается

```python
async def add_to_cart(self, cart_id, product_id, size_id, extras):
    cart = await self.carts.get_with_items(cart_id)          # items уже здесь

    product = await self.products.get(product_id)

    existing = await self.items.find_same(                   # тот же вопрос к БД
        cart_id, product_id, size_id, extras
    )
    if existing:
        existing.quantity += 1
        await self.items.update(existing)
    else:
        await self.items.add(...)

    cart = await self.carts.get_with_items(cart_id)          # третий раз
    return to_cart_out(cart)
```

Три поездки за одними данными.

### Стало

```python
def find_same_line(items, product_id, size_id, dough_id, extra_ids: set):
    for item in items:
        if item.product_id != product_id:
            continue
        if item.size_id != size_id or item.dough_type_id != dough_id:
            continue
        current = {e.ingredient_id for e in item.added_ingredients}
        if current == extra_ids:
            return item
    return None


async def add_to_cart(self, cart_id, product_id, size_id, dough_id, extra_ids, qty):
    cart = await self.carts.get_with_items(cart_id)
    product = await self.products.get(product_id)
    extras = await self.ingredients.get_many(extra_ids)   # один запрос, см. §5

    existing = find_same_line(cart.items, product_id, size_id, dough_id, set(extra_ids))
    if existing:
        existing.quantity += qty
        existing.unit_price = price
    else:
        cart.items.append(CartItem(
            product_id=product_id,
            size_id=size_id,
            dough_type_id=dough_id,
            quantity=qty,
            unit_price=price,
            added_ingredients=[...],
        ))

    return to_cart_out(cart)   # тот же объект, commit будет в конце запроса
```

`find_same_line` — обычная функция, не метод репозитория. Репозиторий уже принёс коллекцию.

Когда второй запрос **нужен**: если первую загрузку делали без `items`, или items могли измениться в другой транзакции и тебе важна свежесть. Для «добавить в свою корзину в одном запросе» — не нужен.

---

## 5. N+1: грузи пачкой

### Зачем

Цикл `for id in ids: get_by_id(id)` — это N поездок в БД. База умеет `WHERE id IN (...)`.

### Было

```python
added = []
for ingredient_id in extra_ids:
    ingredient = await repo.get_by_id(ingredient_id)   # 1 SQL на каждый id
    if ingredient is None:
        raise NotFound(ingredient_id)
    added.append(CartExtra(ingredient_id=ingredient.id, price=ingredient.price))
```

3 допа = 3 SELECT.

### Стало

```python
async def get_by_ids(self, ids: list[UUID]) -> list[Ingredient]:
    if not ids:
        return []
    unique = list(dict.fromkeys(ids))   # порядок сохранить, дубли убрать
    rows = await self.session.scalars(
        select(Ingredient).where(Ingredient.id.in_(unique))
    )
    return list(rows.all())


async def load_extras(self, extra_ids: list[UUID]) -> list[Ingredient]:
    unique = list(dict.fromkeys(extra_ids))
    found = await self.repo.get_by_ids(unique)
    by_id = {row.id: row for row in found}

    missing = [i for i in unique if i not in by_id]
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown extras: {missing}")

    return [by_id[i] for i in unique]   # тот же порядок, что прислал клиент
```

Один SELECT. Потом проверка «все ли нашлись» в Python — это дёшево.

Тот же приём для любых списков id: размеры, теста, пользователи.

Правило: **внутри `for` не должно быть `await repo.get_...`**. Если видишь — собирай id и грузи пачкой.

---

## 6. Грузи только то, что отдаёшь

### Зачем

В async SQLAlchemy нельзя потом лениво сходить в связь (`item.product.category.name`) — упадёт `MissingGreenlet`. Поэтому связи грузят заранее через `selectinload`.

Это правильно. Неправильно грузить **всё дерево меню**, чтобы показать одну строку корзины.

### Как ломается

```python
# загрузка «на всякий случай как в каталоге»
def product_options():
    return (
        selectinload(Product.category),
        selectinload(Product.sizes).selectinload(ProductSize.size),
        selectinload(Product.doughs).selectinload(ProductDough.dough_type),
        selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient),
        selectinload(Product.addons).selectinload(ProductAddon.ingredient),
    )


def cart_options():
    return (
        selectinload(Cart.items).selectinload(CartItem.product).options(*product_options()),
        selectinload(Cart.items).selectinload(CartItem.added_ingredients).selectinload(...),
    )
```

Для каталога это ок: экран правда показывает все размеры и состав.

Для корзины из этого нужна пара полей продукта + выбранный размер + выбранные допы. Остальное поехало в SQL и в Python зря, а потом ещё отфильтровалось в маппере.

### Стало: разные комплекты загрузки

```python
def catalog_product_options():
    return (
        selectinload(Product.category),
        selectinload(Product.sizes).selectinload(ProductSize.size),
        selectinload(Product.doughs).selectinload(ProductDough.dough_type),
        selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient),
        selectinload(Product.addons).selectinload(ProductAddon.ingredient),
    )


def cart_options():
    return (
        selectinload(Cart.items).selectinload(CartItem.product),  # имя, картинка, base_price
        selectinload(Cart.items).selectinload(CartItem.size),
        selectinload(Cart.items).selectinload(CartItem.dough_type),
        selectinload(Cart.items)
            .selectinload(CartItem.added_ingredients)
            .selectinload(CartItemAddedIngredient.ingredient),
    )
```

Каталог и корзина **не делят** один `_load_options`.

Правило: нарисуй JSON, который уходит клиенту. Грузи ровно поля, которые в этом JSON есть. Если поля нет в ответе — его не должно быть в `selectinload`.

Исключение: связи, нужные **сервису** для проверки (например, `product.sizes`, чтобы понять, что `size_id` законный). Их грузят в `get_product`, не обязательно тащить в каждую загрузку корзины.

Два разных метода нормальны:

```python
async def get_for_catalog(self, id) -> Product: ...
async def get_for_pricing(self, id) -> Product: ...   # sizes + addons, без рецепта
async def get_cart_with_lines(self, id) -> Cart: ...
```

Имена важнее «универсальной» функции на все случаи.

---

## 7. Маппер копирует

Маппер — переводчик. Вход: объект с уже выбранными связями. Выход: Pydantic-модель. Без `if` «мы сейчас в корзине или в каталоге?».

Плохой запах:

```python
def to_product(product, size_id=None, extras=None):
    if size_id is not None:      # знает про экран
        ...
    if extras is not None:       # знает про другой смысл поля
        ...
```

Хороший запах: две функции с разными именами, см. §1.

Ещё запах: маппер сам ходит в репозиторий. Тогда это уже сервис.

После `create` не обязательно делать второй `get_by_id`, если:

- нужные связи уже собраны в объекте до `add`, или
- ты сделал `refresh` с `attribute_names` / повторный load одним методом `get_for_catalog`.

Второй `get` после create — допустимый простой вариант, пока объектов мало. Это не каст, это плата за простоту. Каст начинается, когда так делают **на каждый add в корзину**.

---

## 8. Валидация говорит «нет»

### Зачем

Клиент может прислать:

- размер от другой пиццы;
- тесто, которого у товара нет;
- доп, который нельзя класть на этот товар;
- недоступный размер.

Если в этом случае подставить `base_price` и сохранить — в корзине окажется «как будто всё ок», а цена неправильная. Искать такой баг потом тяжело.

### Было

```python
def unit_price(product, size_id, extra_prices):
    price = product.base_price
    if size_id is not None:
        size = next((s for s in product.sizes if s.size_id == size_id and s.is_available), None)
        if size is not None:
            price = size.price
        # если size нет — молча base_price
    return price + sum(extra_prices)
```

И отдельно:

```python
ingredient = await ingredients.get_by_id(extra_id)
if ingredient is None:
    raise HTTPException(400, "not available for this product")
```

Сообщение про «этот продукт», проверка про «существует ли ингредиент в мире».

### Стало: сначала проверить, потом считать

Чистая функция без БД. Все нужные списки уже загружены на продукте.

```python
def ensure_configuration(product, size_id, dough_id, extra_ids: list[UUID]) -> None:
    if size_id is not None:
        allowed = {s.size_id for s in product.sizes if s.is_available}
        if size_id not in allowed:
            raise HTTPException(400, "This size is not available for this product")

    if dough_id is not None:
        allowed = {d.dough_type_id for d in product.doughs}
        if dough_id not in allowed:
            raise HTTPException(400, "This dough is not available for this product")

    allowed_extras = {a.ingredient_id for a in product.addons if a.is_available}
    unknown = [i for i in extra_ids if i not in allowed_extras]
    if unknown:
        raise HTTPException(400, f"Extras not allowed: {unknown}")


def unit_price(product, size_id, extras: list) -> Decimal:
    # сюда попадаем только после ensure_configuration
    if size_id is None:
        price = product.base_price
    else:
        size = next(s for s in product.sizes if s.size_id == size_id)
        price = size.price

    # цену допа лучше брать из addon этого продукта (additional_price),
    # а не из глобальной таблицы ingredients — у разных пицц наценка может быть разной
    addon_by_id = {a.ingredient_id: a for a in product.addons}
    for extra_id in extras:
        price += addon_by_id[extra_id].additional_price

    return price
```

Правило: текст ошибки = то, что реально проверили. Если проверяете «есть в таблице ingredients» — так и пишите. Если «можно на эту пиццу» — смотрите `product.addons`.

Снимок цены в строке корзины (`CartItem.unit_price`, `added_ingredients.price`) — правильная идея. Меню завтра подорожает, уже лежащая в корзине позиция не должна молча измениться. Считаете цену **в момент добавления**, сохраняете число.

---

## 9. Слияние списков

Типичная админ-задача: «вот новый список размеров товара». Нужно:

- чего не прислали — выключить (или удалить);
- что было — обновить;
- чего не было — создать.

### Было

```python
for incoming in data:
    if incoming.size_id in current_ids:
        for row in product.sizes:
            if row.size_id == incoming.size_id:
                row.price = incoming.price
                row.is_available = True
                break
    else:
        product.sizes.append(ProductSize(...))
```

Вложенный цикл. Работает за N×M, читать тяжело.

### Стало

```python
current = {row.size_id: row for row in product.sizes}
incoming_ids = {item.size_id for item in data}

for row in product.sizes:
    if row.size_id not in incoming_ids:
        row.is_available = False

for item in data:
    row = current.get(item.size_id)
    if row is None:
        product.sizes.append(ProductSize(
            size_id=item.size_id,
            price=item.price,
            is_available=True,
        ))
    else:
        row.price = item.price
        row.is_available = True
```

Один проход по старым, один по новым. Ищите в коде `for ... in ...` внутри такого же `for` с сравнением `id` — почти всегда это место для словаря.

То же для ингредиентов рецепта, тестов, допов.

---

## 10. Целевой флоу

Собери всё вместе. Абстрактный «добавить в корзину» после упрощения:

```python
class CartService:
    async def add_product(self, principal, product_id, payload) -> CartOut:
        cart = await self.carts.get_by_principal(principal)
        product = await self.products.get_for_pricing(product_id)
        if product is None:
            raise HTTPException(404, "Product not found")

        extra_ids = list(dict.fromkeys(payload.extra_ids))

        ensure_configuration(
            product,
            payload.size_id,
            payload.dough_id,
            extra_ids,
        )

        price = unit_price(product, payload.size_id, extra_ids)

        existing = find_same_line(
            cart.items,
            product_id,
            payload.size_id,
            payload.dough_id,
            set(extra_ids),
        )

        if existing:
            existing.quantity += payload.quantity
            existing.unit_price = price
        else:
            addon_by_id = {a.ingredient_id: a for a in product.addons}
            cart.items.append(CartItem(
                product_id=product_id,
                size_id=payload.size_id,
                dough_type_id=payload.dough_id,
                quantity=payload.quantity,
                unit_price=price,
                added_ingredients=[
                    CartExtra(
                        ingredient_id=eid,
                        price=addon_by_id[eid].additional_price,
                    )
                    for eid in extra_ids
                ],
            ))

        return to_cart_out(cart)
```

Считай запросы к БД:

1. корзина с позициями и допами;
2. продукт с размерами / тестом / addons.

Дальше — память и один `commit` в `get_session`. Нет цикла `get_by_id`. Нет `find_matching` в SQL. Нет повторного `get_cart`.

Каталог при этом живёт отдельно:

```python
async def get_product_page(self, product_id) -> CatalogProductOut:
    product = await self.products.get_for_catalog(product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return to_catalog_product(product)
```

Две загрузки, два маппера, ноль общих `if extras`.

---

## 11. Чеклист

Иди сверху вниз. Не надо делать всё за вечер.

- [ ] У корзины своя response-схема, у каталога — своя. В `ingredients` каталога больше не лежат допы корзины.
- [ ] `to_product_response` больше не принимает `size_id` / `dough_type_id` / `added_extras`.
- [ ] `get_session` делает `commit` в конце успешного запроса и `rollback` при ошибке.
- [ ] Репозитории не вызывают `commit`. Максимум `add` + `flush`.
- [ ] `add_product_to_cart` не перечитывает корзину после записи.
- [ ] Совпадение позиции ищется в `cart.items`, не вторым SQL.
- [ ] Нет `await get_by_id` внутри `for`.
- [ ] У каталога и корзины разные `selectinload`.
- [ ] Неизвестный размер / тесто / доп → 400, не молчаливый `base_price`.
- [ ] Текст ошибки совпадает с проверкой (`addons` продукта, а не «ингредиент существует»).
- [ ] Цена позиции считается в момент добавления и сохраняется снимком.
- [ ] Обновление списков размеров/ингредиентов идёт через словарь `id → строка`.

Если пункт не выполнен, в коде почти наверняка останется каст из `docs/razbor-korziny.md`.

---

## Мини-словарь

**DTO / schema / Response** — форма JSON для клиента. Не таблица БД.

**Eager load (`selectinload`)** — «подтяни связи сразу». Нужно в async. Не значит «подтяни вообще всё».

**N+1** — 1 запрос за списком + N запросов за каждой связанной сущностью. Лечится `IN (...)` или `selectinload`.

**Unit of Work** — одна транзакция на один сценарий (обычно на один HTTP-запрос).

**Снимок цены** — число, записанное в корзину/заказ в момент выбора. Дальше меню может меняться.

**Identity map** — SQLAlchemy помнит объекты сессии. Повторный SELECT той же строки часто не нужен, если она уже загружена.
