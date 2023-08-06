from __future__ import unicode_literals
from future_builtins import ascii
import traceback, sys, os
_pyRXP = None
_logf = open('pyRXP_test.log','w')
_bad = 0
_total = 0
def _dot(c,write=sys.stdout.write):
	global _total, _bad
	write(c)
	if c=='E': _bad = _bad + 1
	if _total%40 == 39: write('\n')
	_total = _total + 1

greeks = {
	'Aacute': b'\xc3\x81',
	'aacute': b'\xc3\xa1',
	'Acirc': b'\xc3\x82',
	}
def ugeCB(name):
	#plogn('ugeCB called with name=%r' % name)
	try:
		return greeks[name]
	except:
		return '&#38;'+name+';'

def plog(x):
	_logf.write(x+'\n')
	_logf.flush()

def plogn(x):
	plog(x +('' if x.endswith('\n') else '\n'))

def goodTest(x,t,tb=0,inOnly=0,**kw):
	try:
		P=_pyRXP.Parser(**kw)
		r = P(x)
		rb = 0
	except:
		et, ev, _unused = sys.exc_info()
		r = '%s %s' % (et.__name__, ascii(ev)[8:-3])
		rb = 1

	s = ''
	for k,v in kw.items():
		s = s+', %s=%s' % (k,str(v))
	if type(t) is type(''):
		t = t.replace('\r','\\r')
		t = t.replace('\n','\\n')
	if type(r) is type(''):
		r = r.replace('\r','\\r')
		r = r.replace('\n','\\n')
	plog('%s.Parser(%s)(%s)'%(_pyRXP.__name__,s[2:],repr(x)))
	if (inOnly and t in r) or (r==t) and rb==tb:
		plogn('OK')
		_dot('.')
	else:
		_dot('E')
		plogn('\nBAD got %s' % repr(r))
		plogn('Expected %s' % repr(t))

def failTest(x,t,tb=1,inOnly=0,**kw):
	goodTest(x,t,tb,inOnly=inOnly,**kw)

def bigDepth(n):
	return n and '<tag%d>%s</tag%d>' % (n,bigDepth(n-1),n) or 'middle'

def getHere():
	if __name__=='__main__':
		here = sys.argv[0]
	else:
		here = __file__
	here = os.path.dirname(here)
	cwd = os.getcwd()
	if not here:
		here = cwd
	else:
		try:
			os.chdir(here)
			here = os.getcwd()
		finally:
			os.chdir(cwd)
	return here

with open(os.path.join(getHere(),'is-there.dtd'),'rb') as f:
	have_utf8_content_dtd = f.read()
have_unicode_content_dtd = have_utf8_content_dtd.decode('utf8')

DTDs = 	{
		'is-there.dtd': 'is-there.dtd',
		'not-there.dtd': 'really-not-there.dtd',
		'have-utf8-content.dtd': ('have-utf8-content.dtd-uri',have_utf8_content_dtd),
		'have-unicode-content.dtd': ('have-unicode-content.dtd-uri',have_unicode_content_dtd),
		'badt-have-utf8-content.dtd': (1,have_utf8_content_dtd),
		'badt-have-unicode-content.dtd': (1,have_unicode_content_dtd),
		}

def eoDTD(s):
	return DTDs.get(os.path.basename(s),None)

def _runTests(pyRXP):
	global _pyRXP
	_pyRXP = pyRXP
	plogn('############# Testing %s=%8.8X'%(pyRXP.__name__,id(_pyRXP)))
	try:
		for k,v in pyRXP.parser_flags.items(): eval('pyRXP.Parser(%s=%d)' % (k,v))
		plogn('Parser keywords OK')
		_dot('.')
	except:
		traceback.print_exc()
		plogn('Parser keywords BAD')
		_dot('E')
	try:
		for k,v in pyRXP.parser_flags.items(): eval('pyRXP.Parser()("<a/>",%s=%d)' % (k,v))
		plogn('Parser().parse keywords OK')
		_dot('.')
	except:
		traceback.print_exc()
		plogn('Parser().parse keywords BAD')
		_dot('E')

	try:
		P=_pyRXP.Parser()
		plog('Parser()=%r' % P)
		plog('Parser().__class__=%r' % P.__class__)
		plog('type(Parser())=%r\n\n' % type(P))
		del P
		plogn('Parser().__class__ etc OK')
		_dot('.')
	except:
		traceback.print_exc()
		plogn('Parser().__class__ etc BAD')
		_dot('E')

	goodTest('<a></a>',('a', None, [], None))
	goodTest('<a></a>',('a', {}, [], None),ExpandEmpty=1)
	goodTest('<a></a>',['a', None, [], None],MakeMutableTree=1)
	goodTest('<a/>',('a', None, None, None))
	goodTest('<a/>',('a', {}, [], None),ExpandEmpty=1)
	goodTest('<a/>',['a', None, None, None],MakeMutableTree=1)
	goodTest('<a/>',['a', {}, [], None],ExpandEmpty=1,MakeMutableTree=1)
	failTest('</a>',"error Error: End tag </a> outside of any element\n in unnamed entity at line 1 char 4 of [unknown]\nEnd tag </a> outside of any element\nParse Failed!\n")
	goodTest('<a>A<!--comment--></a>',('a', None, ['A'], None))
	goodTest('<a>A<!--comment--></a>',('a', {}, ['A'], None),ExpandEmpty=1)
	goodTest('<a>A<!--comment--></a>', ('a', None, ['A', ('<!--', None, ['comment'], None)], None), ReturnComments=1)
	goodTest('<a>A&lt;&amp;&gt;</a>',('a', None, ['A<&>'], None))
	goodTest('<a>A&lt;&amp;&gt;</a>',('a', None, ['A', '<', '&', '>'], None), MergePCData=0)
	goodTest('<!--comment--><a/>',('a', None, None, None),ReturnComments=1)
	goodTest('<!--comment--><a/>',[('<!--',None,['comment'],None),('a', None, None, None)],ReturnComments=1,ReturnList=1)
	goodTest('<!--comment--><a/>',('a', None, None, None),ReturnComments=1)
	failTest('<?xml version="1.0" encoding="LATIN-1"?></a>',"error Unknown declared encoding LATIN-1\nInternal error, ParserPush failed!\n")
	goodTest('<?work version="1.0" encoding="utf-8"?><a/>',[('<?',{'name':'work'}, ['version="1.0" encoding="utf-8"'],None), ('a', None, None, None)],IgnorePlacementErrors=1,ReturnList=1,ReturnProcessingInstructions=1,ReturnComments=1)
	goodTest('<a>\nHello\n<b>cruel\n</b>\nWorld\n</a>',('a', None, ['\nHello\n', ('b', None, ['cruel\n'], (('aaa', 2, 3), ('aaa', 3, 4))), '\nWorld\n'], (('aaa', 0, 3), ('aaa', 5, 4))),fourth=pyRXP.recordLocation,srcName='aaa')
	goodTest('<a aname="ANAME" aother="AOTHER">\nHello\n<b bname="BNAME" bother="BOTHER">cruel\n</b>\nWorld\n</a>',('a', {"aname": "ANAME", "aother": "AOTHER"}, ['\nHello\n', ('b', {"bname": "BNAME", "bother": "BOTHER"}, ['cruel\n'], (('aaa', 2, 33), ('aaa', 3, 4))), '\nWorld\n'], (('aaa', 0, 33), ('aaa', 5, 4))),fourth=pyRXP.recordLocation,srcName='aaa')
	goodTest('<a><![CDATA[<a>]]></a>',('a', None, ['<a>'], None))
	goodTest('<a><![CDATA[<a>]]></a>',('a', None, [('<![CDATA[', None, ['<a>'], None)], None),ReturnCDATASectionsAsTuples=1)
	goodTest('''<foo:A xmlns:foo="http://www.foo.org/"><foo:B><foo:C xmlns:foo="http://www.bar.org/"><foo:D>abcd</foo:D></foo:C></foo:B><foo:B/><A>bare A<C>bare C</C><B>bare B</B></A><A xmlns="http://default.reportlab.com/" xmlns:bongo="http://bongo.reportlab.com/">default ns A<bongo:A>bongo A</bongo:A><B>default NS B</B></A></foo:A>''',('{http://www.foo.org/}A', {'xmlns:foo': 'http://www.foo.org/'}, [('{http://www.foo.org/}B', None, [('{http://www.bar.org/}C', {'xmlns:foo': 'http://www.bar.org/'}, [('{http://www.bar.org/}D', None, ['abcd'], None)], None)], None), ('{http://www.foo.org/}B', None, None, None), ('A', None, ['bare A', ('C', None, ['bare C'], None), ('B', None, ['bare B'], None)], None), ('{http://default.reportlab.com/}A', {'xmlns': 'http://default.reportlab.com/', 'xmlns:bongo': 'http://bongo.reportlab.com/'}, ['default ns A', ('{http://bongo.reportlab.com/}A', None, ['bongo A'], None), ('{http://default.reportlab.com/}B', None, ['default NS B'], None)], None)], None),XMLNamespaces=1,ReturnNamespaceAttributes=1)
	failTest(bigDepth(257),"""error Internal error, stack limit reached!\n""", inOnly=1)
	failTest('<a>&Aacute;&aacute;</a>','error Error: Undefined entity Aacute\n in unnamed entity at line 1 char 12 of [unknown]\nUndefined entity Aacute\nParse Failed!\n')
	goodTest('<a>&Aacute;</a>',('a', None, ['\xc1'], None), ugeCB=ugeCB)
	filename = os.path.join(os.getcwd(),'not-there.dtd').replace(os.sep,'/')
	if filename.startswith('/'): filename = filename[1:]
	failTest('<!DOCTYPE foo SYSTEM "not-there.dtd"><foo>foo<a>aaa</a>fum</foo>',"error Error: Couldn't open dtd entity file:///%(filename)s\\n in unnamed entity at line 1 char 38 of [unknown]\\nCouldn't open dtd entity file:///%(filename)s\\nParse Failed!\\n"%vars(),NoNoDTDWarning=0)
	failTest('<!DOCTYPE foo SYSTEM "is-there.dtd"><foo><a>aaa</a></foo>','error Error: Content model for foo does not allow it to end here\\n in unnamed entity at line 1 char 57 of [unknown]\\nContent model for foo does not allow it to end here\\nParse Failed!\\n',NoNoDTDWarning=0)
	goodTest('<!DOCTYPE foo SYSTEM "is-there.dtd"><foo><a>aaa</a><b>bbbb</b></foo>',('foo', None, [('a', None, ['aaa'], None), ('b', None, ['bbbb'], None)], None),NoNoDTDWarning=0)
	failTest('<!DOCTYPE foo SYSTEM "is-there.dtd"><foo><a>aaa</a></foo>','error Error: Content model for foo does not allow it to end here\\n in unnamed entity at line 1 char 57 of [unknown]\\nContent model for foo does not allow it to end here\\nParse Failed!\\n',NoNoDTDWarning=0,eoCB=eoDTD)
	goodTest('<!DOCTYPE foo SYSTEM "is-there.dtd"><foo><a>aaa</a><b>bbbb</b></foo>',('foo', None, [('a', None, ['aaa'], None), ('b', None, ['bbbb'], None)], None),NoNoDTDWarning=0,eoCB=eoDTD)
	goodTest('<!DOCTYPE foo SYSTEM "have-utf8-content.dtd"><foo><a>aaa</a><b>bbbb</b></foo>',('foo', None, [('a', None, ['aaa'], None), ('b', None, ['bbbb'], None)], None),NoNoDTDWarning=0,eoCB=eoDTD)
	goodTest('<!DOCTYPE foo SYSTEM "have-unicode-content.dtd"><foo><a>aaa</a><b>bbbb</b></foo>',('foo', None, [('a', None, ['aaa'], None), ('b', None, ['bbbb'], None)], None),NoNoDTDWarning=0,eoCB=eoDTD)
	filename = os.path.join(os.getcwd(),'really-not-there.dtd').replace(os.sep,'/')
	if filename.startswith('/'): filename = filename[1:]
	failTest('<!DOCTYPE foo SYSTEM "not-there.dtd"><foo>foo<a>aaa</a>fum</foo>',"error Error: Couldn't open dtd entity file:///%(filename)s\\n in unnamed entity at line 1 char 38 of [unknown]\\nCouldn't open dtd entity file:///%(filename)s\\n"%vars(),NoNoDTDWarning=0,eoCB=eoDTD,inOnly=1)
	failTest('<!DOCTYPE foo SYSTEM "badt-have-utf8-content.dtd"><foo><a>aaa</a><b>bbbb</b></foo>',"error Error: Couldn't open dtd entity badt-have-utf8-content.dtd\\n in unnamed entity at line 1 char 51 of [unknown]\\nCouldn't open dtd entity badt-have-utf8-content.dtd\\nParse Failed!\\n",NoNoDTDWarning=0,eoCB=eoDTD)
	failTest('<!DOCTYPE foo SYSTEM "badt-have-unicode-content.dtd"><foo><a>aaa</a><b>bbbb</b></foo>',"error Error: Couldn't open dtd entity badt-have-unicode-content.dtd\\n in unnamed entity at line 1 char 54 of [unknown]\\nCouldn't open dtd entity badt-have-unicode-content.dtd\\nParse Failed!\\n",NoNoDTDWarning=0,eoCB=eoDTD)

def run():
	#import pyRXP
	import pyRXPU
	if '__doc__' in sys.argv:
		print(pyRXPU.__doc__)
	else:
		if pyRXPU: _runTests(pyRXPU)
		msg = "\n%d tests, %s failures!" % (_total,_bad and str(_bad) or 'no')
		print(msg)
		plogn(msg)

if __name__=='__main__': #noruntests
	run()
