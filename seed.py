from models import User, Role, Group, Restaurant, MenuItem, Intolerant, Ingredient, ItemIngredient, RestaurantMenu, OrderedItems, Table, Order, db
from datetime import datetime, timedelta
from app import app

#drop and create all tables to start clean
with app.app_context():
    db.drop_all()
    db.create_all()

    roles = [
        Role(name='waitstaff'),
        Role(name='kitchen'),
        Role(name='admin')
    ]
    db.session.add_all(roles)
    
    groups = [
        Group(name='employee'),
        Group(name='customer'),
    ]
    db.session.add_all(groups)
    db.session.commit()

    restaurants = [
        Restaurant(name="Test Restaurant", address="52 Main Street")
    ]

    db.session.add_all(restaurants)
    db.session.commit()

    employees = [
        User(restaurant_id=1, name='test', uname='testadmin', password=User.hash_pw('123test123'), address='123 Test St.', birthday='1/1/1990',
             roles=[Role.query.filter_by(name='admin').first()], 
             groups=[Group.query.filter_by(name='employee').first()]),
        User(restaurant_id=1, name='Jeff', address='1 Jeff Ln', birthday='1/1/1990',
             roles=[Role.query.filter_by(name='waitstaff').first()], 
             groups=[Group.query.filter_by(name='employee').first()]),
        User(restaurant_id=1, name='Karly', address='2 Jeff Ln', birthday='1/2/1990',
             roles=[Role.query.filter_by(name='waitstaff').first()], 
             groups=[Group.query.filter_by(name='employee').first()]),
        User(restaurant_id=1, name='Greg', address='1 Main St', birthday='1/4/1980',
             roles=[Role.query.filter_by(name='kitchen').first()], 
             groups=[Group.query.filter_by(name='employee').first()]),
        User(restaurant_id=1, name='Julianne', address='1 Main St', birthday='1/4/1980', 
             groups=[Group.query.filter_by(name='employee').first()]),
        User(restaurant_id=1, name='John', address='1 Main St', birthday='1/4/1980', 
             roles=[Role.query.filter_by(name='admin').first()], 
             groups=[Group.query.filter_by(name='employee').first()]),
        User(restaurant_id=1, name='Jacque', address='1 Main St', birthday='1/4/1980', 
             roles=[Role.query.filter_by(name='admin').first()], 
             groups=[Group.query.filter_by(name='employee').first()])
    ]

    db.session.add_all(employees)
    db.session.commit()

    customers = [
        User(name='Ken', address='1 Main St', phone_number='123-456-0000', birthday='1/1/1970', groups=[Group.query.filter_by(name='customer').first()]),
        User(name='Barbara', address='1 Main St', phone_number='123-654-0000', birthday='8/1/1978', groups=[Group.query.filter_by(name='customer').first()]),
        User(name='Glenn', address='54 Main St', phone_number='123-456-7890', birthday='1/1/1999', groups=[Group.query.filter_by(name='customer').first()])
    ]

    db.session.add_all(customers)
    db.session.commit()

    intolerants = [
        Intolerant(name='milk'),
        Intolerant(name='eggs'),
        Intolerant(name='fish'),
        Intolerant(name='shellfish'),
        Intolerant(name='tree nuts'),
        Intolerant(name='nuts'),
        Intolerant(name='wheat'),
        Intolerant(name='soybeans'),
        Intolerant(name='sesame')
    ]

    db.session.add_all(intolerants)
    db.session.commit()

    ingredients = [
        Ingredient(name='cheese'),
        Ingredient(name='beef'),
        Ingredient(name='chicken'),
        Ingredient(name='eggs'),
        Ingredient(name='milk'),
        Ingredient(name='bread'),
        Ingredient(name='vanilla essence'),
        Ingredient(name='rice'),
    ]

    db.session.add_all(ingredients)
    db.session.commit()

    menu_items = [
        MenuItem(name='Grilled Cheese', meal_type='sandwich',description='Cheesed melted between toast', cost=1.50, 
                intolerants=Intolerant.query.filter(Intolerant.name.in_(['milk','wheat'])).all(),
                ingredients=Ingredient.query.filter(Ingredient.name.in_(['cheese','bread'])).all()
                ),
        MenuItem(name='Chicken and Rice', meal_type='entree',description='Pan-fried chicken on a bed of rice', cost=12.99, 
                intolerants=Intolerant.query.filter(Intolerant.name.in_(['wheat'])).all(),
                ingredients=Ingredient.query.filter(Ingredient.name.in_(['chicken','rice'])).all()
                ),
        MenuItem(name='Onion Rings', meal_type='appetizer',description='Breaded fried onion rings', cost=6.95),
        MenuItem(name='Salt and Pepper Calamari', meal_type='appetizer',description='Fried squid and octopus', cost=12.99),
        MenuItem(name='Fish and Chips', meal_type='entree',description='Fried halibut and french fries', cost=15.95),
        MenuItem(name='Butter Chicken', meal_type='entree',description='Indian stewed chicken dish with spices', in_stock=False, cost=18.50),
        MenuItem(name='Ice Cream', meal_type='dessert',description='Chilled dairy dish', cost=6.5, 
                intolerants=Intolerant.query.filter(Intolerant.name.in_(['milk','eggs'])).all(),
                ingredients=Ingredient.query.filter(Ingredient.name.in_(['milk','eggs','vanilla essence'])).all()
                ),
        MenuItem(name='Soda', meal_type='beverage',description='Carbonated drink', cost=3.5)
    ]

    db.session.add_all(menu_items)
    for i in menu_items:
        restaurants[0].menu.append(i)
    db.session.commit()

    tables = [
        Table(),
        Table(),
        Table(),
        Table(),
        Table(),
        Table(),
    ]

    db.session.add_all(tables)
    db.session.commit()

    orders = [  
        Order(employee_id=1, type='Takeout', timestamp=datetime.now() - timedelta(minutes=30)),
        Order(employee_id=1, type='Delivery', timestamp=datetime.now() - timedelta(minutes=15)),
        Order(employee_id=3, type='Takeout', timestamp=datetime.now() - timedelta(minutes=5)),
        Order(employee_id=2, type='Dining In', active=False, table_number=2),
        Order(employee_id=2, type='Dining In', active=False, table_number=2),
        Order(employee_id=2, type='Dining In', active=False, table_number=2),
        Order(employee_id=2, type='Dining In', table_number=2),
        Order(employee_id=2, type='Dining In', table_number=5),
        Order(employee_id=2, type='Dining In', table_number=3),
    ]

    db.session.add_all(orders)
    db.session.commit()

    orders2 = db.session.query(Order).all()
    customers2 = db.session.query(User).all()
    orders2[0].customers.append(customers2[0])
    orders2[0].customers.append(customers2[1])
    orders2[1].customers.append(customers2[2])
    orders2[2].customers.append(customers2[1])

    db.session.commit()

    ordered_items = [
        OrderedItems(order_id=1, menu_item_id=1, quantity=2),
        OrderedItems(order_id=1, menu_item_id=2, quantity=1),
        OrderedItems(order_id=1, menu_item_id=3, quantity=1),
        OrderedItems(order_id=2, menu_item_id=1, quantity=4),
        OrderedItems(order_id=2, menu_item_id=3, quantity=1),
        OrderedItems(order_id=3, menu_item_id=1, quantity=1),
        OrderedItems(order_id=3, menu_item_id=5, quantity=1),
        OrderedItems(order_id=4, menu_item_id=2, quantity=1)
    ]

    db.session.add_all(ordered_items)
    db.session.commit()