import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

template_config = {
    "onboarding": {
        "subject": "Welcome to Hindustan Salary Management System",
        "template": "onboarding.html",
    },
    "forgot_password": {
        "subject": "Reset Password",
        "template": "forgot_password.html",
    },
}

TEMPLATE_DIR = os.path.join(os.getcwd(), "app/templates")


class SendGrid:
    def __init__(self):
        self.sg_client = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        self.sender = "contact@zuvatech.com"
        self.portal_link = "http://localhost:3000/"
        self.template_config = template_config
        self.TEMPLATE_DIR = TEMPLATE_DIR

    async def read_template(self, filename):
        filename = os.path.join(self.TEMPLATE_DIR, filename)
        print(filename)
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(e)
            return ""

    async def send_onboarding_email(self, email, name, password):
        html_content = await self.read_template(
            self.template_config["onboarding"]["template"]
        )
        html_content = html_content.replace("{{ employee_name }}", name)
        html_content = html_content.replace("{{ employee_password }}", password)
        html_content = html_content.replace("{{ employee_email }}", email)
        html_content = html_content.replace("{{ portal_link }}", self.portal_link)

        message = Mail(
            from_email=self.sender,
            to_emails=email,
            subject=self.template_config["onboarding"]["subject"],
            html_content=html_content,
        )

        await self.send(message)

    async def send(self, message):
        try:
            response = self.sg_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
