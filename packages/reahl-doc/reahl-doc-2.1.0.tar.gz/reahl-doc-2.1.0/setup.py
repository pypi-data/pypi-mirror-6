from setuptools import setup
setup(
    name='reahl-doc',
    version=u'2.1.0',
    description='Documentation and examples for Reahl.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-doc contains documentation and examples of Reahl.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.doc_dev', 'reahl.doc', 'reahl.doc.examples', 'reahl.doc.examples.features', 'reahl.doc.examples.tutorial', 'reahl.doc.examples.features.i18nexample', 'reahl.doc.examples.features.pageflow', 'reahl.doc.examples.features.persistence', 'reahl.doc.examples.features.validation', 'reahl.doc.examples.features.tabbedpanel', 'reahl.doc.examples.features.access', 'reahl.doc.examples.features.layout', 'reahl.doc.examples.tutorial.login2', 'reahl.doc.examples.tutorial.pageflow1', 'reahl.doc.examples.tutorial.hellonginx', 'reahl.doc.examples.tutorial.i18nexample', 'reahl.doc.examples.tutorial.hello', 'reahl.doc.examples.tutorial.parameterised1', 'reahl.doc.examples.tutorial.parameterised2', 'reahl.doc.examples.tutorial.ajax', 'reahl.doc.examples.tutorial.sessionscope', 'reahl.doc.examples.tutorial.componentconfig', 'reahl.doc.examples.tutorial.migrationexample', 'reahl.doc.examples.tutorial.login1', 'reahl.doc.examples.tutorial.pageflow2', 'reahl.doc.examples.tutorial.pager', 'reahl.doc.examples.tutorial.addressbook2', 'reahl.doc.examples.tutorial.helloapache', 'reahl.doc.examples.tutorial.addressbook1', 'reahl.doc.examples.tutorial.access1', 'reahl.doc.examples.tutorial.jobs', 'reahl.doc.examples.tutorial.access', 'reahl.doc.examples.tutorial.access2', 'reahl.doc.examples.tutorial.slots', 'reahl.doc.examples.tutorial.login2.login2_dev', 'reahl.doc.examples.tutorial.i18nexample.i18nexamplemessages', 'reahl.doc.examples.tutorial.i18nexample.i18nexample_dev', 'reahl.doc.examples.tutorial.parameterised2.parameterised2_dev', 'reahl.doc.examples.tutorial.ajax.ajax_dev', 'reahl.doc.examples.tutorial.sessionscope.sessionscope_dev', 'reahl.doc.examples.tutorial.componentconfig.componentconfig_dev', 'reahl.doc.examples.tutorial.migrationexample.migrationexample_dev', 'reahl.doc.examples.tutorial.login1.login1_dev', 'reahl.doc.examples.tutorial.pager.pager_dev', 'reahl.doc.examples.tutorial.access1.access1_dev', 'reahl.doc.examples.tutorial.jobs.jobs_dev', 'reahl.doc.examples.tutorial.access.access_dev', 'reahl.doc.examples.tutorial.access2.access2_dev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[u'reahl-web>=2.1,<2.2', u'reahl-component>=2.1,<2.2', u'reahl-sqlalchemysupport>=2.1,<2.2', u'reahl-web-elixirimpl>=2.1,<2.2', u'reahl-domain>=2.1,<2.2', u'reahl-domainui>=2.1,<2.2'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.1,<2.2', u'Sphinx', u'reahl-stubble>=2.1,<2.2', u'reahl-dev>=2.1,<2.2', u'reahl-webdev>=2.1,<2.2'],
    test_suite=u'reahl.doc_dev',
    entry_points={
        'reahl.translations': [
            u'reahl-doc = reahl.doc.examples.tutorial.i18nexample.i18nexamplemessages'    ],
        u'reahl.configspec': [
            u'config = reahl.doc.examples.tutorial.componentconfig.componentconfig:AddressConfig'    ],
        u'reahl.dev.commands': [
            u'GetExample = reahl.doc.commands:GetExample',
            u'ListExamples = reahl.doc.commands:ListExamples'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        u'reahl.scheduled_jobs': [
            u'Address.clear_added_flags = reahl.doc.examples.tutorial.jobs.jobs:Address.clear_added_flags'    ],
        u'reahl.persistlist': [
            u'0 = reahl.doc.examples.features.persistence.persistence:Comment',
            u'1 = reahl.doc.fileupload:Comment',
            u'2 = reahl.doc.fileupload:AttachedFile',
            u'3 = reahl.doc.examples.tutorial.addressbook2.addressbook2:Address',
            u'4 = reahl.doc.examples.tutorial.addressbook1.addressbook1:Address',
            u'5 = reahl.doc.examples.tutorial.pageflow2.pageflow2:Address',
            u'6 = reahl.doc.examples.tutorial.pageflow1.pageflow1:Address',
            u'7 = reahl.doc.examples.tutorial.parameterised1.parameterised1:Address',
            u'8 = reahl.doc.examples.tutorial.parameterised2.parameterised2:Address',
            u'9 = reahl.doc.examples.tutorial.sessionscope.sessionscope:User',
            u'10 = reahl.doc.examples.tutorial.sessionscope.sessionscope:LoginSession',
            u'11 = reahl.doc.examples.tutorial.access1.access1:AddressBook',
            u'12 = reahl.doc.examples.tutorial.access1.access1:Collaborator',
            u'13 = reahl.doc.examples.tutorial.access1.access1:Address',
            u'14 = reahl.doc.examples.tutorial.access2.access2:AddressBook',
            u'15 = reahl.doc.examples.tutorial.access2.access2:Collaborator',
            u'16 = reahl.doc.examples.tutorial.access2.access2:Address',
            u'17 = reahl.doc.examples.tutorial.access.access:AddressBook',
            u'18 = reahl.doc.examples.tutorial.access.access:Collaborator',
            u'19 = reahl.doc.examples.tutorial.access.access:Address',
            u'20 = reahl.doc.examples.tutorial.i18nexample.i18nexample:Address',
            u'21 = reahl.doc.examples.tutorial.componentconfig.componentconfig:Address',
            u'22 = reahl.doc.examples.tutorial.migrationexample.migrationexample:Address',
            u'23 = reahl.doc.examples.tutorial.jobs.jobs:Address'    ],
                 },
    extras_require={u'pillow': [u'pillow']}
)
