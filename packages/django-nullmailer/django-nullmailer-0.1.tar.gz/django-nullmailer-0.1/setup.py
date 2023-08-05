from setuptools import setup
setup(
    name='django-nullmailer',
    version='0.1',
    author='20Tab S.r.l.',
    author_email='info@20tab.com',
    description='A django EMAIL_BACKEND for enqueuing mail in nullmailer spool system.',
    url='https://github.com/20tab/django-nullmailer',
    packages=['nullmailer'],
)
