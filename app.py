from flask import Flask, jsonify, request
from services.mail import MailService
from services.odoo import OdooService
from services.storage import NextCloudService
from templates import offboarding_email_template, onboarding_email_template
from utils import create_user_email, generate_password

app = Flask(__name__)

mail_service = MailService()
odoo_service = OdooService()
nextcloud_service = NextCloudService()

def get_from_request(key: str, required: bool = True):
    content = request.json
    if key not in content:
        if required:
            raise Exception(f"'{key}' is required")
        else:
            return None
    return content[key]

def success_response(data: dict = {}, status_code: int = 200):
    return jsonify(data), status_code
        
def failure_response(message: str, status_code: int = 400):
    return jsonify({
        'message': message,
    }), status_code

@app.get('/')
def api():
    return 'API is running'

@app.post('/onboarding')
def onboarding():
    try:
        name = get_from_request('name')
        work_phone = get_from_request('work_phone')
        private_email = get_from_request('private_email')
    except Exception as e:
        return failure_response(str(e))
    
    email = create_user_email(name, "example.com")
    password = generate_password()

    # Odoo: create user and employee
    try:
        employee_id = odoo_service.create_employee({
            'name': name,
            'work_phone': work_phone,
            'work_email': email,
            'private_email': private_email,
        })
        print(f'Odoo - Empleado creado con ID {employee_id}')

        user_id = odoo_service.create_user({
            'name': name,
            'login': email,
            'email': email,
            'password': password,
            'employee_ids': [employee_id],
        })
        print(f'Odoo - Usuario creado con ID {user_id}')

    except Exception as e:
        print(f'Odoo - Error al crear el empleado: {e}')
        return failure_response(str(e))

    # Nextcloud (storage): create user
    try:
        nextcloud_service.create_user({
            'email': email,
            'password': password,
            'name': name,
            'quota_in_gb': 5,
        })
        print(f'Nextcloud - Usuario creado')
    except Exception as e:
        print(f'Nextcloud - Error al crear el usuario de Nextcloud: {e}')
        return failure_response(str(e))

    # Send email
    try:
        email_data = onboarding_email_template(name, email, password)
        mail_service.send_email(
            private_email,
            email_data.subject,
            email_data.body
        )
        print(f"Sendgrid - Se ha enviado un correo a '{private_email}' con las instrucciones")
    except Exception as e:
        print(f'Sendgrid - Error al enviar el correo: {e}')
        return failure_response("Sendgrid - Error al enviar el correo")

    return success_response(f"Usuario creado ({email})")


@app.post('/offboarding')
def offboarding():
    try:
        email = get_from_request('email')
    except Exception as e:
        return failure_response(str(e))

    # Odoo: delete user and employee
    try:
        user = odoo_service.find_user_by_email(email)
        if not user:
            print('Odoo - No se encontró el usuario')
        else:
            odoo_service.delete_user(user[0]['id'])
            print('Odoo - Usuario eliminado')

        employee = odoo_service.find_employee_by_email(email)
        if not employee:
            print('Odoo - No se encontró el empleado')
        else:
            employee_name = employee[0]['name']
            employee_private_email = employee[0]['private_email']
            odoo_service.delete_employee(employee[0]['id'])
            print('Odoo - Empleado eliminado')
    except Exception as e:
        print(f'Odoo - Error al eliminar el empleado: {e}')
        return failure_response(str(e))

    # Nextcloud (storage): delete user
    try:
        nextcloud_service.delete_user(email)
        print('Nextcloud - Usuario eliminado de Nextcloud')
    except Exception as e:
        print(f'Nextcloud - Error al eliminar el usuario de Nextcloud: {e}')
        return failure_response(str(e))

    # Send email
    try:
        email_data = offboarding_email_template(employee_name)
        mail_service.send_email(
            employee_private_email,
            email_data.subject,
            email_data.body
        )
        print(f"Sendgrid - Se ha enviado un correo a '{employee_private_email}' con el aviso")
    except Exception as e:
        print(f'Sendgrid - Error al enviar el correo: {e}')
        return failure_response("Error al enviar el correo")

    return success_response()
