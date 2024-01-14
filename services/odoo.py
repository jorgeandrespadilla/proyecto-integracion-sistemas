import xmlrpc.client

from config import OdooConfig
    
class OdooService:

    def __init__(self):
        # Connect to the Odoo server
        self.common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(OdooConfig.ODOO_URL))
        self.uid = self.common.authenticate(OdooConfig.ODOO_DB_NAME, OdooConfig.ODOO_USER, OdooConfig.ODOO_PASSWORD, {})
        # Create a connection to the Odoo API
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(OdooConfig.ODOO_URL))

    def create_employee(self, employee_data):
        # Create the employee
        employee_email = employee_data['work_email']
        duplicated_employee = self.find_employee_by_email(employee_email)
        if duplicated_employee:
            raise Exception(f'Ya se encuentra registrado un empleado con el correo electrónico {employee_email} en Odoo')
        employee_id = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'create',
            [employee_data]
        )
        return employee_id
    
    def create_user(self, user_data):
        # Create the user
        user_email = user_data['email']
        duplicated_user = self.find_user_by_email(user_email)
        if duplicated_user:
            raise Exception(f'Ya se encuentra registrado un usuario con el correo electrónico {user_email} en Odoo')
        user_id = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'res.users', 'create',
            [user_data]
        )
        return user_id
    
    def get_user_by_id(self, user_id) -> dict | None:
        # Get the user by id
        user_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'res.users', 'search_read',
            [[['id', '=', user_id]]],
            {'fields': ['id', 'name', 'login', 'email', 'employee_id', 'employee_ids']}
        )
        return user_ids[0] if user_ids else None

    def get_employee_by_id(self, employee_id) -> dict | None:
        # Get the employee by id
        employee_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'search_read',
            [[['id', '=', employee_id]]],
            {'fields': ['id', 'name', 'work_email']}
        )
        return employee_ids[0] if employee_ids else None
    
    def find_user_by_email(self, email) -> dict | None:
        # Get the user by email
        user_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'res.users', 'search_read',
            [[['email', '=', email]]],
            {'fields': ['id', 'name', 'login', 'email', 'employee_id', 'employee_ids']}
        )
        return user_ids
    
    def find_employee_by_email(self, email):
        # Get the employee by email
        employee_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'search_read',
            [[['work_email', '=', email]]],
            {'fields': ['id', 'name', 'work_email', 'private_email']}
        )
        return employee_ids
    
    def delete_user(self, user_id):
        # Delete the user
        user_exists = self.get_user_by_id(user_id)
        if not user_exists:
            raise Exception(f'No se encontró el usuario con ID {user_id}')
        self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'res.users', 'unlink',
            [[user_id]]
        )

    def delete_employee(self, employee_id):
        # Delete the employee
        employee_exists = self.get_employee_by_id(employee_id)
        if not employee_exists:
            raise Exception(f'No se encontró el empleado con ID {employee_id}')
        self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'unlink',
            [[employee_id]]
        )

    def get_jobs(self):
        # Get available jobs
        job_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.job', 'search_read',
            [[]],
            {'fields': ['id', 'name']}
        )
        return job_ids
    
    def get_departments(self):
        # Get available departments
        department_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.department', 'search_read',
            [[]],
            {'fields': ['id', 'name']}
        )
        return department_ids
    
