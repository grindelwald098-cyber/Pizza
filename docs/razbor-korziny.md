# Разбор корзины и продукта

Заметки по текущему коду: что работает, почему кажется кастыльным, где лишние запросы.
Это не план правок и не TODO — чтобы прочитать и самому решить, что трогать.

Как исправлять (правила и абстрактные примеры): `docs/rukovodstvo.md`.

Файлы, о которых речь:

- `backend/app/repositories/cart_item.py`
- `backend/app/repositories/cart.py`
- `backend/app/repositories/product.py`
- `backend/app/repositories/ingredients.py`
- `backend/app/services/product/mapper.py`
- `backend/app/services/product/services.py`
- `backend/app/services/product/pricing.py`
- `backend/app/services/cart.py`
- `backend/app/schemas/cart.py`
- `backend/app/schemas/product.py`

---

## 1. Главная проблема: одна карточка товара для каталога и для корзины

`ProductResponse` задуман как ответ **каталога**: все размеры, все теста, состав пиццы.

В корзине нужна **другая** сущность: строка заказа — выбранный размер, выбранное тесто, допы, количество, цена.

Сейчас корзина притворяется каталогом. См. `to_cart_response`:

```python
# backend/app/services/cart.py

def to_cart_response(cart: Cart) -> CartResponse:
    return CartResponse(
        id=cart.id,
        products=[
            CartItemSchema(
                product=to_product_response(
                    item.product,
                    item.size_id,
                    item.dough_type_id,
                    added_extras=list(item.added_ingredients),
                ),
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in cart.items
        ],
        ...
    )
```

А `to_product_response` из-за этого умеет «обрезать» продукт:

```python
# backend/app/services/product/mapper.py

def to_product_response(
    product: Product,
    size_id: UUID | None = None,
    dough_type_id: UUID | None = None,
    added_extras: list[CartItemAddedIngredient] | None = None,
) -> ProductResponse:
    # size/dough — фильтр конфигурации; extras НЕ из product.ingredients.
    sizes = product.sizes
    if size_id is not None:
        sizes = [item for item in product.sizes if item.size_id == size_id]

    doughs = product.doughs
    if dough_type_id is not None:
        doughs = [item for item in product.doughs if item.dough_type_id == dough_type_id]

    if added_extras is not None:
        ingredients = [to_cart_extra_response(extra) for extra in added_extras]
    else:
        ingredients = [
            to_product_ingredient_response(ingredient)
            for ingredient in product.ingredients
        ]
```

Итог: одно и то же поле `ingredients` значит разное.

| Где     | Что лежит в `ingredients`                          |
| ------- | -------------------------------------------------- |
| Каталог | рецепт продукта (`product.ingredients`)            |
| Корзина | дополнительные ингредиенты (`cart_item.added_ingredients`) |

Маппер знает про корзину (`added_extras`, фильтры size/dough). Корзина знает, что продукт надо обрезать. Схема при этом одна — `ProductResponse` в `backend/app/schemas/product.py`.

Отсюда ощущение «всё сложно»: сложность не в пицце, а в том, что две задачи засунуты в одну форму.

### Как выглядело бы проще по смыслу

Каталог отдаёт полный `ProductResponse` как есть.

Корзина отдаёт свою схему, без фильтрации списков внутри продукта:

```python
# пример целевой формы, не текущий код
class CartLineResponse(BaseModel):
    product_id: UUID
    name: str
    image_url: str | None
    size: ProductSizeResponse | None
    dough: DoughTypeResponse | None
    extras: list[ProductIngredientResponse]
    quantity: int
    unit_price: Decimal
```

Тогда у `to_product_response` пропадут `size_id` / `dough_type_id` / `added_extras`, и половина магии в маппере исчезнет.

---

## 2. Лишние запросы в `add_product_to_cart`

Файл: `backend/app/services/cart.py`, метод `CartService.add_product_to_cart`.

Типичный путь «добавить пиццу в корзину» сейчас такой:

1. Загрузить **всю корзину** со всем графом продукта — `get_cart_by_principal`.
2. Отдельно загрузить **тот же продукт** ещё раз — `product_repository.get_by_id`.
3. Для **каждого** допа — отдельный `get_by_id` в цикле (`_build_added_ingredients`).
4. Отдельно поискать совпадающую позицию — `find_matching`, хотя `cart.items` уже загружены.
5. `commit` внутри репозитория.
6. Загрузить **всю корзину ещё раз** — `cart_repository.get_by_id`, чтобы собрать ответ.

Сам метод:

```python
# backend/app/services/cart.py

async def add_product_to_cart(...):
    cart = await self.get_cart_by_principal(principal)   # 1. вся корзина
    cart_id = cart.id

    product = await self.product_repository.get_by_id(product_id)  # 2. продукт ещё раз
    ...
    added_ingredients = await self._build_added_ingredients(...)   # 3. N запросов
    ...
    existing = await self.cart_item_repository.find_matching(...)  # 4. ещё SELECT

    if existing is not None:
        ...
        await self.cart_item_repository.update(existing)  # 5. commit
    else:
        ...
        await self.cart_item_repository.add(cart_item)    # 5. commit

    reloaded = await self.cart_repository.get_by_id(cart_id)  # 6. корзина ещё раз
    return to_cart_response(reloaded)
```

Пункты 2, 4 и 6 часто не нужны. Корзина уже в памяти, продукт для ответа всё равно придёт из `cart.items`, совпадение можно искать в `cart.items`.

### N+1 по допам

```python
# backend/app/services/cart.py

async def _build_added_ingredients(
    self,
    extra_ingredient_ids: list[UUID],
) -> list[CartItemAddedIngredient]:
    added: list[CartItemAddedIngredient] = []
    for ingredient_id in dict.fromkeys(extra_ingredient_ids):
        ingredient = await self.ingredient_repository.get_by_id(ingredient_id)
        ...
```

3 допа = 3 запроса в БД. В `IngredientsRepository` уже есть `get_existing_ids` с `WHERE id IN (...)` — тот же приём можно использовать, чтобы загрузить сами ингредиенты одним запросом.

```python
# backend/app/repositories/ingredients.py — уже умеет пачкой, но только id

async def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
    query = select(Ingredient.id).where(Ingredient.id.in_(ids))
```

### `find_matching` поверх уже загруженной корзины

```python
# backend/app/repositories/cart_item.py

async def find_matching(
    self,
    cart_id: UUID,
    product_id: UUID,
    size_id: UUID | None,
    dough_type_id: UUID | None,
    extra_ingredient_ids: list[UUID],
) -> CartItem | None:
    query = (
        select(CartItem)
        .where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
            CartItem.size_id == size_id,
            CartItem.dough_type_id == dough_type_id,
        )
        .options(selectinload(CartItem.added_ingredients))
    )
    items = list[Any](await self.session.scalars(query))
    wanted = set[UUID](extra_ingredient_ids)
    for item in items:
        current = {extra.ingredient_id for extra in item.added_ingredients}
        if current == wanted:
            return item
    return None
```

Это не ошибка SQLAlchemy. Это повтор той же работы: сервис только что загрузил `cart.items`, но не смотрит на них, а идёт в БД ещё раз и в Python сравнивает множества id.

Сравнение множеств для пет-проекта нормальное. Каст в том, что оно сделано **вторым запросом**.

Ещё мелочь: `list[Any](...)` — костыль типизации, не логики.

---

## 3. Тяжёлая загрузка «на всякий случай»

Для **каждой** позиции корзины подтягивается почти весь продукт: категория, все размеры, все теста, весь рецепт.

```python
# backend/app/repositories/cart.py

@staticmethod
def _load_options():
    # selectinload = заранее подтянуть связи отдельным SELECT IN (...),
    # чтобы потом не было lazy-load и MissingGreenlet в async.
    return (
        selectinload(Cart.items)
        .selectinload(CartItem.added_ingredients)
        .selectinload(CartItemAddedIngredient.ingredient),
        selectinload(Cart.items)
        .selectinload(CartItem.product)
        .options(*ProductRepository._load_options()),
    )
```

А `_load_options` продукта — это полный граф меню:

```python
# backend/app/repositories/product.py

@staticmethod
def _load_options():
    return (
        selectinload(Product.category),
        selectinload(Product.sizes).selectinload(ProductSize.size),
        selectinload(Product.doughs).selectinload(ProductDough.dough_type),
        selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient),
    )
```

Потом маппер почти всё выкидывает и оставляет 1 размер, 1 тесто и допы. Грузим карточку из меню, чтобы отдать строку корзины.

`selectinload` сам по себе правильный приём для async SQLAlchemy. Без него ORM полезет в ленивые связи и упадёт с `MissingGreenlet`. Проблема не в `selectinload`, а в **глубине**: для корзины нужен снимок позиции, а грузится весь продукт.

Тот же симптом в создании продукта: сохранить голую сущность, потом отдельно догрузить дерево, потому что `refresh` связи не подтягивает.

```python
# backend/app/services/product/services.py

created = await self.repository.create(product)
loaded = await self.repository.get_by_id(created.id)

if not loaded:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Product was created but could not be loaded",
    )

return to_product_response(loaded)
```

---

## 4. Репозитории коммитят слишком рано

Почти каждый `add` / `update` / `create` сразу делает `commit()`.

```python
# backend/app/repositories/cart_item.py

async def add(self, cart_item: CartItem) -> CartItem:
    self.session.add(cart_item)
    await self.session.commit()
    await self.session.refresh(cart_item)
    return cart_item

async def update(self, cart_item: CartItem) -> CartItem:
    self.session.add(cart_item)
    await self.session.commit()
    await self.session.refresh(cart_item)
    return cart_item
```

`add` и `update` ещё и одинаковые — это не баг, просто шум.

Из-за раннего commit сервис не может собрать одну операцию:

> найти или создать позицию → дописать допы → посчитать цену → один commit → вернуть то, что уже в памяти

Вместо этого: сохранить кусок → перечитать весь мир. Второй `get_by_id` корзины как раз отсюда.

В FastAPI сессия обычно живёт на весь запрос. Репозиторий может делать `add` / `flush`, а `commit` — один раз в конце (в зависимости сессии или в сервисе). Тогда не нужно «сохранить и заново прочитать».

---

## 5. Цена и валидация почти есть, но ошибки глотаются

```python
# backend/app/services/product/pricing.py

def calculate_unit_price(
    product: Product,
    size_id: UUID | None,
    extra_prices: list[Decimal] | None = None,
) -> Decimal:
    unit_price = product.base_price

    if size_id is not None:
        product_size = next(
            (item for item in product.sizes if item.size_id == size_id and item.is_available),
            None,
        )
        if product_size is not None:
            unit_price = product_size.price

    for price in extra_prices or []:
        unit_price += price

    return unit_price
```

Если `size_id` не найден или размер недоступен — тихо берётся `base_price`. Тесто на цену не влияет (возможно, так и задумано).

Допы суммируются с глобальной таблицы `ingredients`, а не с допов **этого** продукта:

```python
# backend/app/services/cart.py

ingredient = await self.ingredient_repository.get_by_id(ingredient_id)
if ingredient is None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Ingredient {ingredient_id} is not available for this product",
    )
```

Текст ошибки: «недоступен для этого продукта». Проверка только: ингредиент вообще существует в мире.

У `Product` при этом есть связь `addons` — в этом флоу она не используется:

```python
# backend/app/database/models/product.py

addons: Mapped[list["ProductAddon"]] = relationship("ProductAddon", back_populates="product")
```

Бизнес-правило «можно ли добавить пепперони на эту пиццу» в коде не живёт, только звучит в сообщении.

---

## 6. `ProductService`: вложенные циклы вместо словаря

Это не про лишние запросы в БД, а про читаемость. Идея простая: синхронизировать список (пропало → выключить, было → обновить, новое → добавить). Сейчас это циклы внутри циклов.

```python
# backend/app/services/product/services.py — update_sizes_to_product

for size in data:
    if size.size_id in current_ids:
        for product_size in product_sizes:
            if product_size.size_id == size.size_id:
                product_size.price = size.price
                product_size.is_available = True
                break
    else:
        product_sizes.append(...)
```

То же в `update_ingredients_to_product`. Обычно делают так:

```python
# пример проще, не текущий код
current = {row.size_id: row for row in product.sizes}

for size in data:
    row = current.get(size.size_id)
    if row is None:
        product.sizes.append(ProductSize(...))
    else:
        row.price = size.price
        row.is_available = True
```

На прод почти не влияет, читать легче.

---

## 7. Что упрощать в первую очередь (когда дойдёшь до правок)

Не надо делать всё сразу. По смыслу порядок такой:

1. **Развести DTO.** Каталог = полный продукт. Корзина = позиция заказа. Маппер перестанет фильтровать продукт «под корзину».
2. **Один проход в `add_product_to_cart`.** Корзина уже загружена → совпадение искать в `cart.items` → ингредиенты одним `IN (...)` → менять объект в памяти → один `commit` → ответ из того же объекта, без повторного `get_by_id`.
3. **Грузить для корзины только нужное.** Не весь рецепт и не все размеры, а выбранный size/dough + допы + поля для карточки в UI.
4. **Не коммитить в каждом методе репозитория.** `add` / `flush` в репозитории, один `commit` в конце запроса.
5. **Явно валидировать конфигурацию.** Нет размера / тесто не для этой пиццы / доп не из addons → 400. Сейчас часть ошибок маскируется `base_price`.

---

## 8. Что не надо упрощать в ноль

- `selectinload` в async — правильная штука, без него SQLAlchemy полезет в ленивые связи и упадёт.
- Снимок цены допа в `cart_item_added_ingredients.price` — нормально: цена в меню может измениться, в корзине должна остаться той, что была при добавлении.
- Разделение repository / service — ок для роста. Сложность не в слоях, а в том, что слои делают лишнюю работу и делят одну DTO на два смысла.

---

## Короткий вывод

Каст не в Python и не в SQLAlchemy. Каст в модели ответа: **корзина рисуется как обрезанный продукт каталога**.

Из этого следуют:

- фильтры в `mapper.py`;
- жирный eager-load через `ProductRepository._load_options()` внутри корзины;
- повторные запросы в `add_product_to_cart`;
- «догрузить всё, чтобы отдать чуть-чуть».

Если развести «товар в меню» и «строка корзины», код станет короче почти сам: меньше параметров у маппера, меньше JOIN’ов, меньше походов в БД.
