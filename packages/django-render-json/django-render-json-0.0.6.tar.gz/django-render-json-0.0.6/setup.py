from distutils.core import setup

setup(
    name='django-render-json',
    version='0.0.6',
    author='jarvys',
    author_email='yuhan534@126.com',
	url='https://github.com/jarvys/django-render-json',
    py_modules=['django_render_json'],
    install_requires=[
        'django>=1.6'
    ],
	keywords=['django', 'json', 'response', 'http']
)
