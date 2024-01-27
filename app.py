from flask import Flask, jsonify, request
from commands.base import Invoker
from commands.nextcloud_command import NextCloudCommand, NextCloudReceiver
from commands.odoo_command import OdooCommand, OdooReceiver
from commands.store import UserOnboardingData
from services.mail import MailService
from services.odoo import OdooService
from services.storage import NextCloudService
from templates import offboarding_email_template, onboarding_email_template
from utils import get_error_chain

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
        
def failure_response(message: str, status_code: int = 400, errors: list = []):
    return jsonify({
        'message': message,
        'errors': errors,
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
    
    onboarding_data = UserOnboardingData(
        name=name,
        work_phone=work_phone,
        private_email=private_email,
    )
    invoker = Invoker()

    try:
        invoker.execute(OdooCommand(
            receiver=OdooReceiver(odoo_service),
            onboarding_data=onboarding_data,
        ))
        invoker.execute(NextCloudCommand(
            receiver=NextCloudReceiver(nextcloud_service),
            onboarding_data=onboarding_data,
        ))

        # Send email
        try:
            email_data = onboarding_email_template(onboarding_data.name, onboarding_data.company_email, onboarding_data.password)
            mail_service.send_email(
                onboarding_data.private_email,
                email_data.subject,
                email_data.body
            )
            print(f"Correo enviado a '{onboarding_data.private_email}'")
        except Exception as e:
            raise Exception("Error al enviar el correo con Sendgrid") from e

    except Exception as e:
        print("Cancelando proceso de onboarding")
        invoker.undo_all()
        message = f'Error al ejecutar el proceso de onboarding'
        errors = [error['message'] for error in get_error_chain(e)]
        return failure_response(message, errors=errors)
    
    message = f'Proceso de onboarding completado para usuario {onboarding_data.name} ({onboarding_data.company_email})'
    print(message)
    return success_response({
        "message": message
    })


@app.post('/offboarding')
def offboarding():
    try:
        email = get_from_request('email')
    except Exception as e:
        return failure_response(str(e))
    
    user_exists = False

    # Odoo: delete user and employee
    try:
        user = odoo_service.find_user_by_email(email)
        if not user:
            print('No se encontró el usuario en Odoo')
        else:
            user_exists = True
            odoo_service.delete_user(user[0]['id'])
            print('Usuario eliminado de Odoo')

        employee = odoo_service.find_employee_by_email(email)
        if not employee:
            print('No se encontró el empleado en Odoo')
        else:
            user_exists = True
            employee_name = employee[0]['name']
            employee_private_email = employee[0]['private_email']
            odoo_service.delete_employee(employee[0]['id'])
            print('Empleado eliminado de Odoo')
    except Exception as e:
        message = f'Error al eliminar el empleado'
        print(message)
        print(e)
        return failure_response(message, errors=[str(e)])

    # Nextcloud (storage): delete user
    try:
        user = nextcloud_service.get_user_by_id(email)
        if not user:
            print('No se encontró el usuario en Nextcloud')
        else:
            user_exists = True
            nextcloud_service.delete_user(email)
            print('Usuario eliminado de Nextcloud')
    except Exception as e:
        message = f'Error al eliminar el usuario de Nextcloud'
        print(message)
        print(e)
        return failure_response(message, errors=[str(e)])

    # Send email
    if not employee:
        if user_exists:
            message = f"Usuario '{email}' eliminado de las plataformas de la empresa"
            print(message)
            return success_response({
                "message": message
            })
        else:
            message = f"No se pudo encontrar al usuario con el correo '{email}' en las plataformas de la empresa"
            print(message)
            return failure_response(message)

    try:
        email_data = offboarding_email_template(employee_name)
        mail_service.send_email(
            employee_private_email,
            email_data.subject,
            email_data.body
        )
        print(f"Se ha enviado un correo a '{employee_private_email}'")
    except Exception as e:
        message = f'Error al enviar el correo con Sendgrid'
        print(message)
        print(e)
        return failure_response(message, errors=[str(e)])
    
    message = f"Proceso de offboarding completado para usuario con correo electrónico '{email}'"
    print(message)
    return success_response({
        "message": message
    })
