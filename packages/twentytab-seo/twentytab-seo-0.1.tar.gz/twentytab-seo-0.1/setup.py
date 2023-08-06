from setuptools import setup, find_packages
import seo

setup(name='twentytab-seo',
      version=seo.__version__,
      description='A django app that allows to manage the meta contents of pages. He needs twentytab-tree. It also allows to translate information related to pages',
      author='20tab S.r.l.',
      author_email='info@20tab.com',
      url='https://github.com/20tab/twentytab-seo',
      license='MIT License',
      install_requires=[
          'Django >=1.6',
          'django-appconf>=0.6',
          'django-modeltranslation >=0.7',
          'twentytab-tree',
          'twentytab-tab-translation'
      ],
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
      }
)
