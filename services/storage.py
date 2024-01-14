import requests

from config import NextCloudConfig

class NextCloudService:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = f'{NextCloudConfig.NEXTCLOUD_URL}/ocs/v1.php/cloud'
        self.session.auth = (NextCloudConfig.NEXTCLOUD_USER, NextCloudConfig.NEXTCLOUD_PASSWORD)
        self.session.headers.update({
            'Accept': 'application/json',
            'OCS-APIRequest': 'true'
        })

    def create_user(self, user_data):
        # Create the user
        duplicate_user = self.get_user_by_id(user_data['email'])
        if duplicate_user:
            raise Exception('Ya existe un usuario con ese correo electrónico')
        response = self.session.post(
            f'{self.base_url}/users',
            data={
                'userid': user_data['email'],
                'password': user_data['password'],
                'displayName': user_data['name'],
                'email': user_data['email'],
                'quota': user_data['quota_in_gb'] * 1024 * 1024 * 1024,
            }
        )
        content = response.json()
        if not self._is_success(content):
            raise Exception('Error al crear el usuario')
        return self._extract_data(content)['id']

    def get_user_by_id(self, user_id) -> dict | None:
        # Get the user by id
        response = self.session.get(f'{self.base_url}/users/{user_id}')
        content = response.json()
        if not self._is_success(content):
            return None
        return self._extract_data(content)

    def delete_user(self, user_id): # User ID is the email
        # Delete the user
        user_exists = self.get_user_by_id(user_id)
        if not user_exists:
            raise Exception(f'No se encontró el usuario con ID {user_id}')
        response = self.session.delete(f'{self.base_url}/users/{user_id}')
        content = response.json()
        if not self._is_success(content):
            raise Exception('Error al eliminar el usuario')

    def _is_success(self, content):
        return content['ocs']['meta']['status'] == 'ok'
    
    def _extract_data(self, content):
        return content['ocs']['data']
