from setuptools import setup
setup(
    name='reahl-domain',
    version=u'2.0.2',
    description='End-user domain functionality for use with Reahl.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis Reahl component includes functionality modelling user accounts, some simple workflow concepts and more.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.messages', 'reahl.domain_dev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=[u'reahl-component>=2.0,<2.1', u'reahl-mailutil>=2.0,<2.1', u'reahl-interfaces>=2.0,<2.1', u'reahl-sqlalchemysupport>=2.0,<2.1', u'elixir>=0.7,<0.8'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0,<2.1', u'reahl-stubble>=2.0,<2.1', u'reahl-dev>=2.0,<2.1'],
    test_suite=u'reahl.domain_dev',
    entry_points={
        'reahl.translations': [
            u'reahl-domain = reahl.messages'    ],
        u'reahl.configspec': [
            u'config = reahl.systemaccountmodel:SystemAccountConfig'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.scheduled_jobs': [
            u'DeferredAction.check_deadline = reahl.workflowmodel:DeferredAction.check_deadline',
            u'UserSession.remove_dead_sessions = reahl.systemaccountmodel:UserSession.remove_dead_sessions'    ],
        u'reahl.persistlist': [
            u'0 = reahl.partymodel:Party',
            u'1 = reahl.systemaccountmodel:SystemAccount',
            u'2 = reahl.systemaccountmodel:UserSession',
            u'3 = reahl.systemaccountmodel:EmailAndPasswordSystemAccount',
            u'4 = reahl.systemaccountmodel:AccountManagementInterface',
            u'5 = reahl.systemaccountmodel:VerificationRequest',
            u'6 = reahl.systemaccountmodel:VerifyEmailRequest',
            u'7 = reahl.systemaccountmodel:NewPasswordRequest',
            u'8 = reahl.systemaccountmodel:ActivateAccount',
            u'9 = reahl.systemaccountmodel:ChangeAccountEmail'    ],
                 },
    extras_require={}
)
