from typing import NamedTuple


EmailTemplate = NamedTuple("EmailTemplate", [
    ("subject", str), 
    ("body", str)
])

def onboarding_email_template(name: str, email: str, password: str) -> EmailTemplate:
    return EmailTemplate(
        subject = "Bienvenido/a",
        body = f"""
        Estimado/a <b>{name}</b>,
        <br/><br/>
        Bienvenido/a a nuestra empresa. De ahora en adelante tendrás acceso a los servicios internos de la empresa (correo, almacenamiento, etc.).<br/><br/>Tu correo electrónico empresarial es: 
        <pre>{email}</pre><br/>
        Tu contraseña temporal en la plataforma de almacenamiento es: <pre>{password}</pre><br/>
        Por favor, no compartas esta información con nadie y procura cambiar tu contraseña lo antes posible.
        <br/><br/>
        Saludos cordiales,<br/>
        Equipo de RRHH
        """
    )

def offboarding_email_template(name: str) -> EmailTemplate:
    return EmailTemplate(
        subject = "Desvinculación",
        body = f"""
        Estimado/a <b>{name}</b>,
        <br><br>
        Gracias por haber sido parte de nuestra empresa. A partir de este momento no tendrás más acceso a los servicios internos de la empresa (correo, almacenamiento, etc.). 
        <br><br>
        Si tienes alguna duda o comentario, por favor comunícate con el departamento de RRHH.
        <br><br>
        Saludos cordiales,<br>
        Equipo de RRHH
        """
    )