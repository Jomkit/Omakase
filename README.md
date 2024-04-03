# Omakase OMS

**A multi-page web application that facilitates order management, geared towards small-businesses. Omakase allows restaurant owners to set up their own menus and manage their employees. Customers are also able to order food from their own devices, choosing dining in, takeout, or delivery, as desired.**

**This app was built using Python, specifically the Flask web app framework, JavaScript jQuery, and PostgreSQL for databasing.**

Try out the app at: [Omakase OMS](https://github.com/hatchways-community/capstone-project-one-730961227c7e4439bdc8b03ed6c3cd4d.git)

## App Features

![Omakase landing page](/static/images/oms_landing.png)
*Website landing page*

- Restaurant owners can upload images, descriptions of their business, and add employees to different roles. 
- Restaurant staff with proper authorization (admin) can add menu items to the restaurant menu.  
- Restaurant staff can monitor active orders and view order history from the employee dashboard.

![Image of employee dashboard](/static/images/emp_db.png)
*Employee Dashboard*

- List of all employees, their employee id, name, role, and phone number.

![Image of employee list page](/static/images/emp_list.png)
*Employee List Page*

- Customers can choose whether to dine in, get takeout, or order delivery. (picture?)
    - Dining in has the option to choose a table.
    - Takeout requires inputting name, and phone number.
    - Delivery requires name and phone number as well, as well as street, city, and state. 
- Customers can order food from the menu, which will be added to their order and update a bill on the side of the screen. 
- Customers can press a button to request assistance from the waitstaff. 
- When ready, customers can check out and see their itemized bill. 

## User Flow

There are two main user flows associated with this app.

### Restaurant Staff

- A staff member logs in from the landing page
- They are taken to the employee dashboard. An "Employees" dropdown menu is displayed in the navbar.

![Image of employee dropdown](/static/images/emp_dropdown.png)
*Employee Dropdown Menu*

- This dropdown menu has multiple options; staff members may add a menu item, go to the employee list, or add an employee.
    - Clicking the "Add Menu Item" brings the user to a form where they can add information for a new menu item, including name, description, cost, and image.
    - Clicking "Employee List" brings the user to the employee list.
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


## Resources
### API
- Created custom RESTful API to handle dynamic order updates.

### Technology Used
- Python
- Flask Web Application Framework
- JavaScript
- jQuery
- Bootstrap

////////////////////////////////////////////////////

[Here is an example of a previous project.](https://github.com/juliahazer/chart-my-team)
