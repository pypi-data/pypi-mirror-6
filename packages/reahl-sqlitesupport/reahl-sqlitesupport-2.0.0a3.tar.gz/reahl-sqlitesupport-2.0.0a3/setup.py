from setuptools import setup
setup(
    name='reahl-sqlitesupport',
    version=u'2.0.0a3',
    description='Support for using Sqlite with Reahl.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language. . This package contains infrastructure necessary to use Reahl with Sqlite. ',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-component>=2.0.0a3,<2.1'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0.0a3,<2.1', u'reahl-stubble>=2.0.0a3,<2.1'],
    test_suite='tests',
    entry_points={
        u'reahl.component.databasecontrols': [
            u'SQLiteControl = reahl.sqlitesupport:SQLiteControl'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={}
)
