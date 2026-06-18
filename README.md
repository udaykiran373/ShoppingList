# Shopping List Management API

A production-quality RESTful API built with **FastAPI** and **MongoDB** (async Motor driver) for managing multiple shopping lists and their items.

---

## Features

- Full CRUD for shopping lists and items
- Soft delete (data is never permanently lost)
- Pagination on all list endpoints
- Name-based search (MongoDB text index)
- Bulk item creation
- Mark all items as purchased
- Structured logging (INFO + ERROR)
- Centralized exception handling with meaningful error codes
- Auto-generated Swagger UI at `/docs`

---

## Project Structure

```
app/
├── main.py                          # App entry point, lifecycle, global handlers
├── routers/
│   ├── shopping_lists.py            # Shopping list endpoints
│   └── shopping_items.py            # Shopping item endpoints
├── services/
│   ├── shopping_list_service.py     # Business logic for lists
│   └── shopping_item_service.py     # Business logic for items
├── repositories/
│   ├── shopping_list_repository.py  # MongoDB queries for lists
│   └── shopping_item_repository.py  # MongoDB queries for items
├── models/
│   ├── shopping_list.py             # DB document model
│   └── shopping_item.py             # DB document model
├── schemas/
│   ├── shopping_list.py             # Request/response Pydantic schemas
│   └── shopping_item.py             # Request/response Pydantic schemas
├── database/
│   └── mongodb.py                   # Motor client, indexes, dependency
└── utils/
    └── logger.py                    # Structured logger factory
```

---

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=shopping_list_db
```

---

## Setup & Run

### Local Python

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env

# 4. Start MongoDB locally (if not running)
mongod --dbpath ./data/db

# 5. Run the API
uvicorn app.main:app --reload
```

---

## API Documentation

Open your browser at:

- Swagger UI: `http://127.0.0.1:8000/docs`

---

## API Endpoints

### Shopping Lists

| Method | Endpoint                    | Description                         |
| ------ | --------------------------- | ----------------------------------- |
| POST   | `/shopping-lists`           | Create a new shopping list          |
| GET    | `/shopping-lists`           | List all shopping lists (paginated) |
| GET    | `/shopping-lists/{list_id}` | Get a shopping list by ID           |
| PUT    | `/shopping-lists/{list_id}` | Update a shopping list              |
| DELETE | `/shopping-lists/{list_id}` | Soft-delete a shopping list         |

### Shopping Items

| Method | Endpoint                                             | Description                 |
| ------ | ---------------------------------------------------- | --------------------------- |
| POST   | `/shopping-lists/{list_id}/items`                    | Add item to list            |
| POST   | `/shopping-lists/{list_id}/items/bulk`               | Bulk add items              |
| GET    | `/shopping-lists/{list_id}/items`                    | List all items (paginated)  |
| GET    | `/shopping-lists/{list_id}/items/{item_id}`          | Get item by ID              |
| PUT    | `/shopping-lists/{list_id}/items/{item_id}`          | Update item                 |
| DELETE | `/shopping-lists/{list_id}/items/{item_id}`          | Soft-delete item            |
| PATCH  | `/shopping-lists/{list_id}/items/mark-all-purchased` | Mark all items as purchased |

### Query Parameters (GET list endpoints)

| Parameter   | Default | Description                  |
| ----------- | ------- | ---------------------------- |
| `page`      | 1       | Page number (1-based)        |
| `page_size` | 10      | Results per page (max 100)   |
| `search`    | —       | Filter by name (text search) |

---

## Usage Examples

### Create a shopping list

```bash
curl -X POST http://localhost:8000/shopping-lists \
  -H "Content-Type: application/json" \
  -d '{"name": "Weekly Groceries", "description": "Items for the week"}'
```

### Add an item

```bash
curl -X POST http://localhost:8000/shopping-lists/<list_id>/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Milk", "quantity": 2, "unit": "liters"}'
```

### Bulk add items

```bash
curl -X POST http://localhost:8000/shopping-lists/<list_id>/items/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"name": "Eggs", "quantity": 12, "unit": "pieces"},
      {"name": "Bread", "quantity": 1, "unit": "loaf"}
    ]
  }'
```

### Search lists by name

```bash
curl "http://localhost:8000/shopping-lists?search=grocery&page=1&page_size=5"
```

### Mark all items as purchased

```bash
curl -X PATCH http://localhost:8000/shopping-lists/<list_id>/items/mark-all-purchased
```

---

## Error Response Format

```json
{
  "message": "Shopping list not found",
  "error_code": "SHOPPING_LIST_NOT_FOUND"
}
```

### HTTP Status Codes

| Scenario           | Code |
| ------------------ | ---- |
| Created            | 201  |
| Success            | 200  |
| No Content         | 204  |
| Invalid Request    | 400  |
| Not Found          | 404  |
| Validation Failure | 422  |
| Internal Error     | 500  |

---

## Bonus Features Implemented

- [x] Pagination for list endpoints
- [x] Search shopping lists by name
- [x] Search items by name
- [x] Soft delete support
- [x] Bulk item creation endpoint
- [x] Mark all items as purchased endpoint
- [x] MongoDB indexes (text + compound)
- [x] Async MongoDB driver (Motor)
