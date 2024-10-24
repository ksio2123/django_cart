# Little Lemon API

## Description
This project sets up REST endpoints for a shopping cart system for a restaurant. It includes functionalities for managers to add items, customers to add items to a shopping cart and create an order, and delivery crew to deliver the order.

## Endpoints
### Users
- **POST /api/users**
  - No role required
  - Creates a new user with name, email, and password.
- **GET /api/users/users/me/**
  - Anyone with a valid user token
  - Displays user information.

### Menu Items
- **GET /api/menu-items**
  - Customer, delivery crew
  - Lists all menu items. Returns a...

### Groups
- **GET /api/groups/manager/users**
  - Manager
  - Returns all managers.

## Models
### Category
- **Fields:**
  - slug (SlugField)
  - title (CharField)

### MenuItem
- **Fields:**
  - title (CharField)
  - price (DecimalField)
  - featured (BooleanField)
  - category (ForeignKey to Category)

### Cart
- **Fields:**
  - user (ForeignKey to User)
  - menu_item (ForeignKey to MenuItem)
  - quantity (SmallIntegerField)
  - unit_price (DecimalField)
  - price (DecimalField)

### Order
- **Fields:**
  - user (ForeignKey to User)
  - delivery_crew (ForeignKey to User, nullable)
  - status (BooleanField)
  - total (DecimalField)
  - date (DateField)

### OrderItem
- **Fields:**
  - order_id (ForeignKey to Order)
  - menu_item_id (ForeignKey to MenuItem)
  - quantity (IntegerField)
  - unit_price (DecimalField)
  - price (DecimalField)

## Installation
1. Clone the repository.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Apply migrations by running `python manage.py migrate`.
4. Start the development server with `python manage.py runserver`.

## Usage
1. Access the API endpoints to interact with the shopping cart system.
2. Use appropriate permissions for different user roles (customer, manager, delivery crew).
3. Test the functionality of adding items to the cart, creating orders, and managing menu items.

## Contributors
- [Your Name](https://github.com/yourusername)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.