from flask import Flask
from services.mail import MailService
from services.odoo import OdooService
from services.storage import NextCloudService
from templates import offboarding_email_template, onboarding_email_template
from utils import create_user_email, generate_password

app = Flask(__name__)

mail_service = MailService()
odoo_service = OdooService()
nextcloud_service = NextCloudService()

def add(name: str, work_phone: str, private_email: str):
    email = create_user_email(name, 'example.com')

    # Odoo: create user and employee
    try:
        employee_id = odoo_service.create_employee({
            'name': name,
            'work_phone': work_phone,
            'work_email': email,
            'private_email': private_email,
        })
        print(f'Empleado creado con ID {employee_id}')

        user_id = odoo_service.create_user({
            'name': name,
            'login': email,
            'email': email,
            'employee_ids': [employee_id],
        })
        print(f'Usuario creado con ID {user_id}')

    except Exception as e:
        print(f'Error al crear el empleado: {e}')

    # Nextcloud (storage): create user
    try:
        password = generate_password()
        nextcloud_service.create_user({
            'email': email,
            'password': password,
            'name': name,
            'quota_in_gb': 5,
        })
        print(f'Usuario creado en Nextcloud')
    except Exception as e:
        print(f'Error al crear el usuario de Nextcloud: {e}')

    # Send email
    try:
        email_data = onboarding_email_template(name, email, password)
        mail_service.send(
            private_email,
            email_data.subject,
            email_data.body
        )
        print(f"Se ha enviado un correo a '{private_email}' con las instrucciones")
    except Exception as e:
        print(f'Error al enviar el correo: {e}')


def delete(email: str):
    # Odoo: delete user and employee
    try:
        user = odoo_service.find_user_by_email(email)
        if not user:
            print('No se encontró el usuario')
        else:
            odoo_service.delete_user(user[0]['id'])
            print('Usuario eliminado')

        employee = odoo_service.find_employee_by_email(email)
        if not employee:
            print('No se encontró el empleado')
        else:
            employee_name = employee[0]['name']
            employee_private_email = employee[0]['private_email']
            odoo_service.delete_employee(employee[0]['id'])
            print('Empleado eliminado')
    except Exception as e:
        print(f'Error al eliminar el empleado: {e}')

    # Nextcloud (storage): delete user
    try:
        nextcloud_service.delete_user(email)
        print('Usuario eliminado de Nextcloud')
    except Exception as e:
        print(f'Error al eliminar el usuario de Nextcloud: {e}')

    # Send email
    try:
        email_data = offboarding_email_template(employee_name)
        mail_service.send(
            employee_private_email,
            email_data.subject,
            email_data.body
        )
        print(f"Se ha enviado un correo a '{employee_private_email}' con el aviso")
    except Exception as e:
        print(f'Error al enviar el correo: {e}')

# add('Juan Perez', '1234567890', 'user@gmail.com')
# delete('juan.perez@example.com')
