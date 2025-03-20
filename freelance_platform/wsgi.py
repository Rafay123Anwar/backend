import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_platform.settings')

app = get_wsgi_application()  # This should be `app`, not `application`
