__author__ = 'sathley'

from pyappacitive import AppacitiveEmail


def send_email_test_with_config():
    AppacitiveEmail.send_raw_email(['sathley@appacitive.com'], 'hello from py sdk', 'Wazza!', smtp={
        "username": "sathley@appacitive.com",
		"password": "########",
		"host": "smtp.gmail.com",
		"port": 465,
		"enablessl": True
    }, from_email='sathley@appacitive.com')


def send_email_test_without_config():
    AppacitiveEmail.send_raw_email(['sathley@appacitive.com'], 'hello from py sdk', 'Wazza!', from_email='sathley@appacitive.com')


def send_templated_email_test():
    AppacitiveEmail.send_templated_email(['sathley@appacitive.com'], 'Hello from py sdk', 'sample', {
        'username': 'john.doe',
        'firstname': 'John',
        'lastname': 'Doe'
    }, [], [], from_email='sathley@appacitive.com')
