# -*- coding:utf-8 -*-
import setuptools

setuptools.setup(
    name="django-forumbr",
    version="0.4.0.1",
    packages=[
        "forum",
        "forum.templatetags",
    ],

    install_requires=[
        "django>=1.5",
        "pillow",
        "south"
    ],
    tests_require=[
        'django-registration'
    ],

    author="Italo Maia",
    author_email="italo.maia@gmail.com",
    url="https://bitbucket.org/italomaia/django-forumbr",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Simple and complete django forum solution",
    keywords="django forum python",
    include_package_data=True,
)
