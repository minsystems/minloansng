EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'minacademy'
EMAIL_HOST_PASSWORD = "FReakyboygeniuse123"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "customer@minloans.com.ng"
SUPPORT_EMAIL = "support@minloans.com.ng"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Minloans"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
SENDGRID_API_KEY = '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'

# message = Mail(
#     from_email=DEFAULT_FROM_EMAIL,
#     to_emails='mathegeniuse@gmail.com',
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>'
# )
#
# try:
#     sg = SendGridAPIClient(SENDGRID_API_KEY)
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(e.message)