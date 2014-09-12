# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

SETUP_INFO = dict(
    name='lino',
    version='1.6.14',
    install_requires=[
        'North', 'djangosite', 'odfpy',
        'jinja2', 'appy', 'pytidylib', 'PyYAML'],
    description="A framework for writing desktop-like web applications \
    using Django and ExtJS",
    license='LGPL',
    include_package_data=True,
    zip_safe=False,
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com',
    url="http://www.lino-framework.org",
    #~ test_suite = 'lino.test_apps',
    test_suite='tests',
    classifiers="""\
  Programming Language :: Python
  Programming Language :: Python :: 2
  Development Status :: 4 - Beta
  Environment :: Web Environment
  Framework :: Django
  Intended Audience :: Developers
  Intended Audience :: System Administrators
  License :: OSI Approved :: GNU Lesser General Public License (LGPL)
  Natural Language :: English
  Natural Language :: French
  Natural Language :: German
  Operating System :: OS Independent
  Topic :: Database :: Front-Ends
  Topic :: Home Automation
  Topic :: Office/Business
  Topic :: Software Development :: Libraries :: \
  Application Frameworks""".splitlines())

SETUP_INFO.update(long_description="""\
Lino is a high-level framework for writing desktop-like customized
database applications based on `Django <https://www.djangoproject.com/>`_
and `Sencha ExtJS <http://www.sencha.com/products/extjs/>`_.
A Lino application is technically just a Django project,
but the application developer does not need to write any
URLconf, HTML nor CSS (`more <http://lino-framework.org/about>`_)


Examples of Lino applications are
`Lino Welfare <http://welfare.lino-framework.org>`__,
`Lino Così <http://cosi.lino-framework.org>`__
`Lino Patrols <http://patrols.lino-framework.org>`__
or
`Lino Faggio <http://faggio.lino-framework.org>`__.

Lino is based on three other projects by the same author:
`atelier <http://atelier.lino-framework.org>`__,
`djangosite <http://site.lino-framework.org>`__
and
`north <http://north.lino-framework.org>`__.
  
""")

SETUP_INFO.update(packages=[str(n) for n in """
lino
lino.core
lino.history
lino.management
lino.management.commands
lino.mixins
lino.modlib
lino.modlib.auto
lino.modlib.auto.sales
lino.modlib.addresses
lino.modlib.appypod
lino.modlib.awesomeuploader
lino.modlib.beid
lino.modlib.boards
lino.modlib.bootstrap3
lino.modlib.cal
lino.modlib.cal.fixtures
lino.modlib.cal.management
lino.modlib.cal.management.commands
lino.modlib.cal.tests
lino.modlib.cal.workflows
lino.modlib.contacts
lino.modlib.contacts.fixtures
lino.modlib.countries
lino.modlib.countries.fixtures
lino.modlib.davlink
lino.modlib.dedupe
lino.modlib.excerpts
lino.modlib.export_excel
lino.modlib.extensible
lino.modlib.extjs
lino.modlib.eid_jslib
lino.modlib.eid_jslib.beid
lino.modlib.families
lino.modlib.finan
lino.modlib.finan.fixtures
lino.modlib.humanlinks
lino.modlib.humanlinks.fixtures
lino.modlib.iban
lino.modlib.importfilters
lino.modlib.languages
lino.modlib.languages.fixtures
lino.modlib.ledger
lino.modlib.ledger.fixtures
lino.modlib.lists
lino.modlib.lists.fixtures
lino.modlib.notes
lino.modlib.notes.fixtures
lino.modlib.print_pisa
lino.modlib.products
lino.modlib.products.fixtures
lino.modlib.projects
lino.modlib.properties
lino.modlib.rooms
lino.modlib.sales
lino.modlib.sales.fixtures
lino.modlib.uploads
lino.modlib.users
lino.modlib.users.fixtures
lino.modlib.thirds
lino.modlib.reception
lino.modlib.tickets
lino.modlib.tickets.fixtures
lino.modlib.vocbook
lino.modlib.outbox
lino.modlib.outbox.fixtures
lino.modlib.blogs
lino.modlib.workflows
lino.modlib.polls
lino.modlib.polls.fixtures
lino.modlib.postings
lino.modlib.accounts
lino.modlib.vat
lino.modlib.households
lino.modlib.households.fixtures
lino.modlib.courses
lino.modlib.about
lino.modlib.pages
lino.modlib.pages.fixtures
lino.modlib.codechanges
lino.modlib.orders
lino.modlib.changes
lino.modlib.comments
lino.modlib.concepts
lino.modlib.partners
lino.modlib.partners.fixtures
lino.modlib.declarations
lino.modlib.events
lino.modlib.events.fixtures
lino.modlib.events.tests
lino.modlib.smtpd
lino.modlib.smtpd.management
lino.modlib.smtpd.management.commands
lino.modlib.statbel
lino.modlib.statbel.fixtures
lino.modlib.sepa
lino.modlib.sepa.fixtures
lino.modlib.system
lino.modlib.system.fixtures
lino.modlib.system.tests
lino.projects
lino.projects.belref
lino.projects.belref.fixtures
lino.projects.belref.settings
lino.projects.cms
lino.projects.cms.fixtures
lino.projects.crl
lino.projects.crl.fixtures
lino.projects.estref
lino.projects.estref.settings
lino.projects.events
lino.projects.homeworkschool
lino.projects.homeworkschool.settings
lino.projects.homeworkschool.fixtures
lino.projects.i18n
lino.projects.igen
lino.projects.igen.tests
lino.projects.min1
lino.projects.min2
lino.projects.min2.modlib
lino.projects.min2.modlib.contacts
lino.projects.min2.modlib.contacts.fixtures
lino.projects.min2.tests
lino.projects.polly
lino.projects.polly.settings
lino.projects.presto
lino.projects.presto.fixtures
lino.projects.presto.settings
lino.projects.presto.modlib
lino.projects.presto.modlib.contacts
lino.projects.presto.modlib.contacts.fixtures
lino.projects.presto.tests
lino.projects.std
lino.projects.babel_tutorial
lino.projects.babel_tutorial.fixtures
lino.projects.docs
lino.sphinxcontrib
lino.sphinxcontrib.logo
lino.test_apps
lino.test_apps.20090714
lino.test_apps.20090717
lino.test_apps.20100126
lino.test_apps.20100127
lino.test_apps.20100206
lino.test_apps.20100212
lino.test_apps.chooser
lino.test_apps.properties
lino.test_apps.example
lino.test_apps.quantityfield
lino.test_apps.20121124
lino.test_apps.mti
lino.test_apps.nomti
lino.tests
lino.tutorials
lino.tutorials.mini
lino.tutorials.lets1
lino.tutorials.lets1.fixtures
lino.tutorials.lets1.lets
lino.ui
lino.utils
lino.utils.xmlgen
lino.utils.xmlgen.intervat
lino.utils.xmlgen.cbss
lino.utils.xmlgen.odf
lino.utils.xmlgen.sepa
""".splitlines() if n])

SETUP_INFO.update(message_extractors={
    'lino': [
        ('**/sandbox/**',        'ignore', None),
        ('**/cache/**',          'ignore', None),
        ('**.py',                'python', None),
        ('**/linoweb.js',        'jinja2', None),
        #~ ('**.js',                'javascript', None),
        ('**/config/**.html', 'jinja2', None),
        #~ ('**/templates/**.txt',  'genshi', {
        #~ 'template_class': 'genshi.template:TextTemplate'
        #~ })
    ],
})

SETUP_INFO.update(package_data=dict())


def add_package_data(package, *patterns):
    package = str(package)
    l = SETUP_INFO['package_data'].setdefault(package, [])
    l.extend(patterns)
    return l

add_package_data('lino', 'config/*.odt')
add_package_data('lino.modlib.cal', 'config/*.odt')
add_package_data('lino.modlib.notes', 'config/notes/Note/*.odt')
add_package_data('lino.modlib.outbox', 'config/outbox/Mail/*.odt')
add_package_data('lino.modlib.languages.fixtures', '*.tab')

l = add_package_data('lino')
for lng in 'de fr et nl'.split():
    l.append('locale/%s/LC_MESSAGES/*.mo' % lng)