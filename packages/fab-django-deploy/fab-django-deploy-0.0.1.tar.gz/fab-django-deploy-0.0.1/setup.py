from setuptools import setup


version = '0.0.1'


install_requires = (
    'fabric>=1.8',
)


setup(
    name='fab-django-deploy',
    py_modules=['fab_deploy'],
    version=version,
    description='',
    long_description='',
    author='incuna',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/fab-django-deploy/',
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
)
