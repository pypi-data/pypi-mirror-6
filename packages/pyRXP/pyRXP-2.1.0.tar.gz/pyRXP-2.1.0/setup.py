#!/usr/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/rl_addons/pyRXP/setup.py
if __name__=='__main__': #NO RUNTESTS
	import os, sys, shutil, re
	pkgDir=os.path.dirname(sys.argv[0])
	if not pkgDir:
		pkgDir=os.getcwd()
	elif not os.path.isabs(pkgDir):
		pkgDir=os.path.abspath(pkgDir)
	try:
		from setuptools import setup, Extension
	except ImportError:
		from distutils.core import setup, Extension

	def raiseConfigError(msg):
		import exceptions 
		class ConfigError(exceptions.Exception): 
			pass 
		raise ConfigError(msg)

	LIBS = []
	LIBRARIES=[]
	EXT_MODULES = []

	#building pyRXP
	if sys.platform=="win32":
		LIBS=['wsock32']
	elif sys.platform=="sunos5":
		LIBS=['nsl', 'socket', 'dl']
	elif sys.platform=="aix4":
		LIBS=['nsl_r', 'dl']
	else:
		LIBS=[]

	rxpFiles = ('xmlparser.c', 'url.c', 'charset.c', 'string16.c', 'ctype16.c', 
				'dtd.c', 'input.c', 'stdio16.c', 'system.c', 'hash.c', 
				'version.c', 'namespaces.c', 'http.c', 'nf16check.c', 'nf16data.c')
	pyRXPDir = os.path.join(pkgDir,'src')
	RXPLIBSOURCES=[]
	pyRXP_c = os.path.join(pyRXPDir,'pyRXP.c')
	VERSION = re.search(r'^#\s*define\s+VERSION\s*"([^"]+)"',open(pyRXP_c,'r').read(),re.MULTILINE)
	VERSION = VERSION and VERSION.group(1) or 'unknown'
	RXPDIR=os.path.join(pyRXPDir,'rxp')
	RXPLIBSOURCES= [os.path.join(RXPDIR,f) for f in rxpFiles]
	EXT_MODULES =	[Extension( 'pyRXPU',
								[pyRXP_c]+RXPLIBSOURCES,
								include_dirs=[RXPDIR],
								define_macros=[('CHAR_SIZE', 16),],
								library_dirs=[],
								# libraries to link against
								libraries=LIBS,
								#uncomment when debugging
								#extra_compile_args=['/Zi'], extra_link_args=['/DEBUG'],
								),
					]

	setup(	name = "pyRXP",
			version = VERSION,
			description = "Python RXP interface - fast validating XML parser",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			ext_modules = EXT_MODULES,
			#license = open(os.path.join('rxp','COPYING')).read(),
            classifiers = [
				'Development Status :: 5 - Production/Stable',
				'Intended Audience :: Developers',
				'License :: OSI Approved :: ReportLab BSD derived',
				'Programming Language :: Python',
				'Programming Language :: C',
				'Operating System :: Unix',
				'Operating System :: POSIX',
				'Operating System :: Microsoft :: Windows',
				'Topic :: Software Development :: Libraries :: Python Modules',
				'Topic :: Text Processing :: Markup :: XML',
                ]
			)
