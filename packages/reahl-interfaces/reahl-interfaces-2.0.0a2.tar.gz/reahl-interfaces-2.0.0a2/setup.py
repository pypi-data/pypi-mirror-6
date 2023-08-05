from setuptools import setup
setup(
    name='reahl-interfaces',
    version=u'2.0.0a2',
    description='Python abstract classes for important Reahl interfaces.',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language. . This package contains interfaces for which different implementations can be supplied. These implementations are called from the core Reahl framework. ',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[],
    setup_requires=[],
    tests_require=[u'reahl-tofu>=2.0.0a2,<2.1', u'reahl-stubble>=2.0.0a2,<2.1'],
    test_suite='tests',
    entry_points={
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={}
)
