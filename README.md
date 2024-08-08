# Omakase OMS

**A multi-page web application that facilitates order management, geared towards small-businesses. Omakase allows restaurant owners to set up their own menus and manage their employees. Customers are also able to order food from their own devices, choosing dining in, takeout, or delivery, as desired.**

**This app was built using Python, specifically the Flask web app framework, JavaScript jQuery, and PostgreSQL for databasing.**

Try out the app at: [Omakase OMS](https://omakase-ma8t.onrender.com)

### Quickstart
- After following [Setup](#setup) below, all you have to do to get started is run the flask server and you'll be greeted with the landing page. Either run through the userflow for customers by clicking any one of the Header Tabs or the options "Dining In," "Takeout," or "Delivery."
- If you'd like to check out the employee userflow, from the base url add `/login`. I recommend using the pre-seeded manager user instance, username: "testmanager" and password: "123test123."

## App Features

![Omakase landing page](/static/images/omakase_landing_v2.png)
*Website landing page*

- Restaurant owners can upload images, descriptions of their business, and add employees to different roles. 
- Restaurant staff with proper authorization (manager) can add menu items to the restaurant menu.  
- Restaurant staff can monitor active orders and view order history from the employee dashboard.

![Omakase employee dashboard](/static/images/emp_dashboard_v2.png)
*Employee Dashboard*

- List of all employees, their employee id, name, role, and phone number.

![Omakase employee list](/static/images/employee_list_v2.png)
*Employee List Page*

- Customers can choose whether to dine in, get takeout, or order delivery. (picture?)
    - Dining in has the option to choose a table.
    - Takeout requires inputting name, and phone number.
    - Delivery requires name and phone number as well, as well as street, city, and state. 
- Customers can order food from the menu, which will be added to their order and update a bill on the side of the screen. 
- Customers can press a button to request assistance from the waitstaff. 
- When ready, customers can checkout and see their itemized bill. 
- After choosing a payment option, they are directed to waitstaff to complete the payment process

## User Flow

There are two main user flows associated with this app.

### Restaurant Staff

- A staff member must append `/login` to the url to go to the login page.
- Upon signing in, they are taken to the employee dashboard. An "Employees" dropdown menu is displayed in the navbar.
- This dropdown menu has multiple options; staff members may add a menu item, go to the employee list, or add an employee.
    - Clicking the "Add Menu Item" brings the user to a form where they can add information for a new menu item, including name, description, cost, and image.
    - Clicking "Employee List" brings the user to the employee list. Only managers have the authority to delete employees.
    - Clicking "Add Employee" takes the user to a form where they can add a new employee.

### Customers

- The customer has three paths they can take, all roughly the same: Dining in, takeout, and delivery
- Customers dining in will click the "Dining In" tab on the navbar, and then be taken to a page where they choose their table. 
- Customers getting takeout will click the "Takeout" tab on the navbar, taking them to a page where they enter their name and phone number for contact. 
- Customers ordering delivery will click the "Delivery" tab on the navbar, taking them to a page similar to the takeout contact form, except for deliveries. This form includes name and phone number fields, as well as address.
- After choosing their table or entering their contact info/address, customers are taken to a menu page where they can order food and it is updated on the itemized bill. 
- Customers can request assistance from waitstaff by clicking on the "Assistance" button located on the righthand bill. 
- When finished with their order, customers can checkout by clicking the associated button on the bill area.
- Clicking "Checkout" takes the customer to a "Final Bill" screen where they can check over their order one last time before proceeding to a payment page.
- This payment page doesn't actually handle payments, but lets the customer pick a payment type which is saved to the order.
- After they've picked their payment type users are taken to a final "Thank You" page, where they can exit the page safely.

## Setup 
- The first step to setting up this project locally is to copy it. Either [forking](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) or [cloning](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the repository will do.
- If you don't want to globally install dependencies, make sure to set up a virtual environment as well. 
- install dependencies
- create a `.env` file and include `SECRET_KEY` and `FLASK_ENV` variables. Set the former to whatever string, random or otherwise, you like, but be sure to set `FLASK_ENV` to "development".
- Set up a psql database named "omakase": `createdb omakase`
- Set up the database by seeding it: `python seed.py`
- Once seeded, an example restaurant, example employees, and example customers will be loaded. 
    - If you'd like you can edit the `seed.py` file to remove most of the employees and customers, but **don't delete the example restaurant**, and **make sure there is one employee with the manager role**. Edit the one in the `seed.py` file if you'd like to.
- **Now it's time to start up the app!**
- Run `flask run` while in a virtual environment and head to `localhost:5000`

## How To Omakase
- I encourage you to explore and try out this app, and please share your thought and critiques. If you'd like a step-by-step tutorial however, this is the section for you.

### Login as Manager
- If you haven't edited the manager user instance in the seed, then the login should be username: `testmanager`, password: `123test123`.

## Running Tests
- Running tests is simple, and begins with `python -m unittest`. 
- To run all tests, from the root directory of the project enter `python -m unittest discover -s tests -p "test_*`. This will search for all tests in the `tests` file and run the ones prefixed with `test_`.
- Running individual tests is as easy as specifying the file: `python -m unittest tests.test_basic_routes` for example. 
    - Simply replace `test_basic_routes` with whichever test file you'd like to run specifically, in the `tests` folder.

## Future Functionality
In the future, functionality I would like to implement include:
* Sign-in and user profiles for customers to save favorite orders save delivery information
* Reservation system
* Dine-in waitlist
* Interactive and editable floor plan view
* File upload functionality for managers/owners adding pictures of the restaurant to landing page

## Resources Used
### API
- Created custom RESTful API to handle dynamic order updates.

### Technology Used
- Python
- Flask Web Application Framework
- JavaScript
- jQuery
- Bootstrap
