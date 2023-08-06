from setuptools import setup, find_packages
import tree

setup(name='twentytab-tree',
      version=tree.__version__,
      description='A django app that allows to create a tree menu and breadcrumb. It provides to create also urls, views and template.',
      author='20tab S.r.l.',
      author_email='info@20tab.com',
      url='https://github.com/20tab/twentytab-tree',
      license='MIT License',
      install_requires=[
          'Django >=1.6',
          'django-appconf>=0.6',
          'django_mptt >=0.6',
          'twentytab-utils',
      ],
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
      }
)
