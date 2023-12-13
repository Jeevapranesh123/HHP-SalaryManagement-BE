import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGrid:
    def __init__(self):
        self.sg_client = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        self.sender = "contact@zuvatech.com"
        self.portal_link = "http://localhost:3000/"

    async def read_template(self, filename):
        cwd = os.getcwd()
        print(cwd)
        filename = os.path.join(cwd, filename)
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()

    async def send_onboarding_email(self, email, name, password):
        subject = "Welcome to Hindustan Salary Management System"
        html_content = await self.read_template("app/api/templates/onboarding.html")
        html_content = html_content.replace("{{employee_name}}", name)
        html_content = html_content.replace("{{employee_password}}", password)
        html_content = html_content.replace("{{employee_email}}", email)
        print(html_content)
        # message = Mail(
        #     from_email=self.sender,
        #     to_emails=email,
        #     subject=subject,
        #     html_content=html_content,
        # )

        # await self.send(message)

    async def send(self, message):
        try:
            response = self.sg_client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
