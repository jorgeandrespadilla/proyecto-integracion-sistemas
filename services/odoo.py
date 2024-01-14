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
        duplicated_employee = self.get_employee_by_email(employee_email)
        if duplicated_employee:
            raise Exception(f'Ya se encuentra registrado un empleado con el correo electrónico {employee_email} en Odoo')
        employee_id = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'create',
            [employee_data]
        )
        return employee_id
    
    def get_employee_by_id(self, employee_id) -> dict | None:
        # Get the employee by id
        employee_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'search_read',
            [[['id', '=', employee_id]]],
            {'fields': ['id', 'name', 'work_email']}
        )
        return employee_ids[0] if employee_ids else None
    
    def find_employee_by_email(self, email):
        # Get the employee by email
        employee_ids = self.models.execute_kw(
            OdooConfig.ODOO_DB_NAME, self.uid, OdooConfig.ODOO_PASSWORD,
            'hr.employee', 'search_read',
            [[['work_email', '=', email]]],
            {'fields': ['id', 'name', 'work_email']}
        )
        return employee_ids
    
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
    
