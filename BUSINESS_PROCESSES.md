# Бизнес-процессы и логика: клон Додо Пицца

Документ — **план работ**: что уже есть в проекте и какую бизнес-логику нужно реализовать, чтобы получить сервис в стиле [Додо Пицца](https://dodopizza.ru).

Опирается на схему БД в `backend/app/database/models/` и FastAPI-бэкенд (`backend/app/`).

---

## 0. Суть продукта (как Додо)

Клиент:

1. Смотрит меню (пицца, напитки, закуски…).
2. Собирает пиццу: размер → тесто → состав / допы.
3. Кладёт в корзину (можно без регистрации).
4. Логинится, указывает адрес или самовывоз, применяет промокод.
5. Оплачивает (онлайн или при получении).
6. Следит за статусами: принят → готовится → готов / в пути → доставлен.
7. В ЛК: история, адреса, избранное, отзывы, уведомления.

Сотрудники:

- **Админ** — каталог, цены, промо, роли.
- **Оператор** — заказы, помощь клиенту, смена статусов.
- **Кухня** — очередь заказов, готовка.
- **Курьер** — доставка.

---

## 1. Текущее состояние проекта

| Слой | Статус |
|------|--------|
| PostgreSQL + Alembic + Docker | Есть |
| Модели: каталог, юзеры, корзина (в т.ч. гостевая), заказы, оплата, RBAC, промо, отзывы, избранное, уведомления | Таблицы и ORM есть |
| Snapshot в `order_items` (имена/цены на момент покупки) | Есть |
| Seed статусов заказа (`new` … `cancelled`) | Есть в миграции |
| API каталога (`products`, `categories`, `ingredients`, `sizes`, `dough_types`) | Черновик, частично сломан |
| Auth, корзина, заказы, оплата, промо, отзывы, уведомления | **Логики нет** (только таблицы) |
| Frontend | **Нет** |
| Зоны доставки | **Не спроектированы** в БД |

**Вывод:** доменная модель уже близка к Додо. Дальше — сервисы, API, правила, фронт и операционка.

Архитектура бэкенда: **Router → Service → Repository → SQLAlchemy**. Её нужно сохранить для всех новых доменов.

---

## 2. Роли (RBAC)

В БД уже есть: `roles`, `permissions`, `user_roles`, `role_permissions`.

| Роль | Кто | Что может |
|------|-----|-----------|
| `guest` | Не в системе | Меню, гостевая корзина |
| `client` | Клиент | Заказ, адреса, избранное, отзывы, свои заказы |
| `operator` | Смена / колл-центр | Все заказы, смена статусов, помощь |
| `kitchen` | Производство | Заказы `confirmed`/`cooking`/`ready` |
| `courier` | Доставка | `ready` → `delivering` → `completed` |
| `admin` | Владелец | Каталог, промо, роли, модерация, отчёты |

### Минимальный набор permissions (сделать seed)

- `catalog:read` / `catalog:write`
- `orders:read_own` / `orders:read_all` / `orders:update_status` / `orders:cancel`
- `promo:write`
- `users:manage`
- `reviews:moderate`
- `notifications:admin`

### Что реализовать

- [ ] Seed ролей и permissions
- [ ] Назначение `client` при регистрации
- [ ] FastAPI `Depends`: user → roles → permissions на защищённых эндпоинтах
- [ ] Админ-API только с нужным permission

---

## 3. Карта процессов (сквозной сценарий)

```
Меню → Конфигуратор → Корзина → [Логин] → Промокод → Checkout
  → Оплата → Кухня → Готов → Самовывоз / Доставка → Завершение
  → Уведомления / Отзыв / Избранное
```

Параллельно: **ЛК клиента**, **админка каталога**, **панель кухни/оператора/курьера**.

Ниже — процессы A–N: цель, правила, API, чек-лист.

---

## 4. Процесс A — Каталог и меню

### Цель
Клиент видит категории и товары с ценами и наличием — как витрина Додо.

### Модели (уже есть)
`categories`, `products`, `sizes`, `dough_types`, `ingredients`,  
`product_sizes`, `product_doughs`, `product_ingredients`, `product_addons`.

### Бизнес-правила

1. Категории: только `is_active`, сортировка `sort_order`.
2. Товары в списке: `is_active` + `is_available`; в карточке — мин. цена по `product_sizes` или `base_price`.
3. Деталка товара:
   - размеры и цены (`product_sizes`, только `is_available`);
   - типы теста (`product_doughs`, флаг `is_default`);
   - состав по умолчанию (`product_ingredients`);
   - допы (`product_addons` + `additional_price`).
4. Стоп-лист: `is_available = false` без удаления товара (как «закончилось на сегодня»).
5. Неактивный размер/доп нельзя выбрать, даже если товар доступен.

### Целевой API

| Метод | Путь | Кто |
|-------|------|-----|
| GET | `/categories`, `/categories/{slug}` | все |
| GET | `/products?category=&q=` | все |
| GET | `/products/{id\|slug}` | все (с sizes/doughs/ingredients/addons) |
| POST/PATCH/DELETE | каталог + привязки product_* | admin |

### Чек-лист реализации

- [ ] Починить текущий CRUD (схемы ingredients ≠ модели; sizes create сломан; delete не везде)
- [ ] Полный list/get/update для categories
- [ ] Деталка продукта с eager-load связей
- [ ] Админ: привязка sizes/doughs/ingredients/addons к продукту
- [ ] Seed: категории, размеры (25/30/35), тесто, 5–10 пицц
- [ ] (Опционально) загрузка картинок → storage, сейчас только `image_url`

---

## 5. Процесс B — Конфигуратор пиццы

### Цель
Как в Додо: размер → тесто → убрать/добавить ингредиенты → цена live → «В корзину».

### Бизнес-правила (зафиксировать и не менять без причины)

1. **Базовая цена позиции** = `product_sizes.price` выбранного размера (не слепо `products.base_price`).
2. **Тесто** — по умолчанию **бесплатно** (в `product_doughs` цены нет). Если позже нужна доплата — добавить поле.
3. **Снятие ингредиентов из состава** — цена **не снижается** (как у Додо чаще всего). Хранить список `removed_ingredient_ids` (потребуется поле/таблица или JSON; сейчас в схеме только «добавленные»).
4. **Допы** — цена из `product_addons.additional_price` (fallback: `ingredients.price`).
5. **Формула:**
   ```
   unit_price = size.price + sum(addon.price)
   line_total = unit_price * quantity
   ```
6. Ограничения: макс. N разных допов / макс. quantity на позицию (константы в сервисе).
7. Нельзя добавить недоступный продукт/размер/доп.
8. **Цену всегда считает сервер** — клиенту не доверять.

### Чек-лист

- [ ] Сервис `PriceCalculator` / `ConfiguratorService`
- [ ] Валидация конфигурации перед add-to-cart
- [ ] Решение по removed ingredients: таблица или JSON + API
- [ ] Константы лимитов допов

---

## 6. Процесс C — Корзина

### Модели (уже есть)
`carts` (`user_id` **или** `guest_token`), `cart_items` (`size_id`, `dough_type_id`), `cart_item_added_ingredients`.

### Бизнес-правила

1. Одна пользовательская корзина на `user_id` (unique).
2. Гостевая — по `guest_token` (cookie / `X-Cart-Token`).
3. В строке `carts` заполнено **ровно одно**: `user_id` или `guest_token`.
4. Добавление: валидация → расчёт `unit_price` → если та же конфигурация уже есть — `quantity++`.
5. Одинаковая конфигурация = `product_id` + `size_id` + `dough_type_id` + одинаковый набор допов.
6. Итоги: `subtotal`, после промо — `discount`, `delivery_cost` (на checkout), `total`.
7. На checkout пересчитать цены из каталога; если позиция стала недоступна — ошибка с понятным текстом.
8. TTL гостевых корзин: чистить старше 7–14 дней (cron/фоновая задача).

### Гостевая корзина (UX как Додо)

1. Первый `POST /cart/items` без JWT → создать Cart + `guest_token` → отдать токен.
2. Дальше гость шлёт `X-Cart-Token` или cookie.
3. После login/register: **merge** гостевой в пользовательскую → удалить гостевую.
4. Checkout только после авторизации (нужны user, адреса, история).

### Merge после логина

1. Найти guest cart по токену и user cart по `user_id`.
2. Слить: одинаковая конфигурация → сложить quantity; иначе — перенести.
3. Пересчитать `unit_price` по актуальному каталогу.
4. Удалить guest cart; клиент дальше только с JWT.

### Целевой API

- `GET /cart`
- `POST /cart/items`
- `PATCH /cart/items/{id}`
- `DELETE /cart/items/{id}`
- `DELETE /cart`
- `POST /cart/merge` (или автоматически внутри `/auth/login`)

### Чек-лист

- [ ] CartRepository + CartService
- [ ] Guest token create/validate
- [ ] Merge logic
- [ ] Серверный пересчёт итогов
- [ ] Очистка старых guest carts

---

## 7. Процесс D — Авторизация, профиль, адреса

### Модели (уже есть)
`users`, `addresses` (есть `is_default`).

### Auth

1. Регистрация: email + пароль + телефон + имя; `password_hash` (bcrypt/argon2); роль `client`.
2. Логин: JWT access + refresh (или session cookie).
3. После login — merge корзины (процесс C).
4. Восстановление пароля (email/SMS) — после MVP.

### Профиль (`/me`)

| Поле | В ответе | Изменение |
|------|----------|-----------|
| first_name, last_name, phone | да | `PATCH /me` |
| email | да | с подтверждением (после MVP можно запретить смену) |
| password_hash | **никогда** | `POST /me/password` (старый + новый) |
| is_active | нет клиенту | только admin |

Prefill checkout: `customer_name` ← имя, `customer_phone` ← phone, адрес ← `is_default`.

### Адреса

- CRUD: город, улица, дом, квартира, подъезд, этаж, домофон, комментарий, lat/lng.
- Ровно один `is_default` на пользователя (при установке нового — сбрасывать остальные).

### Зона доставки (нет в БД — спроектировать)

- Проверка: адрес в зоне (радиус / полигон / справочник).
- Вне зоны → только самовывоз или отказ.
- На MVP: константы в сервисе (`FREE_DELIVERY_FROM`, `DELIVERY_COST`, `MAX_RADIUS_KM`).
- Позже: таблица `delivery_zones`.

### Целевой API

- `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`
- `GET/PATCH /me`, `POST /me/password`
- CRUD `/me/addresses`

### Чек-лист

- [ ] Добавить в requirements: passlib/bcrypt, python-jose или PyJWT
- [ ] Auth service + middleware
- [ ] Addresses service + правило is_default
- [ ] Простая проверка зоны (константы)

---

## 8. Процесс E — Промокоды

### Модели (уже есть)
`promocodes`, `promocode_usages`.

### Бизнес-правила

1. `discount_type`: `percent` | `fixed` (позже: free_delivery).
2. Проверки при применении:
   - `is_active`, окно `starts_at`–`expires_at`;
   - `min_order_amount`;
   - `usage_limit` vs `usage_count` (0 = без лимита — зафиксировать);
   - один раз на пользователя через `promocode_usages` (рекомендуется для MVP);
   - `max_discount_amount` для percent.
3. Скидка **не** применяется к `delivery_cost`.
4. Успешный заказ → запись usage + `usage_count++`.
5. Отмена до оплаты → откат usage (политика).

### API

- `POST /cart/promocode`, `DELETE /cart/promocode`
- Admin CRUD `/admin/promocodes`

### Чек-лист

- [ ] PromoService (validate + calculate)
- [ ] Привязка к корзине (сессия/поле) и фиксация на checkout
- [ ] Admin CRUD

---

## 9. Процесс F — Оформление заказа (Checkout)

### Модели (уже есть)
`orders`, `order_items` (+ snapshots), `order_item_added_ingredients`,  
`order_statuses`, `order_status_history`, `payments`, `addresses`.

### Шаги UX

1. Корзина не пуста, позиции валидны, цены пересчитаны.
2. Доставка / самовывоз (`is_delivery`).
3. Адрес (сохранённый / новый) или точка самовывоза.
4. Контакты: `customer_name`, `customer_phone`.
5. Комментарий.
6. Промокод (если ещё не применён).
7. Расчёт:
   - `subtotal`
   - `discount_amount`
   - `delivery_cost` (0 при самовывозе; иначе тариф / бесплатно от N ₽)
   - `total_amount`
8. Способ оплаты → Payment → подтверждение.
9. После успеха (или COD):
   - создать Order + OrderItems + addon snapshots;
   - статус `new` (или `confirmed` для COD);
   - запись в `order_status_history`;
   - очистить корзину;
   - уведомление клиенту (+ событие для кухни).

### Статусы (seed уже в миграции)

| code | Название | Кто меняет |
|------|----------|------------|
| `new` | Новый | система |
| `confirmed` | Подтверждён | оператор / авто после оплаты |
| `cooking` | Готовится | кухня |
| `ready` | Готов | кухня |
| `delivering` | В пути | курьер / оператор |
| `completed` | Выполнен | курьер / система |
| `cancelled` | Отменён | клиент (рано) / оператор |

Каждый переход → `order_status_history` + `changed_by_user_id` + comment.

### Разрешённые переходы (state machine)

```
new → confirmed | cancelled
confirmed → cooking | cancelled
cooking → ready | cancelled (только operator)
ready → delivering | completed (самовывоз)
delivering → completed | cancelled (только operator)
```

Запретить любые другие прыжки статусов.

### Отмена

- Клиент: только `new` / `confirmed`.
- После `cooking` — только operator + причина.
- Оплаченный заказ → refund (процесс G).

### Snapshot (уже в схеме — обязательно писать при создании)

В `order_items`: `product_name`, `size_name`, `dough_type_name`, `unit_price`, `total_price`.  
В допах заказа: `ingredient_name` + `price`.  
Каталог потом можно менять — история заказа не ломается.

### API

- `POST /orders`
- `GET /orders` (мои), `GET /orders/{id}`
- `POST /orders/{id}/cancel`
- Staff: `PATCH /orders/{id}/status`, `GET /admin/orders`

### Чек-лист

- [ ] OrderService: create from cart + snapshots
- [ ] State machine статусов
- [ ] Cancel rules
- [ ] Идемпотентность создания (ключ запроса / повторный submit)

---

## 10. Процесс G — Оплата

### Модель (уже есть)
`payments`: amount, payment_method, status, paid_at, transaction_id.

### Способы (как у Додо)

| method | Описание | MVP |
|--------|----------|-----|
| `cash_on_delivery` | Наличные / карта курьеру | **Да, первым** |
| `card_online` | ЮKassa / CloudPayments / Stripe | После MVP |

### Логика онлайн (после MVP)

1. Order + Payment `pending`.
2. Редирект / виджет.
3. Webhook: успех → `paid` + заказ `confirmed`; неуспех → `failed`.
4. Идемпотентность webhook по `transaction_id`.
5. Кухне не отдавать заказ до надёжной оплаты (кроме COD).

### Чек-лист MVP

- [ ] COD: создать Payment `status=pending` или `awaiting_cash`, заказ `confirmed`
- [ ] Статусы payment: `pending` / `paid` / `failed` / `refunded`
- [ ] (Позже) эквайринг + webhook

---

## 11. Процесс H — Кухня

### Цель
Электронная очередь: ticket с размером, тестом, составом и допами.

### Логика

1. Экран: заказы `confirmed` → взять → `cooking`.
2. По готовности → `ready`.
3. Самовывоз: уведомить клиента «готов к выдаче».
4. Доставка: заказ появляется у курьера.
5. Live: polling каждые N сек или WebSocket/SSE.

### Чек-лист

- [ ] API списка заказов для роли `kitchen`
- [ ] Смена статуса с проверкой перехода
- [ ] Формат ticket (snapshots + addons)

---

## 12. Процесс I — Доставка

### Логика

1. Курьер: заказы `ready` + `is_delivery = true`.
2. Взял → `delivering`.
3. Доставил → `completed`, заполнить `completed_at`.
4. ETA на MVP: фикс (например 45–60 мин) или слот.
5. Клиентский трекинг: таймлайн статусов (как в Додо).

### Стоимость доставки (правила поверх БД)

Сейчас только поле `orders.delivery_cost`. Нужны правила в сервисе:

- самовывоз → 0;
- subtotal ≥ N → 0;
- иначе фикс / по зоне;
- вне зоны → ошибка.

### Чек-лист

- [ ] DeliveryCostService
- [ ] Courier API статусов
- [ ] Клиентский таймлайн в `GET /orders/{id}`

---

## 13. Процесс J — Избранное

### Модель
`favorites` (unique user+product, FK есть).

### API
- `GET /favorites`
- `POST /favorites/{product_id}`
- `DELETE /favorites/{product_id}`

### Чек-лист

- [ ] FavoritesService + API
- [ ] Только для авторизованных

---

## 14. Процесс K — Отзывы

### Модель
`reviews` (`rating`, `comment`, `is_published`).

### Правила

1. Отзыв только если у пользователя есть `completed` заказ с этим продуктом.
2. Рейтинг 1–5.
3. Публикация после модерации (`is_published`).
4. На карточке товара — средний рейтинг + опубликованные отзывы.

### API

- `POST /products/{id}/reviews`
- `GET /products/{id}/reviews`
- Admin: `PATCH /reviews/{id}` (publish/hide)

### Чек-лист

- [ ] ReviewsService + проверка покупки
- [ ] Модерация для admin

---

## 15. Процесс L — Уведомления

### Модель
`notifications` (title, message, type, is_read, read_at).

### События клиенту

- Заказ принят / готовится / готов / в пути / доставлен / отменён
- Ошибка оплаты
- (Позже) промо / новости

### API

- `GET /notifications`
- `PATCH /notifications/{id}/read`
- `POST /notifications/read-all`

### Чек-лист

- [ ] Создавать notification при смене статуса заказа
- [ ] API чтения
- [ ] (Позже) email / SMS / push

---

## 16. Процесс M — Админка и операционка

Не отдельный бэкенд, а UI + права поверх тех же API:

1. Каталог и стоп-лист (`is_available`)
2. Промокоды
3. Заказы и статусы (оператор)
4. Пользователи и роли
5. Модерация отзывов
6. (Позже) отчёты: заказы за день, средний чек, отмены

### Чек-лист

- [ ] Группа `/admin/*` с RBAC
- [ ] Seed admin-пользователя для разработки

---

## 17. Frontend (ещё нет)

Рекомендуемый стек: **Next.js / React** (или Vue) + мобильная вёрстка first.

| Экран | Процессы |
|-------|----------|
| Главная / меню по категориям | A |
| Карточка + конфигуратор | B |
| Корзина | C |
| Логин / регистрация | D |
| Checkout | F + G |
| Трекинг заказа | F + H + I |
| ЛК: профиль, адреса, история, избранное | D + J + L |
| Админ / кухня / курьер (можно отдельные SPA) | H + I + M |

### Чек-лист MVP UI

- [ ] Меню + конфигуратор + корзина
- [ ] Auth + checkout + COD
- [ ] Мои заказы + таймлайн статуса
- [ ] Простая панель кухни/оператора

---

## 18. Нефункциональные требования

1. **Цена всегда на сервере.**
2. **Идемпотентность** оплаты и `POST /orders`.
3. **Аудит статусов** — только append в `order_status_history`.
4. Индексы: `slug`, `category_id`, `user_id`, `guest_token`, `order.status_id`.
5. CORS, единый entrypoint (`app.main`), без дубля `backend/main.py` в проде.
6. Логи оплаты и смены статусов.
7. JWT + RBAC на admin/kitchen/courier.
8. Не создавать заказ из пустой / битой корзины.
9. Не отдавать `password_hash` наружу никогда.

---

## 19. Roadmap (порядок внедрения)

### Этап 0 — Стабилизация каталога
Починить CRUD sizes / dough / ingredients / categories / products. Seed меню. CORS.

### Этап 1 — Каталог «как Додо»
Деталка с sizes/doughs/addons. Админский CRUD + привязки.

### Этап 2 — Auth + адреса
Register/login JWT, `/me`, CRUD адресов, простая зона.

### Этап 3 — Конфигуратор + корзина
Расчёт цены, guest cart, merge, API корзины.

### Этап 4 — Checkout + статусы
Заказ из корзины, snapshots, history, отмена, «мои заказы».

### Этап 5 — Оплата MVP
COD; позже онлайн + webhook.

### Этап 6 — Промокоды
Validate/apply/usages.

### Этап 7 — Операционка
Кухня / оператор / курьер, уведомления при статусах.

### Этап 8 — ЛК-усилители
Избранное, отзывы, зоны доставки в БД.

### Этап 9 — Frontend
Параллельно можно начинать с этапа 1 (меню) и наращивать.

---

## 20. Критерии MVP «как Додо»

Пользователь может:

1. Открыть меню и выбрать пиццу с размером и тестом.
2. Добавить допы, положить в корзину (в т.ч. гостем), применить промокод.
3. Залогиниться, указать адрес / самовывоз и оформить заказ.
4. Оплатить хотя бы «при получении».
5. Видеть статусы: принят → готовится → готов / в пути → доставлен.
6. Админ ведёт каталог; кухня/оператор двигают статусы.

Онлайн-оплата, push, сложные зоны, аналитика, удалённые ингредиенты в БД — **после MVP**.

---

## 21. Связь процессов с кодом

| Процесс | Модели (есть) | Сделать |
|---------|---------------|---------|
| A Каталог | category, product, sizes, dough, ingredients, product_* | дописать CRUD + деталка |
| B Конфигуратор | product_sizes/doughs/addons | PriceCalculator |
| C Корзина | carts, cart_items, cart_item_added_ingredients | CartService + guest merge |
| D Auth / профиль | users, addresses | auth, me, addresses |
| E Промо | promocodes, promocode_usages | PromoService |
| F Заказ | orders, order_items, order_status* | OrderService + state machine |
| G Оплата | payments | PaymentService (+ webhook позже) |
| H–I Кухня / доставка | orders | status API + роли |
| J Избранное | favorites | Favorites API |
| K Отзывы | reviews | Reviews API |
| L Уведомления | notifications | create on events + API |
| M RBAC / админ | roles, permissions, … | seeds + Depends |

---

## 22. Техдолг, который мешает старту

1. Schemas `ingredients` не совпадают с моделью.
2. `SizesService.create` — битый код (импорт / `data.id`).
3. DELETE у части сущностей объявлен, но не реализован.
4. Category API — только create.
5. Нет JWT/hash библиотек в `requirements.txt`.
6. Два entrypoint: `backend/main.py` и `app/main.py`.
7. Нет seed каталога.
8. Frontend отсутствует.

Имеет смысл закрыть п.1–4 и 7 на **Этапе 0**, до корзины и заказов.

---

*Документ обновлять при выборе эквайринга, стека фронта и правил зон доставки.*
