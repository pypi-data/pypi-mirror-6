#
#    Copyright (C) 2009-2013  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from setuptools import setup, find_packages
from lxml import etree
import os

NAME = 'BastionLedger'

md = os.path.join(os.path.dirname(__file__), 'Products', NAME,'profiles', 'default', 'metadata.xml')
version = etree.fromstring(open(md).read(), 
                           etree.XMLParser()).xpath('/metadata/version')[0].text

setup(name='Products.BastionLedger',
      version=version,
      description="Zope/Plone Accountancy Suite.",
      long_description="""
General Ledger, Order Management, Debtor and Creditor Management,Shareholder Management, Asset Register, Forecasting, ...""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Topic :: Office/Business :: Financial :: Accounting",
        ],
      keywords='BastionLedger',
      author='Alan Milligan',
      author_email='alan.milligan@last-bastion.net',
      url='http://www.last-bastion.net/forge/BastionLedger',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'xhtml2pdf',
          'Products.BastionBanking',
          'Products.ZScheduler',
          'archetypes.referencebrowserwidget',
          'Products.AdvancedQuery',
          'Products.ManagableIndex',
          'collective.quickupload',
          'beautifulsoup4',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
      )
