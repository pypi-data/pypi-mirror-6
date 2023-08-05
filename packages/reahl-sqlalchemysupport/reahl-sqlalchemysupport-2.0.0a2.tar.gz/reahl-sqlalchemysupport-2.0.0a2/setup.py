from setuptools import setup
setup(
    name='reahl-sqlalchemysupport',
    version=u'2.0.0a2',
    description='Support for using SqlAlchemy with Reahl.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language. . This package contains infrastructure necessary to use Reahl with SqlAlchemy or Elixir. ',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-component>=2.0.0a2,<2.1', u'sqlalchemy>=0.7,<0.7.999', u'alembic>=0.5,<0.5.999'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0.0a2,<2.1', u'reahl-stubble>=2.0.0a2,<2.1'],
    test_suite=u'reahl.sqlalchemysupport_dev',
    entry_points={
        u'reahl.configspec': [
            u'config = reahl.sqlalchemysupport:SqlAlchemyConfig'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.persistlist': [
            u'0 = reahl.sqlalchemysupport:SchemaVersion'    ],
                 },
    extras_require={}
)
