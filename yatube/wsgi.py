import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
# from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')

application = get_wsgi_application()
# application = WhiteNoise(application, root='/path/to/static/files')
# application.add_files('/path/to/more/static/files', prefix='more-files/')
# application = WhiteNoise(application)
