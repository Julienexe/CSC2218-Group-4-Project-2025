class EmailClient:
    """
    Hypothetical third-party email library client.
    """
    def __init__(self, smtp_server: str, port: int):
        self.smtp_server = smtp_server
        self.port = port
    def send_mail(self, from_addr: str, to_addr: str, subject: str, body: str) -> None:
        # Implementation that sends email via SMTP
        print(f"[EMAILCLIENT] Sending email from {from_addr} to {to_addr}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")