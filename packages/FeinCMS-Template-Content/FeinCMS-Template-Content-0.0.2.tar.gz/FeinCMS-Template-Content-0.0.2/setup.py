from setuptools import setup
import feincms_template_content

setup(
    name='FeinCMS-Template-Content',
    version=feincms_template_content.__version__,
    packages=['feincms_template_content'],
    package_data={
        'feincms_template_content': [
            'templates/content/*html',
        ]
    },
    license='MIT License',
    description='FeinCMS content types with (optionally) selectable templates.',
    long_description=open('README.rst').read(),
    author='Richard Ward',
    author_email='richard@richard.ward.name',
    url='https://github.com/RichardOfWard/feincms-template-content',
    install_requires=['django', 'feincms'],
    test_suite='tests',
    tests_require=['mock'],
)
