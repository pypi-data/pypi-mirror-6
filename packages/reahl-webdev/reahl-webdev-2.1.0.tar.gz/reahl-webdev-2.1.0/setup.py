from setuptools import setup
setup(
    name='reahl-webdev',
    version=u'2.1.0',
    description='Web-specific development tools for Reahl.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl development tools for testing and working with web based programs.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.webdev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-web>=2.1,<2.2', u'reahl-dev>=2.1,<2.2', u'reahl-component>=2.1,<2.2', u'reahl-tofu>=2.1,<2.2', u'lxml>=3.2', u'WebTest>=1.4,<1.5', u'selenium>=2.25,<2.27'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.1,<2.2', u'reahl-stubble>=2.1,<2.2'],
    test_suite='tests',
    entry_points={
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.dev.commands': [
            u'ServeCurrentProject = reahl.webdev.commands:ServeCurrentProject'    ],
                 },
    extras_require={u'pillow': [u'pillow>=1.7.8,<1.999']}
)
