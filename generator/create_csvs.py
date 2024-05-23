"""Generate CSVs of random data for omakase

Using the 'create_csvs.py' file from the warbler
project for reference
"""

import csv
import requests

EMPLOYEE_CSV_HEADERS = ['name', 'address', 'birthday', 'role']
CUSTOMER_CSV_HEADERS = ['name', 'phone_number','address','birthday']

NUM_CUSTOMERS = 50