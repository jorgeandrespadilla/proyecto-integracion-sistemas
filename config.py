from dotenv import dotenv_values

env_values = dotenv_values()

class MailConfig:
    SENDGRID_API_KEY = env_values['SENDGRID_API_KEY']
    SENDER_EMAIL = env_values['SENDER_EMAIL']

class OdooConfig:
    ODOO_URL = env_values['ODOO_URL']
    ODOO_DB_NAME = env_values['ODOO_DB_NAME']
    ODOO_USER = env_values['ODOO_USER']
    ODOO_PASSWORD = env_values['ODOO_PASSWORD']

class NextCloudConfig:
    NEXTCLOUD_URL = env_values['NEXTCLOUD_URL']
    NEXTCLOUD_USER = env_values['NEXTCLOUD_USER']
    NEXTCLOUD_PASSWORD = env_values['NEXTCLOUD_PASSWORD']
