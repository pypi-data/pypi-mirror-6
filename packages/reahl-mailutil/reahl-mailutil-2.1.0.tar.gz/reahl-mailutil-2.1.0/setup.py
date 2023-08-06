from setuptools import setup
setup(
    name='reahl-mailutil',
    version=u'2.1.0',
    description='Simple utilities for sending email from Reahl.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-mailutil is a simple library for sending emails (optionally from ReST sources).\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.mailutil_dev', 'reahl.mailutil'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-component>=2.1,<2.2', u'docutils>=0.8,<0.9'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.1,<2.2', u'reahl-stubble>=2.1,<2.2'],
    test_suite=u'reahl.mailutil_dev',
    entry_points={
        u'reahl.configspec': [
            u'config = reahl.mailutil.reusableconfig:MailConfig'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={}
)
