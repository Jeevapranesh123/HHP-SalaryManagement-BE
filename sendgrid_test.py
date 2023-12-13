from app.api.lib.SendGrid import SendGrid
import asyncio

sendgrid = SendGrid()


async def send_email():
    await sendgrid.send_onboarding_email(
        "jpranesh14@gmail.com", "Jeeva Pranesh", "test"
    )


asyncio.run(send_email())
