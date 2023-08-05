from setuptools import setup
setup(
    name='reahl-tofu',
    version=u'2.0.0a3',
    description='A testing framework that couples fixtures and tests loosely.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language. . Tofu is a plugin for nosetests, and part of the Reahl development tools. . Tofu allows you to have a hierarchy of test fixtures that is *completely* decoupled from your hierarchy of tests or test suites. Tofu includes a number of other related test utilities. . Tofu can also be used to run the set_ups of fixtures from the command line.  This is useful for acceptance tests whose fixtures create data in databases that can be used for demonstration and user testing. ',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['tofu_test', 'examples', 'reahl', 'devenv', 'reahl.tofu'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-component>=2.0.0a3,<2.1', u'nose'],
    setup_requires=[],
    tests_require=[u'reahl-stubble>=2.0.0a3,<2.1'],
    test_suite=u'reahl.tofu_dev',
    entry_points={
        u'nose.plugins.0.10': [
            u'run-fixture = reahl.tofu.nosesupport:RunFixturePlugin',
            u'long-output = reahl.tofu.nosesupport:LongOutputPlugin',
            u'test-directory = reahl.tofu.nosesupport:TestDirectoryPlugin',
            u'log-level = reahl.tofu.nosesupport:LogLevelPlugin',
            u'setup-fixture = reahl.tofu.nosesupport:SetUpFixturePlugin'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={}
)
