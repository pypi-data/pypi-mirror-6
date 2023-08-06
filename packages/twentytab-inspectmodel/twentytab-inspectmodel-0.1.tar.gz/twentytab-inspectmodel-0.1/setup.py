from setuptools import setup, find_packages
import inspectmodel

setup(name='twentytab-inspectmodel',
      version=inspectmodel.__version__,
      description='A django app based on django-inspect-model that implements a user interface to inspect all models in your applications',
      author='20tab S.r.l.',
      author_email='info@20tab.com',
      url='https://github.com/20tab/twentytab-inspectmodel',
      license='MIT License',
      install_requires=[
          'Django >=1.6',
          'django-appconf>=0.6',
          'django-inspect-model'
      ],
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
      }
)
