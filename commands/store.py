from utils import create_user_email, generate_password


class UserOnboardingData:
    name: str
    work_phone: str
    private_email: str
    company_email: str
    password: str

    def __init__(
        self,
        name: str,
        work_phone: str,
        private_email: str,
        company_domain: str = "example.com",
    ):
        self.name = name
        self.work_phone = work_phone
        self.private_email = private_email
        self.company_email = create_user_email(name, company_domain)
        self.password = generate_password()
