from setuptools import setup, find_packages
import os

version = '2.4.2'

tests_require = [
    'Products.Silva [test]',
    ]

def product_path(filename):
    return os.path.join("Products", "SilvaForum", filename)

setup(name='Products.SilvaForum',
      version=version,
      description="Forum for Silva",
      long_description=open(product_path("README.txt")).read() + "\n" + \
          open(product_path("HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='forum silva zope2',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/Products.SilvaForum',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Silva',
        'Products.SilvaMetadata',
        'five.grok',
        'setuptools',
        'silva.app.subscriptions',
        'silva.batch',
        'silva.captcha',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.services',
        'silva.core.views',
        'silva.resourceinclude',
        'silva.translations',
        'zeam.form.silva',
        'zeam.utils.batch',
        'zope.component',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
