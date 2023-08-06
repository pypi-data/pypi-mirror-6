from distutils.core import setup
# -*- coding: UTF-8 -*-

setup(
    name='FinCDB',
    version='0.1.0',
    py_modules=['fincdb\CDBClasse', 'fincdb\TesteClasseCDB2', 'fincdb\GeraArquivosFin'],
    author='Marcelo G Facioli',
    author_email='mgfacioli@yahoo.com.br',
    url='http://matfinanpython.blogspot.com.br/',
    keywords = ["CDB", "Renda Fixa", "Mercado Financeiro Brasileiro", "Financas", "Investimentos"],
    license='LICENSE.TXT',
    classifiers = [
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
		"Development Status :: 1 - Planning",
		"Environment :: Console",
		"Intended Audience :: Financial and Insurance Industry",
		"Operating System :: OS Independent",
		"Natural Language :: Portuguese (Brazilian)",
		"Topic :: Office/Business :: Financial",
		"Topic :: Office/Business :: Financial :: Investment",
		"Topic :: Software Development :: Libraries :: Python Modules",
	],
    description='Modulo contendo as Classes bases para trabalhar-se com operacoes de Renda Fixa (CDB, Debentures, LFT, NTN-F, etc) do mercado financeiro brasileiro.',
    long_description=open('docs\README.txt').read(),
)