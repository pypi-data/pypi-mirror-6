from setuptools import setup
setup(
    name='reahl-domainui',
    version=u'2.0.2',
    description='A user interface for reahl-domain.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis Reahl component contains a user interface for some of the domain functionality in reahl-domainui.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.messages', 'reahl.domainui_dev', 'reahl.domainui'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=[u'reahl-component>=2.0,<2.1', u'reahl-sqlalchemysupport>=2.0,<2.1', u'reahl-web>=2.0,<2.1', u'reahl-domain>=2.0,<2.1'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0,<2.1', u'reahl-stubble>=2.0,<2.1', u'reahl-dev>=2.0,<2.1', u'reahl-webdev>=2.0,<2.1', u'reahl-dev>=2.0,<2.1', u'reahl-webdev>=2.0,<2.1'],
    test_suite=u'reahl.domainui_dev',
    entry_points={
        'reahl.translations': [
            u'reahl-domainui = reahl.messages'    ],
        u'reahl.configspec': [
            u'config = reahl.domainuiegg:DomainUiConfig'    ],
        u'reahl.workflowui.task_widgets': [
            u'TaskWidget = reahl.domainui.workflow:TaskWidget'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={}
)
