import pytest
from app.tests.setup import client, test_db
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models import Product, Order, OrderProduct
from app.views.orders import (
    get_products_by_ids,
    create_order_record,
    process_order_items,
    validate_product_stock,
    finalize_order,
    format_order_response,
    create_order
)
from app import schemas
from app import exception


class TestOrderAPI:
    def test_create_order(self, client, test_db):
        """Test creating a new order with valid products and quantities"""
        # Create test products
        product1 = Product(name="Product 1", description="Description 1", price=10.0, stock=10)
        product2 = Product(name="Product 2", description="Description 2", price=20.0, stock=20)
        test_db.add(product1)
        test_db.add(product2)
        test_db.commit()
        test_db.refresh(product1)
        test_db.refresh(product2)

        # Create order
        response = client.post(
            "/orders/",
            json={
                "products": [
                    {"product_id": product1.id, "quantity": 2},
                    {"product_id": product2.id, "quantity": 1}
                ]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total_price"] == 10.0 * 2 + 20.0 * 1
        assert data["status"] == "pending"
        assert len(data["products"]) == 2

        # Verify stock was reduced
        test_db.refresh(product1)
        test_db.refresh(product2)
        assert product1.stock == 8
        assert product2.stock == 19

    def test_create_order_insufficient_stock(self, client, test_db):
        """Test creating an order with insufficient stock"""
        # Create test product with limited stock
        product = Product(name="Limited Stock", description="Description", price=10.0, stock=5)
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)

        # Try to order more than available
        response = client.post(
            "/orders/",
            json={
                "products": [
                    {"product_id": product.id, "quantity": 10}
                ]
            }
        )

        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]

        # Verify stock was not reduced
        test_db.refresh(product)
        assert product.stock == 5

    def test_create_order_nonexistent_product(self, client):
        """Test creating an order with a nonexistent product"""
        response = client.post(
            "/orders/",
            json={
                "products": [
                    {"product_id": 9999, "quantity": 1}
                ]
            }
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_empty_order(self, client):
        """Test creating an order with no products"""
        response = client.post(
            "/orders/",
            json={
                "products": []
            }
        )

        assert response.status_code == 422  # Validation error


class TestGetProductsByIds:
    def test_returns_products_map_when_all_products_exist(self):
        
        mock_db = MagicMock(spec=Session)
        product_ids = [1, 2]
        mock_products = [
            MagicMock(spec=Product, id=1),
            MagicMock(spec=Product, id=2)
        ]
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = mock_products

        
        result = get_products_by_ids(mock_db, product_ids)

        assert len(result) == 2
        assert 1 in result
        assert 2 in result
        mock_db.query.assert_called_once_with(Product)
        mock_query.filter.assert_called_once()

    def test_raises_exception_when_product_not_found(self):
        
        mock_db = MagicMock(spec=Session)
        product_ids = [1, 2]
        mock_products = [MagicMock(spec=Product, id=1)]  # Only one product found
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.all.return_value = mock_products

        
        with pytest.raises(exception.ProductNotFoundError) as exc_info:
            get_products_by_ids(mock_db, product_ids)

        assert exc_info.value.product_id == 2


class TestCreateOrderRecord:
    def test_creates_pending_order(self):
        
        mock_db = MagicMock(spec=Session)

        
        result = create_order_record(mock_db)

        
        assert result.status == "pending"
        assert result.total_price == 0.0
        mock_db.add.assert_called_once_with(result)
        mock_db.flush.assert_called_once()


class TestValidateProductStock:
    def test_passes_when_sufficient_stock(self):
        
        mock_product = MagicMock(spec=Product, id=1, stock=10)
        requested_quantity = 5

        # Should not raise an exception
        validate_product_stock(mock_product, requested_quantity)

    def test_raises_exception_when_insufficient_stock(self):
        
        mock_product = MagicMock(spec=Product, id=1, stock=5)
        requested_quantity = 10

        
        with pytest.raises(exception.InsufficientStockError) as exc_info:
            validate_product_stock(mock_product, requested_quantity)

        assert exc_info.value.product_id == 1
        assert exc_info.value.available == 5
        assert exc_info.value.requested == 10


class TestProcessOrderItems:
    def test_processes_items_correctly(self):
        
        order_id = 1
        items = [
            schemas.OrderProductItem(product_id=1, quantity=2),
            schemas.OrderProductItem(product_id=2, quantity=3)
        ]
        products_map = {
            1: MagicMock(spec=Product, id=1, price=10.0, stock=5),
            2: MagicMock(spec=Product, id=2, price=15.0, stock=10)
        }
        mock_db = MagicMock(spec=Session)

        
        total_price, order_products = process_order_items(order_id, items, products_map, mock_db)

        
        assert total_price == (2 * 10.0) + (3 * 15.0) == 65.0
        assert len(order_products) == 2
        assert products_map[1].stock == 3  # 5 - 2
        assert products_map[2].stock == 7  # 10 - 3
        mock_db.bulk_save_objects.assert_called_once_with(order_products)


class TestFinalizeOrder:
    def test_updates_order_total_and_commits(self):
        
        mock_order = MagicMock(spec=Order)
        total_price = 100.0
        mock_db = MagicMock(spec=Session)

        
        finalize_order(mock_order, total_price, mock_db)

        
        assert mock_order.total_price == 100.0
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_order)


class TestFormatOrderResponse:
    def test_formats_order_correctly(self):
        
        mock_order_product = MagicMock(spec=OrderProduct)
        mock_order_product.product_id = 1
        mock_order_product.quantity = 2

        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.total_price = 100.0
        mock_order.status = "pending"
        mock_order.order_products = [mock_order_product]

        
        result = format_order_response(mock_order)

        
        assert result.id == 1
        assert result.total_price == 100.0
        assert result.status == "pending"
        assert len(result.products) == 1
        assert result.products[0].product_id == 1
        assert result.products[0].quantity == 2


class TestCreateOrder:
    @patch('app.views.orders.get_products_by_ids')
    @patch('app.views.orders.create_order_record')
    @patch('app.views.orders.process_order_items')
    @patch('app.views.orders.finalize_order')
    @patch('app.views.orders.format_order_response')
    def test_create_order_success(self, mock_format, mock_finalize, mock_process,
                                  mock_create_record, mock_get_products):
        
        mock_db = MagicMock(spec=Session)
        order = schemas.OrderCreate(products=[
            schemas.OrderProductItem(product_id=1, quantity=2),
            schemas.OrderProductItem(product_id=2, quantity=3)
        ])

        mock_products_map = {1: MagicMock(), 2: MagicMock()}
        mock_order = MagicMock(spec=Order, id=1)
        mock_get_products.return_value = mock_products_map
        mock_create_record.return_value = mock_order
        mock_process.return_value = (100.0, [MagicMock()])
        mock_format.return_value = schemas.Order(
            id=1, total_price=100.0, status="pending", products=[]
        )

        
        result = create_order(order, mock_db)

        
        mock_get_products.assert_called_once_with(mock_db, [1, 2])
        mock_create_record.assert_called_once_with(mock_db)
        mock_process.assert_called_once_with(mock_order.id, order.products, mock_products_map, mock_db)
        mock_finalize.assert_called_once_with(mock_order, 100.0, mock_db)
        mock_format.assert_called_once_with(mock_order)
        assert result.id == 1
        assert result.total_price == 100.0
        assert result.status == "pending"

    @patch('app.views.orders.get_products_by_ids')
    def test_create_order_product_not_found(self, mock_get_products):
        
        mock_db = MagicMock(spec=Session)
        order = schemas.OrderCreate(products=[
            schemas.OrderProductItem(product_id=1, quantity=2)
        ])

        # Simulate product not found
        mock_get_products.side_effect = exception.ProductNotFoundError(1)

        
        with pytest.raises(exception.ProductNotFoundError):
            create_order(order, mock_db)
