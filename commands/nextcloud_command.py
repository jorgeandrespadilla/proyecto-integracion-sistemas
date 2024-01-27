from commands.base import ICommand
from commands.store import UserOnboardingData
from services.storage import NextCloudService


class NextCloudReceiver:
    def __init__(self, nextcloud_service: NextCloudService) -> None:
        self._nextcloud_service = nextcloud_service
        self._user_id: str = None

    def get_user_id(self) -> str:
        return self._user_id

    def create_user(self, data: dict) -> str:
        self._user_id = self._nextcloud_service.create_user(data)
        return self._user_id
    
    def delete_user(self) -> None:
        if not self._user_id:
            print("No se puede eliminar el usuario porque no existe")
            return
        self._nextcloud_service.delete_user(self._user_id)


class NextCloudCommand(ICommand):
    def __init__(self, receiver: NextCloudReceiver, onboarding_data: UserOnboardingData) -> None:
        super().__init__()
        self._receiver = receiver
        self._onboarding_data = onboarding_data
        
    def execute(self) -> None:
        try:
            print("Creando cuenta en NextCloud")
            user_id = self._receiver.create_user({
                'email': self._onboarding_data.private_email,
                'password': self._onboarding_data.password,
                'name': self._onboarding_data.name,
                'quota_in_gb': 5,
            })
            print("Cuenta creada en NextCloud")
        except Exception as e:
            raise Exception("Error al crear la cuenta en NextCloud") from e

    def undo(self) -> None:
        print("Eliminando usuario en NextCloud")
        self._receiver.delete_user()
