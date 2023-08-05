import mandrill
from django.conf import settings


class EmailMessage:
    """
    Sends an email.
    
    Args:
        sender (dict):
            email(string) - The sender's email address.
            name (string) - The sender's name.
        recipients (array[dict]):
            email (string) - The recipient's email.
            name (string, optional) - The recipient's name.
        subject (string) - The email's subject.
        text_content (string) - The email content in plaintext.
        html_content (string, optional) - The email content in html.
        metadata (dict, optional) - Metadata.
        tags (array[string], optional) - Tags.
    """
    
    def __init__(self, sender, recipients, subject, text_content, html_content=None, metadata=None, tags=None):
        """
        Constructor.
        """
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.text_content = text_content
        self.html_content = html_content
        self.metadata = metadata
        self.tags = tags
    
    def send(self):
        """
        Raises:
          InvalidTemplateError: The given template name already exists or contains invalid characters
        """
        
        # Build message and send.
        mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
        message = {
             'auto_html': True,
             'auto_text': False,
             'from_email': self.sender['email'],
             'from_name': self.sender['name'],
             'important': False,
             'inline_css': None,
             'preserve_recipients': None,
             'signing_domain': None,
             'subject': self.subject,
             'text': self.text_content,
             'to': self.recipients,
             'track_clicks': True,
             'track_opens': True,
             'url_strip_qs': None
        }
        
        # If html content provided.
        if self.html_content:
            message['html'] = self.html_content
        
        # If metadata provided.
        if self.metadata:
            message['metadata'] = self.metadata
            
        # If tags are provided.
        if self.tags:
            message['tags'] = self.tags
        
        # Send.
        result = mandrill_client.messages.send(message=message)
        
        # Process result.
        for r in result:
            # Check if email wasn't sent.
            if r['status'] != 'sent' and r['status'] != 'queued':
                return {
                    'sent': False,
                    'result': result
                }
                
        # If this point is reached, email was sent successfully.
        return { 'sent': True }