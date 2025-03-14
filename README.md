**Restful APIs for a simple e-commerce platform built with FastAPI.**


**Features**

- View all available products
- Add new products to the platform
- Place orders with stock validation
- Comprehensive error handling
- Caching & optimised querying ensuring APIs are performant at scale
- Complete test suite
- Dockerized for easy deployment

---
**API Endpoints**

**Products**

- GET /products - Retrieve a list of all available products
- POST /products - Add a new product
- GET /products/{product_id} - Retrieve a specific product

**Orders**

- POST /orders - Place a new order with automatic stock validation
- GET /orders - Retrieve all orders
- GET /orders/{order_id} - Retrieve a specific order

**Getting Started**

**Prerequisites**
- Docker and Docker Compose
- Python 3.9+ (for local development)

**Running with Docker**

1. Clone the repository:
```
git clone https://github.com/srujanamanvi/ecommerce_fastapi.git
cd ecommerce-api
```
2. Add a .env file with the below environment variables on the machine where the code is run
```
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL

```

3. Build and start the Docker container:
```docker-compose up --build```

4. The API will be available at http://localhost:8000
- API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

---
**Local Development:**

1. Create a virtual environment:
```
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```pip install -r requirements.txt```

3. setup DATABASE_URL (optional if not present):
```export DATABASE_URL="postgresql://postgres:password@localhost:5432/mydatabase"```

4. Run the application:
```
  alembic upgrade head
  uvicorn app.main:app --reload
```
5. (Optional - not required if using testing with sqllite) Add a .env file with the below environment variables
```
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL

```


**Running Tests:**

- In Docker:

  ```docker-compose run api pytest```
  
- Locally
```
     pytest tests/test_orders.py
     pytest tests/test_products.py
```

---
**API Examples**

**Creating a Product**

```curl -X 'POST' \
  'http://localhost:8000/products/' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Smartphone",
  "description": "Latest model smartphone",
  "price": 699.99,
  "stock": 50
}'
```

**Placing an Order**
```
curl -X 'POST' \
  'http://localhost:8000/orders/' \
  -H 'Content-Type: application/json' \
  -d '{
  "products": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}'
```

**Project Structure**

```
zaniaTest/
├── app/                   # Application code
│   ├── __init__.py
│   ├── main.py            # Main FastAPI application
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database setup
│   ├── exceptions.py      # Custom exceptions
│   ├── urls.py            # all the URLs defined in the system
│   └── views/             # API endpoints
│       ├── __init__.py
│       ├── products.py
│       └── orders.py
    └── settings/          # API endpoints
│       ├── __init__.py
│       ├── local.py
│       └── production.py
|
├── tests/                 # Test cases
│   ├── __init__.py
│   ├── test_products.py
│   └── test_orders.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic                 # alembic migrations 
├── alembic.ini.example     # alembic local config
└── README.md

```


**Business Logic Implementation**
- Stock Management: Automatic stock validation and deduction
- Order Processing: Comprehensive validation before confirming orders
