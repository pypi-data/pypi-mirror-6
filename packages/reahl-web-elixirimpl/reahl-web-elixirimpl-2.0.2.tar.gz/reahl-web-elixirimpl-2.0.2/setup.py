from setuptools import setup
setup(
    name='reahl-web-elixirimpl',
    version=u'2.0.2',
    description='An implementation of Reahl persisted classes using Elixir.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nSome core elements of Reahl can be implemented for use with different persistence technologies. This is such an implementation based on SqlAlchemy/Elixir.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.webelixirimpl_dev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-interfaces>=2.0,<2.1', u'reahl-sqlalchemysupport>=2.0,<2.1', u'reahl-web>=2.0,<2.1', u'reahl-component>=2.0,<2.1', u'reahl-domain>=2.0,<2.1'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0,<2.1', u'reahl-stubble>=2.0,<2.1', u'reahl-dev>=2.0,<2.1', u'reahl-webdev>=2.0,<2.1'],
    test_suite=u'reahl.webelixirimpl_dev',
    entry_points={
        u'reahl.configspec': [
            u'config = reahl.webelixirimpl:ElixirImplConfig'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.persistlist': [
            u'0 = reahl.webelixirimpl:WebUserSession',
            u'1 = reahl.webelixirimpl:SessionData',
            u'2 = reahl.webelixirimpl:UserInput',
            u'3 = reahl.webelixirimpl:PersistedException',
            u'4 = reahl.webelixirimpl:PersistedFile'    ],
                 },
    extras_require={}
)
