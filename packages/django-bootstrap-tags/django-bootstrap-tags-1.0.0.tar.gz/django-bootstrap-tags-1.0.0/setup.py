from setuptools import setup, find_packages

setup(
    name = "django-bootstrap-tags",
    version = "1.0.0",
    packages = find_packages(),
    install_requires = ['django>=1.5'],
    author = "A.J. May",
    author_email = "aj7may@gmail.com",
    description = "A django form widget and tag model to add typeahead tagging to any form.",
    license = "Creative Commons Attribution-ShareAlike 4.0 International License",
    keywords = "django bootstrap tags tagging form widget typeahead",
    url = "http://thegoods.aj7may.com/django-bootstrap-tags",
    zip_safe = False,
    package_data = {
        'django_password_strength': [
            'static/js/*',
            'static/css/*',
            'templates/*',
        ],
    },
)