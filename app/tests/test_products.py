from app.models import Product
from app.tests.setup import client, test_db


def test_create_product(client, test_db):
    """Test creating a new product"""
    response = client.post(
        "/products/",
        json={
            "name": "Test Product",
            "description": "Test Description",
            "price": 10.99,
            "stock": 100
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["description"] == "Test Description"
    assert data["price"] == 10.99
    assert data["stock"] == 100
    assert "id" in data


def test_get_products(client, test_db):
    """Test getting all products"""
    # Add test products
    product1 = Product(name="Product 1", description="Description 1", price=10.0, stock=10)
    product2 = Product(name="Product 2", description="Description 2", price=20.0, stock=20)
    test_db.add(product1)
    test_db.add(product2)
    test_db.commit()

    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Product 1"
    assert data[1]["name"] == "Product 2"


def test_get_product(client, test_db):
    """Test getting a single product by ID"""
    # Add a test product
    product = Product(name="Test Product", description="Test Description", price=10.0, stock=10)
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    response = client.get(f"/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["id"] == product.id


def test_get_nonexistent_product(client):
    """Test getting a product that doesn't exist"""
    response = client.get("/products/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
