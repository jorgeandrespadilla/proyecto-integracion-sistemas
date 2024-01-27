from commands.base import CompositeCommand, ICommand
from commands.store import UserOnboardingData
from services.odoo import OdooService


class OdooReceiver:
    def __init__(self, odoo_service: OdooService) -> None:
        self._odoo_service = odoo_service
        self._employee_id: any = None
        self._user_id: any = None

    def get_employee_id(self) -> int:
        return self._employee_id
    
    def get_user_id(self) -> int:
        return self._user_id

    def create_employee(self, data: dict) -> int:
        self._employee_id = self._odoo_service.create_employee(data)
        return self._employee_id
    
    def create_user(self, data: dict) -> int:
        self._user_id = self._odoo_service.create_user(data)
        return self._user_id
    
    def delete_employee(self) -> None:
        if not self._employee_id:
            print("No se puede eliminar el empleado porque no existe")
            return
        self._odoo_service.delete_employee(self._employee_id)

    def delete_user(self) -> None:
        if not self._user_id:
            print("No se puede eliminar el usuario porque no existe")
            return
        self._odoo_service.delete_user(self._user_id)


class OdooCommand(CompositeCommand):
    def __init__(self, receiver: OdooReceiver, onboarding_data: UserOnboardingData) -> None:
        super().__init__()
        self._receiver = receiver
        self._onboarding_data = onboarding_data
        self.add(OdooCreateEmployeeCommand(receiver, onboarding_data))
        self.add(OdooCreateUserCommand(receiver, onboarding_data))
        
    def execute(self) -> None:
        print("Ejecutando onboarding en Odoo")
        try:
            super().execute()
        except Exception as e:
            raise Exception("Error al ejecutar el onboarding en Odoo") from e

    def undo(self) -> None:
        print("Revirtiendo onboarding en Odoo")
        super().undo()


class OdooCreateEmployeeCommand(ICommand):
    def __init__(self, receiver: OdooReceiver, onboarding_data: UserOnboardingData) -> None:
        self._receiver = receiver
        self._onboarding_data = onboarding_data
    
    def execute(self) -> None:
        try:
            print("Creando empleado en Odoo")
            employee_id = self._receiver.create_employee({
                'name': self._onboarding_data.name,
                'work_phone': self._onboarding_data.work_phone,
                'work_email': self._onboarding_data.company_email,
                'private_email': self._onboarding_data.private_email,
            })
            print(f'Empleado creado en Odoo con ID {employee_id}')
        except Exception as e:
            raise Exception("Error al crear el empleado en Odoo") from e

    def undo(self) -> None:
        print("Eliminando empleado en Odoo")
        self._receiver.delete_employee()


class OdooCreateUserCommand(ICommand):
    def __init__(self, receiver: OdooReceiver, onboarding_data: UserOnboardingData) -> None:
        self._receiver = receiver
        self._onboarding_data = onboarding_data
    
    def execute(self) -> None:
        try:
            print("Creando usuario en Odoo")
            user_id = self._receiver.create_user({
                'name': self._onboarding_data.name,
                'login': self._onboarding_data.company_email,
                'email': self._onboarding_data.company_email,
                'password': self._onboarding_data.password,
                'employee_ids': [self._receiver.get_employee_id()],
            })
            print(f'Usuario creado en Odoo con ID {user_id}')
        except Exception as e:
            raise Exception("Error al crear el usuario en Odoo") from e

    def undo(self) -> None:
        print("Eliminando usuario en Odoo")
        self._receiver.delete_user()
