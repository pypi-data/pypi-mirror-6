from setuptools import setup
setup(
    name='reahl-component',
    version=u'2.1.0',
    description='The component framework of Reahl.',
    long_description=u"Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-component is the component that contains Reahl's component framework.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ",
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.messages', 'reahl.component_dev', 'reahl.component'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=[u'Babel>=0.9,<0.10', u'python-dateutil>=1.5,<1.6', u'decorator>=3.4,<3.4'],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.1,<2.2', u'reahl-stubble>=2.1,<2.2'],
    test_suite=u'reahl.component_dev',
    entry_points={
        'reahl.translations': [
            u'reahl-component = reahl.messages'    ],
        u'reahl.component.databasecontrols': [
            u'NullDatabaseControl = reahl.component.dbutils:NullDatabaseControl'    ],
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
        'console_scripts': [
            u'reahl-control = reahl.component.prodshell:ProductionCommandline.execute_one'    ],
        u'reahl.component.prodcommands': [
            u'CreateDBUser = reahl.component.prodshell:CreateDBUser',
            u'DropDBUser = reahl.component.prodshell:DropDBUser',
            u'CreateDB = reahl.component.prodshell:CreateDB',
            u'DropDB = reahl.component.prodshell:DropDB',
            u'BackupDB = reahl.component.prodshell:BackupDB',
            u'RestoreDB = reahl.component.prodshell:RestoreDB',
            u'BackupAllDB = reahl.component.prodshell:BackupAllDB',
            u'RestoreAllDB = reahl.component.prodshell:RestoreAllDB',
            u'SizeDB = reahl.component.prodshell:SizeDB',
            u'RunJobs = reahl.component.prodshell:RunJobs',
            u'CreateDBTables = reahl.component.prodshell:CreateDBTables',
            u'DropDBTables = reahl.component.prodshell:DropDBTables',
            u'MigrateDB = reahl.component.prodshell:MigrateDB',
            u'ListConfig = reahl.component.prodshell:ListConfig',
            u'CheckConfig = reahl.component.prodshell:CheckConfig',
            u'ListDependencies = reahl.component.prodshell:ListDependencies'    ],
                 },
    extras_require={}
)
