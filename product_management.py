from database import DatabaseManager

class ProductManager:
    def __init__(self, config):
        self.db_manager = DatabaseManager(config)

    def create_product(self, product_name, description, category, unit_price, quantity):
        query = "INSERT INTO products (product_name, description, category, unit_price, quantity) VALUES (%s, %s, %s, %s, %s)"
        params = (product_name, description, category, unit_price, quantity)
        self.db_manager.execute_query(query, params)

    def get_product(self, product_id):
        query = "SELECT * FROM products WHERE product_id = %s"
        params = (product_id,)
        result = self.db_manager.execute_query(query, params)
        return result.fetchone() if result else None

    def get_all_products(self):
        query = "SELECT * FROM products"
        result = self.db_manager.execute_query(query)
        return result.fetchall() if result else []

    def update_product(self, product_id, product_name, description, category, unit_price, quantity):
        query = "UPDATE products SET product_name = %s, description = %s, category = %s, unit_price = %s, quantity = %s WHERE product_id = %s"
        params = (product_name, description, category, unit_price, quantity, product_id)
        self.db_manager.execute_query(query, params)

    def delete_product(self, product_id):
        query = "DELETE FROM products WHERE product_id = %s"
        params = (product_id,)
        self.db_manager.execute_query(query, params)
