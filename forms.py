from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, SelectField, SelectMultipleField, BooleanField, FormField, FieldList, widgets, Form
from markupsafe import Markup
from wtforms.validators import DataRequired, Optional, EqualTo

# Code for custom MultiCheckboxField from
# techcoil -> https://www.techcoil.com/blog/rendering-multiple-checkboxes-with-wtforms-and-bootstrap/ 

class BootstrapListWidget(widgets.ListWidget):
 
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
            else:
                html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))
 
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.
 
    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = BootstrapListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

#################################

class AddMenuItemForm(FlaskForm):
    """Form for adding menu items"""

    name = StringField("Menu Item Name", validators=[DataRequired()])

    image = StringField("Image", validators=[Optional()], filters=[lambda x: x or None])

    meal_type = SelectField("Meal Type", choices=[('entree','Entrees'),('appetizer', 'Appetizers'),('soup', 'Soups'), ('salad', 'Salads'),('beverage', 'Beverages'),('dessert','Desserts')])
    
    in_stock = BooleanField("In Stock")

    vegetarian = BooleanField("Vegetarian")

    description = TextAreaField('Description', validators=[Optional()])

    cost = DecimalField('Cost')
    
    # Single choice for now, will need to figure out how to add more later. Might use JS and a button
    ingredients = FieldList(StringField('Ingredients', validators=[Optional()], filters=[lambda x: x or None]), min_entries=3, max_entries=30)

    intolerants = MultiCheckboxField('Food Allergies', validators=[Optional()], filters=[lambda x: x or None])

# class AddOrderForm(FlaskForm):
#     """Form for adding orders"""


class ContactInfo(Form):
    """Subform for adding customer contact info"""

    name = StringField("Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number")
    
class Address(Form):
    """SubForm for adding customer address info, for delivery"""
    street = StringField("Street", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])


class TakeoutForm(FlaskForm):
    contact_info = FormField(ContactInfo)
    
class DeliveryForm(FlaskForm):
    """Form that encapsulates ContactInfoForm and AddressForm to get relevant information for delivery"""
    contact_info = FormField(ContactInfo)
    address = FormField(Address)

class PaymentMethodForm(FlaskForm):
    """Form to to choose payment option and send to waitstaff for checkout"""
    payment_method = SelectField("Payment Method", choices=[('cash', 'Cash'), ('card', 'Credit/Debit Card'), ('electronic', 'Electronic Payment Method')])

class SignupForm(FlaskForm):
    """Signup form for user, can be either customer or employee"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[Optional()])
    password = PasswordField('Password')
    # confirm = PasswordField('Confirm Password', validators=[EqualTo('password', 'passwords must match')])

    roles = SelectField("Role")
    
    email = StringField('Email Address', validators=[DataRequired()])
    address = StringField('Address', validators=[Optional()], filters=[lambda x: x or None])
    birthday = StringField('Birthday', validators=[Optional()], filters=[lambda x: x or None])
    phone_number = StringField('Telephone Number', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SelectTableForm(FlaskForm):
    table_number = SelectField('Tables', validators=[DataRequired()])