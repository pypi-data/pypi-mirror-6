"""
Django Unique Submission
"""

from setuptools import setup


setup(
        name='django-unique-submission',
        version='0.1',
        url='https://github.com/mengzhuo/django-unique-submission',
        license='BSD',
        author='Meng Zhuo',
        author_email='mengzhuo1203@gmail.com',
        description=('Django unique submission preventing duplicate post data'),
        long_description = __doc__,
        packages=['django_unique_submission'],
        zip_safe=False,
        include_package_data=True,
        platforms='any',
        install_requires=['Django>=1.4',],
            classifiers=[
                        'Environment :: Web Environment',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: BSD License',
                        'Operating System :: OS Independent',
                        'Programming Language :: Python',
                        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                        'Topic :: Software Development :: Libraries :: Python Modules'            ]
)
