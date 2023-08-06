/****************************************************************************
Copyright ReportLab Europe Ltd. 2000-2013 see license.txt for license details
 ****************************************************************************/
#include <Python.h>
#if PY_MAJOR_VERSION >= 3
#	define isPy3
#endif
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "system.h"
#if !defined(CHAR_SIZE)
#	error CHAR_SIZE not specified
#endif
#include "ctype16.h"
#include "charset.h"
#include "string16.h"
#include "dtd.h"
#include "input.h"
#include "xmlparser.h"
#include "stdio16.h"
#include "version.h"
#include "namespaces.h"
#define VERSION "2.1.0"
#define MAX_DEPTH 256
#if PY_VERSION_HEX < 0x02050000
#	define Py_ssize_t int
#endif

static	int	g_byteorder;
static	char *g_encname;

struct module_state {
	PyObject *moduleError;
	PyObject *moduleVersion;
	PyObject *RXPVersion;
	PyObject *commentTagName;
	PyObject *piTagName;
	PyObject *CDATATagName;
	PyObject *recordLocation;
	PyObject *parser_flags;
	PyObject *parser;
	};

typedef struct {
	PyObject_HEAD
	PyObject		*warnCB, *eoCB, *ugeCB, *srcName, *fourth, *__instance_module__;
	int				flags[2];
	} pyRXPParser;

#ifdef isPy3
#	define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#	define MSTATE(m,n) GETSTATE(m)->n
#	define PPSTATE(p,n) MSTATE(((pyRXPParser *)p)->__instance_module__,n)
#	define PDSTATE(pd,n) PPSTATE(((ParserDetails*)pd)->__self__,n)
#	define PSTATE(p,n) PDSTATE(((Parser)p)->warning_callback_arg,n)
#	define PyInt_FromLong	PyLong_FromLong
#	define PyInt_AsLong	PyLong_AsLong
#	define staticforward static
#	define statichere static
	/*cmp(a,b) = (a > b) - (a < b) in Python3*/
#	define PyObject_Cmp(a,b,i) *i=(PyObject_RichCompareBool(a, b, Py_GT)-PyObject_RichCompareBool(a, b, Py_LT))
#	define PyNumber_Int	PyNumber_Long
PyObject *RLPy_FindMethod(PyMethodDef *ml, PyObject *self, const char* name){
	for(;ml->ml_name!=NULL;ml++)
		if(name[0]==ml->ml_name[0] && strcmp(name+1,ml->ml_name+1)==0) return PyCFunction_New(ml, self);
	if(1){
		char buf[128];
		sprintf(buf,"attribute '%s' not found", name);
		PyErr_SetString(PyExc_AttributeError, buf);
		}
	return NULL;
	}
#	define Py_FindMethod RLPy_FindMethod
#	define KEY2STR(key) PyUnicode_AsUTF8(key)
#else
	static	PyObject *g_module;
	static struct module_state _state;
#	define GETSTATE(m) (&_state)
#	define MSTATE(m,n) GETSTATE(m)->n
#	define PPSTATE(p,n) MSTATE(p,n)
#	define PDSTATE(pd,n) MSTATE(pd,n)
#	define PSTATE(p,n) MSTATE(p,n)
#	include "bytesobject.h"
#	ifndef PyVarObject_HEAD_INIT
#		define PyVarObject_HEAD_INIT(type, size) \
			PyObject_HEAD_INIT(type) size,
#	endif
#	ifndef Py_TYPE
#		define Py_TYPE(ob) (((PyObject*)(ob))->ob_type)
#	endif
#	define PyBytes_AS_STRING	PyString_AS_STRING
#	define PyBytes_AsString	PyString_AsString
#	define PyBytes_GET_SIZE		PyString_GET_SIZE
#	define KEY2STR(key) PyBytes_AsString(key)
#endif

#if CHAR_SIZE==16
#	define MODULENAME "pyRXPU"
#	define UTF8DECL ,int utf8
#	define UTF8PASS ,utf8
#	define PYNSNAME(nsed, name) PyNSName(nsed,name,utf8)
PyObject* _PYSTRING(const Char* s, int utf8)
{
	int	lens = (int)Strlen(s);
#if defined(Py_UNICODE_WIDE)
	PyObject *u, *x;
	u = PyUnicode_DecodeUTF16((char*)s,2*lens,NULL,NULL);
	if(!utf8 || !u) return u;
	x = PyUnicode_AsUTF8String(u);
	Py_DECREF(u);
	return x;
#else
	return utf8 ? PyUnicode_EncodeUTF8((Py_UNICODE*)s, lens, NULL)
				: PyUnicode_FromUnicode((Py_UNICODE*)s, lens);
#endif
}
#	define PYSTRING(s) _PYSTRING(s,utf8)
PyObject* PYSTRING8(const char* s)
{
	return PyUnicode_DecodeUTF8((const char*)s, (int)strlen(s), NULL);
}
#	define EmptyCharStr (Char*)"\0"
#	define FMTCHAR "u"
#else
#	define MODULENAME "pyRXP"
#	define UTF8DECL
#	define UTF8PASS
#	define PYNSNAME(nsed, name) PyNSName(nsed,name)
#	define PYSTRING(s) PyString_FromString(s)
#	define PYSTRING8(s) PyString_FromString(s)
#	define EmptyCharStr (Char*)""
#	define FMTCHAR "s"
#endif
PyObject* PyNSName(NSElementDefinition nsed, const Char *name UTF8DECL){
	Char		*t, *ns;
	Namespace	NS;
	static Char braces[]={'{','}',0};
	int			lns;
	PyObject*	r;
	if(nsed && (NS=nsed->RXP_NAMESPACE) && (ns=NS->nsname) && (lns=(int)Strlen(ns))){
		t = Strchr(name,':');
		if(t) name=t+1;
		t = (Char*)Malloc((lns+Strlen(name)+3)*sizeof(Char));
		Strncpy(t,braces,1);
		Strncpy(t+1,ns,lns);
		Strncpy(t+lns+1,braces+1,1);
		Strcpy(t+lns+2,name);
		}
	else t = (Char*)name;
	r = PYSTRING(t);
	if(t!=name) Free(t);
	return r;
	}
#if	CHAR_SIZE==16
#	define __DOC__1 "		 ReturnUTF8 = 0\n\
			Return UTF8 encoded strings rather than the default unicode\n"
#else
#	define __DOC__1 ""
#endif
PyDoc_STRVAR(__DOC__,
"\n\
This is " MODULENAME " a python wrapper for RXP, a validating namespace-aware XML parser\n\
in C.\n\
\n\
RXP was written by Richard Tobin at the Language Technology Group,\n\
Human Communication Research Centre, University of Edinburgh.\n\
\n\
RXP is distributed under the GNU Public Licence, which is in the file\n\
COPYING.  RXP may be made available under other licensing terms;\n\
contact M.Moens@ed.ac.uk for details.\n\
\n\
RXP is based on the W3C XML 1.0 recommendation of 10th February 1998\n\
and the Namespaces recommendation of 14th January 1999.  Deviations\n\
from these recommendations should probably be considered as bugs.\n\
\n\
Interface summary:\n\
\n\
The python module exports the following\n\
	error			a python exception\n\
	version			the string version of the module\n\
	RXPVersion		the version string of the rxp library\n\
					embedded in the module\n\
	parser_flags	a dictionary of parser flags\n\
					the values are the defaults for parsers\n\
	piTagName		special tagname used for processing instructions\n\
	commenTagName	special tagname used for comments\n\
	recordLocation	a special do nothing constant that can be used as\n\
					the 'fourth' argument and causes location information\n\
					to be recorded in the fourth position of each node.\n\
\n\
\n\
	Parser(*kw)		Class that creates a parser\n\
\n\
\n\
	Parser Attributes and Methods\n\
		parse(src,**kw)\n\
			The main interface to the parser. It returns Aaron Watter's\n\
			radxml encoding of the xml src.\n\
			The string src contains the xml.\n\
			The keyword arguments can modify the instance attributes\n\
			for this call only.\n\
			The __call__ attribute of Parser instances is equivalent to\n\
			the parse attribute.\n\
\n\
		srcName '[unknown]', name used to refer to the parser src\n\
			in error and warning messages.\n\
\n""\
		warnCB	0, should either be None, 0, or a\n\
			callable method with a single argument which will\n\
			receive warning messages. If None is used then warnings\n\
			are thrown away. If the default 0 value is used then\n\
			warnings are written to the internal error message buffer\n\
			and will only be seen if an error occurs.\n\
\n\
		eoCB	argument should be None or a callable method with\n\
			a single argument. This method will be called when external\n\
			entities are opened. The method should return a possibly\n\
			modified URI or a tuple containing a tuple (URI,'text...') to allow\n\
			the content itself to be returned. The possibly changed URI\n\
			is required.\n\
		ugeCB	 argument should be None or a callable method with\n\
			a single argument. This method will be called when undefined\n\
			general entity references are seen. The method should return a byte string\n\
			containing the definition of the entity\
\n""\
		fourth	argument should be None (default) or a callable method with\n\
			no arguments. If callable, will be called to get or generate the\n\
			4th item of every 4-item tuple or list in the returned tree.\n\
			May also be the special value pyRXP.recordLocation in which\n\
			case the 4th item is set to the tuple\n\
			((startsrc,startline,startchar),(endsrc,endline,endchar)).\n\
\n\
		Flag attributes corresponding to the rxp flags;\n\
			the values are the module standard defaults.\n\
		ExpandCharacterEntities = 1\n\
		ExpandGeneralEntities = 1\n\
			If these are set, entity references are expanded.  If not, the\n\
			references are treated as text, in which case any text returned that\n\
			starts with an ampersand must be an entity reference (and provided\n\
			MergePCData is off, all entity references will be returned as separate\n\
			pieces).\n\
		XMLSyntax = 1\n\
		XMLPredefinedEntities = 1\n\
		ErrorOnUnquotedAttributeValues = 1\n\
		NormaliseAttributeValues = 1\n\
			If this is set, attributes are normalised according to the standard.\n\
			You might want to not normalise if you are writing something like an\n\
			editor.\n\
		ErrorOnBadCharacterEntities = 1\n\
			If this is set, character entities which expand to illegal values are\n\
			an error, otherwise they are ignored with a warning.\n\
		ErrorOnUndefinedEntities = 1\n\
			If this is set, undefined general entity references are an error,\n\
			otherwise a warning is given and a fake entity constructed whose value\n\
			looks the same as the entity reference.\n\
		ReturnComments = 0\n\
			If this is set, comments are returned, otherwise they are ignored.\n\
		ReturnProcessingInstructions = 0\n\
			If this is set, processing instructions are returned, otherwise\n\
			they are ignored.\n\
		CaseInsensitive = 0\n\
		ErrorOnUndefinedElements = 0\n""\
		ErrorOnUndefinedAttributes = 0\n\
			If these are set and there is a DTD, references to undeclared elements\n\
			and attributes are an error.\n\
		WarnOnRedefinitions = 0\n\
			If this is on, a warning is given for redeclared elements, attributes,\n\
			entities and notations.\n\
		TrustSDD = 1\n\
		ProcessDTD = 0\n\
			If TrustSDD is set and a DOCTYPE declaration is present, the internal\n\
			part is processed and if the document was not declared standalone or\n\
			if Validate is set the external part is processed.	Otherwise, whether\n\
			the DOCTYPE is automatically processed depends on ProcessDTD; if\n\
			ProcessDTD is not set the user must call ParseDtd() if desired.\n\
		XMLExternalIDs = 1\n""\
		ReturnDefaultedAttributes = 1\n\
			If this is set, the returned attributes will include ones defaulted as\n\
			a result of ATTLIST declarations, otherwise missing attributes will not\n\
			be returned.\n\
		MergePCData = 1\n\
			If this is set, text data will be merged across comments and entity\n\
			references.\n\
		XMLMiscWFErrors = 1\n\
		XMLStrictWFErrors = 1\n\
			If this is set, various well-formedness errors will be reported as errors\n\
			rather than warnings.\n\
		AllowMultipleElements = 0\n\
		MaintainElementStack = 1\n\
		IgnoreEntities = 0\n\
		XMLLessThan = 0\n\
		IgnorePlacementErrors = 0\n""\
		Validate = 1\n\
			If this is on, the parser will validate the document.\n\
		ErrorOnValidityErrors = 1\n\
			If this is on, validity errors will be reported as errors rather than\n\
			warnings.  This is useful if your program wants to rely on the\n\
			validity of its input.\n\
		XMLSpace = 0\n\
			If this is on, the parser will keep track of xml:space attributes\n\
		XMLNamespaces = 0\n\
			If this is on, the parser processes namespace declarations (see\n\
			below).  Namespace declarations are *not* returned as part of the list\n\
			of attributes on an element. The namespace value will be prepended to names\n\
			in the manner suggested by James Clark ie if xmlns:foo='foovalue'\n\
			is active then foo:name-->{fovalue}name.\n\
		NoNoDTDWarning = 1\n\
			Usually, if Validate is set, the parser will produce a warning if the\n\
			document has no DTD.  This flag suppresses the warning (useful if you\n\
			want to validate if possible, but not complain if not).\n\
		SimpleErrorFormat = 0\n""\
		AllowUndeclaredNSAttributes = 0\n\
		RelaxedAny = 0\n\
		ReturnNamespaceAttributes = 0\n\
		ReturnList = 0\n\
			Usually we discard comments and want only one tag; set this to 1 to get\n\
			a list at the top level instead of a supposed singleton tag.\n\
			If 0 the first tuple in the list will be returned (ie the first tag tuple).\n\
		ExpandEmpty false (default) or true.  If false, empty attribute dicts and\n\
			empty lists of children are changed into the value None\n\
			in every 4-item tuple or list in the returned tree\n\
		MakeMutableTree false (default) or true.  If false, nodes in the returned tree\n\
			are 4-item tuples; if true, 4-item lists.\n\
		ReturnCDATASectionsAsTuples = 0\n\
			If this is on, the parser returns for each CDATA section a tuple\n\
			with name field equal to CDATATagName containing a single string\n\
			in its third field that is the CDATA section.\n\
		XML11CheckNF = 0\n\
			If this is set the parser will check for unicode normalization and\n\
			is only relevant with XML 1.1 documents.\n\
		XML11CheckExists = 0\n\
			Controls whether unknown characters are present. It is only effective\n\
			when XML11CheckNF is set and the document is XML 1.1.\n\
		XMLIDs = 0\n\
			Check for xml:id attributes\n\
		XMLIDCheckUnique = 0\n\
			Ensure xml:id attributes are unique.\n"
"		 Pre105Chars = 1\n\
			use pre XML 1.0 fifth edition charset\n\
		Pre105VersionCheck = 1\n\
			if 1 force unrecognized XML 1.x versions to 1.0\n"
__DOC__1
);

/*alter the integer values to change the module defaults*/
static struct {char* k;long v;} flag_vals[]={
	{"ExpandCharacterEntities",1},
	{"ExpandGeneralEntities",1},
	{"XMLSyntax",1},
	{"XMLPredefinedEntities",1},
	{"ErrorOnUnquotedAttributeValues",1},
	{"NormaliseAttributeValues",1},
	{"ErrorOnBadCharacterEntities",1},
	{"ErrorOnUndefinedEntities",1},
	{"ReturnComments",0},
	{"CaseInsensitive",0},
	{"ErrorOnUndefinedElements",0},
	{"ErrorOnUndefinedAttributes",0},
	{"WarnOnRedefinitions",0},
	{"TrustSDD",1},
	{"XMLExternalIDs",1},
	{"ReturnDefaultedAttributes",1},
	{"MergePCData",1},
	{"XMLMiscWFErrors",1},
	{"XMLStrictWFErrors",1},
	{"AllowMultipleElements",0},
	{"MaintainElementStack",1},
	{"IgnoreEntities",0},
	{"XMLLessThan",0},
	{"IgnorePlacementErrors",0},
	{"Validate",1},
	{"ErrorOnValidityErrors",1},
	{"XMLSpace",0},
	{"XMLNamespaces",0},
	{"NoNoDTDWarning",1},
	{"SimpleErrorFormat",0},
	{"AllowUndeclaredNSAttributes",0},
	{"RelaxedAny",0},
	{"ReturnNamespaceAttributes",0},
	{"ProcessDTD",0},
	{"XML11Syntax",0},
	{"XML11CheckNF",0},
	{"XML11CheckExists",0},
	{"XMLID",0},
	{"XMLIDCheckUnique",0},
	{"Pre105Chars",1},
	{"Pre105VersionCheck",1},

	{"ReturnList",0},
	{"ExpandEmpty",0},
	{"MakeMutableTree",0},
	{"ReturnProcessingInstructions",0},
	{"ReturnCDATASectionsAsTuples",0},
#if	CHAR_SIZE==16
	{"ReturnUTF8",0},
#endif
	{0}};
#define LASTRXPFLAG Pre105VersionCheck
#define ReturnList (ParserFlag)(1+(int)LASTRXPFLAG)
#define ExpandEmpty (ParserFlag)(1+(int)ReturnList)
#define MakeMutableTree (ParserFlag)(1+(int)ExpandEmpty)
#define ReturnProcessingInstructions (ParserFlag)(1+(int)MakeMutableTree )
#define ReturnCDATASectionsAsTuples (ParserFlag)(1+(int)ReturnProcessingInstructions)
#if	CHAR_SIZE==16
#define ReturnUTF8 (ParserFlag)(1+(int)ReturnCDATASectionsAsTuples)
#endif
#define __GetFlag(p, flag) \
  ((((flag) < 32) ? ((p)->flags[0] & (1u << (flag))) : ((p)->flags[1] & (1u << ((flag)-32))))!=0)
#ifdef	_DEBUG
#	define Py_REFCOUNT(op) ((op)->ob_refcnt)
#endif

typedef	struct {
		Parser		p;
		int			warnCBF;
		int			warnErr;
		PyObject*	warnCB;
		PyObject*	eoCB;
		PyObject*	ugeCB;
		PyObject*	fourth;
		PyObject*	(*Node_New)(ssize_t);
		int			(*SetItem)(PyObject*, Py_ssize_t, PyObject*);
		PyObject*	(*GetItem)(PyObject*, Py_ssize_t);
		int			none_on_empty;
#if	CHAR_SIZE==16
		int			utf8;
#endif
#ifdef	isPy3
		pyRXPParser*	__self__;	/*the associated parser object*/
#endif
		} ParserDetails;

#define PDGetItem pd->GetItem
#define PDSetItem pd->SetItem
#define PDNode_New pd->Node_New
static	PyObject* get_attrs(ParserDetails* pd, Attribute a)
{
	int		useNone = pd->none_on_empty && !a;
#if	CHAR_SIZE==16
	int		utf8 = pd->utf8;
#endif

	if(!useNone){
		PyObject *attrs=PyDict_New(), *t, *s;
		for(; a; a=a->next){
			PyDict_SetItem(attrs,
				t=PYSTRING((Char*)a->definition->name),
				s=PYSTRING((Char*)a->value)
				);
			Py_XDECREF(t);
			Py_XDECREF(s);
			}
		return attrs;
		}
	else {
		Py_INCREF(Py_None);
		return Py_None;
		}
}

static	PyObject* _getSrcInfo(ParserDetails *pd)
{
	InputSource s = pd->p->source;
	PyObject *t = PyTuple_New(3);
	const char *name = EntityDescription(s->entity);
	int lnum, cnum;
	PyTuple_SET_ITEM(t,0,PYSTRING8(name));
	switch(SourceLineAndChar(s, &lnum, &cnum)){
		case 0:
		case 1:
			PyTuple_SET_ITEM(t,1,PyInt_FromLong(lnum));
			PyTuple_SET_ITEM(t,2,PyInt_FromLong(cnum));
			break;
		default:
			PyTuple_SET_ITEM(t,1,Py_None);
			PyTuple_SET_ITEM(t,2,Py_None);
			Py_INCREF(Py_None);
			Py_INCREF(Py_None);
		}
	return t;
}

static	void _reverseSrcInfoTuple(PyObject *info)
{
	PyObject *t0, *t1;
	t0 = PyTuple_GET_ITEM(info,0);
	t1 = PyTuple_GET_ITEM(info,1);
	PyTuple_SET_ITEM(info,0,t1);
	PyTuple_SET_ITEM(info,1,t0);
}

static	PyObject* _makeNode(ParserDetails* pd, PyObject *pyName, PyObject* attr, int empty)
{
	PyObject	*t = PDNode_New(4);
	PDSetItem(t, 0, pyName);	/*Note we borrow this*/
	PDSetItem(t, 1, attr);
	if(empty && pd->none_on_empty){
		attr = Py_None;
		Py_INCREF(Py_None);
		}
	else
		attr = PyList_New(0);
	PDSetItem(t,2,attr);
	if(pd->fourth && pd->fourth!=Py_None){
		if(pd->fourth==PDSTATE(pd,recordLocation)){
			attr = PyTuple_New(2);
			PyTuple_SET_ITEM(attr,0,_getSrcInfo(pd));
			PyTuple_SET_ITEM(attr,1,Py_None);
			Py_INCREF(Py_None);
			}
		else attr = PyObject_CallObject(pd->fourth, 0);
		}
	else {
		attr = Py_None;
		Py_INCREF(Py_None);
		}
	PDSetItem(t, 3, attr);
	return t;
}

static	PyObject* makeNode(ParserDetails* pd, const Char *name, PyObject* attr, int empty)
{
#if	CHAR_SIZE==16
	int		utf8 = pd->utf8;
#endif
	return _makeNode(pd, PYSTRING(name), attr, empty);
}

/*_makeNode for predefined python objects*/
static	PyObject* _makeNodePD(ParserDetails* pd, PyObject *pyName, PyObject* attr, int empty)
{
	Py_INCREF(pyName);
	return _makeNode(pd, pyName, attr, empty);
}


static	int handle_bit(Parser p, XBit bit, PyObject *stack[],int *depth)
{
	int	r = 0, empty;
	PyObject	*t, *s;
	ParserDetails*	pd = (ParserDetails*)(p->warning_callback_arg);
#if	CHAR_SIZE==16
	int		utf8 = pd->utf8;
#endif
	switch(bit->type) {
		case XBIT_eof: break;
		case XBIT_error:
			ParserPerror(p, bit);
			r = 1;
			break;
		case XBIT_start:
		case XBIT_empty:
			if(*depth==MAX_DEPTH){
				Fprintf(Stderr,"Internal error, stack limit reached!\n");
				r = 2;
				break;
				}

			empty = bit->type == XBIT_empty;
			t = ParserGetFlag(p, XMLNamespaces) ?
					_makeNode( pd, PYNSNAME(bit->ns_element_definition, bit->element_definition->name),
						get_attrs(pd, bit->attributes), empty)
					:
					makeNode( pd, bit->element_definition->name,
						get_attrs(pd, bit->attributes), empty);
			if(empty){
				PyList_Append(PDGetItem(stack[*depth],2),t);
				Py_DECREF(t);
				}
			else {
				*depth = *depth + 1;
				stack[*depth] = t;
				}
			break;
		case XBIT_end:
			if(*depth==0){
				Fprintf(Stderr,"Internal error, stack underflow!\n");
				r = 2;
				break;
				}
			t = stack[*depth];
			if(pd->fourth==PDSTATE(pd,recordLocation)){
				PyTuple_SET_ITEM(PDGetItem(t,3),1,_getSrcInfo(pd));
				Py_DECREF(Py_None);
				}
			*depth = *depth-1;
			PyList_Append(PDGetItem(stack[*depth],2),t);
			Py_DECREF(t);
			break;
		case XBIT_pi:
			if(ParserGetFlag(p,ReturnProcessingInstructions)){
				s = PyDict_New();
				PyDict_SetItemString(s, "name", t=PYSTRING(bit->pi_name));
				Py_XDECREF(t);
				t = _makeNodePD( pd, PDSTATE(pd,piTagName), s, 0);
				if(pd->fourth==PDSTATE(pd,recordLocation)) _reverseSrcInfoTuple(PyTuple_GET_ITEM(t,3));
				Py_INCREF(PDSTATE(pd,piTagName));
				s = PYSTRING(bit->pi_chars);
				PyList_Append(PDGetItem(t,2),s);
				Py_XDECREF(s);
				PyList_Append(PDGetItem(stack[*depth],2),t);
				Py_DECREF(t);
				}
			break;
		case XBIT_pcdata:
			t = PYSTRING(bit->pcdata_chars);
			PyList_Append(PDGetItem(stack[*depth],2),t);
			Py_XDECREF(t);
			break;
		case XBIT_cdsect:
			if(ParserGetFlag(p,ReturnCDATASectionsAsTuples)){
				t = _makeNodePD( pd, PDSTATE(pd,CDATATagName),Py_None, 0);
				if(pd->fourth==PDSTATE(pd,recordLocation)) _reverseSrcInfoTuple(PyTuple_GET_ITEM(t,3));
				Py_INCREF(PDSTATE(pd,CDATATagName));
				Py_INCREF(Py_None);
				s = PYSTRING(bit->cdsect_chars);
				PyList_Append(PDGetItem(t,2),s);
				Py_XDECREF(s);
				PyList_Append(PDGetItem(stack[*depth],2),t);
				Py_DECREF(t);
				}
			else {
				t = PYSTRING(bit->cdsect_chars);
				PyList_Append(PDGetItem(stack[*depth],2),t);
				Py_XDECREF(t);
				}
			break;
		case XBIT_dtd:
			break;
		case XBIT_comment:
			if(ParserGetFlag(p,ReturnComments)){
				t = _makeNodePD( pd, PDSTATE(pd,commentTagName), Py_None, 0);
				if(pd->fourth==PDSTATE(pd,recordLocation)) _reverseSrcInfoTuple(PyTuple_GET_ITEM(t,3));
				Py_INCREF(Py_None);
				Py_INCREF(PDSTATE(pd,commentTagName));
				s = PYSTRING(bit->comment_chars);
				PyList_Append(PDGetItem(t,2),s);
				Py_XDECREF(s);
				PyList_Append(PDGetItem(stack[*depth],2),t);
				Py_DECREF(t);
				}
			break;
		default:
			Fprintf(Stderr, "\nUnknown event type %s\n", XBitTypeName[bit->type]);
			ParserPerror(p, bit);
			r = 1;
			break;
		}
	return r;
}


static InputSource entity_open(Entity e, void *info)
{
	ParserDetails*	pd = (ParserDetails*)info;
	PyObject	*eoCB = pd->eoCB, *text=NULL, *tmp;

	if(e->type==ET_external){
		PyObject	*arglist,*result;
		arglist = Py_BuildValue("(s)",e->systemid);	/*NB 8 bit*/
		result = PyEval_CallObject(eoCB, arglist);
		if(result){
			int isTuple=PyTuple_Check(result), isBytes=PyBytes_Check(result);
			if(!(isBytes||isTuple)&&PyUnicode_Check(result)){
				tmp = PyUnicode_AsEncodedString(result,"utf8","strict");
				if(tmp){
					Py_DECREF(result);
					result = tmp;
					isBytes = 1;
					}
				}
			if(isBytes||isTuple){
				void *esid=(void *)(e->systemid);
				if(isTuple){
					tmp = PyTuple_GET_ITEM(result,0);
					if(PyUnicode_Check(tmp)){
						tmp = PyUnicode_AsEncodedString(tmp,"utf8","strict");
						if(!tmp){
							PyErr_SetString(PDSTATE(pd,moduleError),"eoCB could not convert tuple URI (element 0) from unicode");
L_err0:						Py_DECREF(result);
							return NULL;
							}
						}
					else if(!PyBytes_Check(tmp)){
						PyErr_SetString(PDSTATE(pd,moduleError),"eoCB could not convert tuple URI (element 0) from unknown type");
						goto L_err0;
						}
					e->systemid = strdup8(PyBytes_AS_STRING(tmp));
					text = PyTuple_GET_ITEM(result,1);
					Py_INCREF(text);
					}
				else{
					e->systemid = strdup8(PyBytes_AS_STRING(result));
					}
				CFree(esid);
				}
			Py_DECREF(result);
			}
		else {
			PyErr_Clear();
			}
		Py_DECREF(arglist);
		}
	if(text){
		int textlen;
		char *buf;
		FILE16 *f16;
		if(PyUnicode_Check(text)){
			tmp = PyUnicode_AsEncodedString(text,"utf8","strict");
			if(tmp){
				Py_DECREF(text);
				text = tmp;
				}
			else {
				PyErr_SetString(PDSTATE(pd,moduleError),"eoCB could not convert tuple text value");
				Py_DECREF(text);
				return NULL;
				}
			}
		else if(!PyBytes_Check(text)){
			PyErr_SetString(PDSTATE(pd,moduleError),"eoCB returned tuple with non-text value");
			Py_DECREF(text);
			return NULL;
			}
		textlen = PyBytes_Size(text);
		buf = Malloc(textlen);
		memcpy(buf,PyBytes_AS_STRING(text),textlen);
		f16 = MakeFILE16FromString(buf, textlen, "r");
		SetCloseUnderlying(f16,1);
		Py_DECREF(text);
		if(!e->base_url) EntitySetBaseURL(e,e->systemid);
		return NewInputSource(e, f16);
		}
	else return EntityOpen(e);
}

void PyErr_FromStderr(Parser p, char *msg){
	struct _FILE16 {
		void *handle;
		int handle2, handle3;
		};
	char *buf=((struct _FILE16*)Stderr)->handle;
#if CHAR_SIZE == 8
	if(p->errbuf) Fprintf(Stderr,"%s\n", p->errbuf);
	Fprintf(Stderr,"%s\n", msg);
	buf[((struct _FILE16*)Stderr)->handle2] = 0;
	PyErr_SetString(PSTATE(p,moduleError),buf);
#else
	PyObject* t;
	if(p->errbuf) Fprintf(Stderr,"%s\n", p->errbuf);
	Fprintf(Stderr,"%s\n", msg);
	t = PyUnicode_DecodeUTF16((const char *)buf, (Py_ssize_t)(((struct _FILE16*)Stderr)->handle2), NULL, &g_byteorder);
	if(!t) return;
	PyErr_SetObject(PSTATE(p,moduleError),t);
	Py_DECREF(t);
#endif
}

int	checkFirstProperNode(ParserDetails *pd,PyObject *t)
{
	PyObject* n=PDGetItem(t,0);
	if(!n){
		PyErr_Clear();
		return 0;
		}
	return n!=PDSTATE(pd,piTagName) && n!=PDSTATE(pd,commentTagName) && n!=PDSTATE(pd,CDATATagName);
}

/*return non zero for error*/
PyObject *ProcessSource(Parser p, InputSource source)
{
	XBit		bit=0;
	int			r, depth, i;
	PyObject	*stack[MAX_DEPTH+1];
	PyObject	*retVal = 0;
	ParserDetails*	pd = (ParserDetails*)(p->warning_callback_arg);

	if(ParserPush(p, source) == -1) {
		PyErr_FromStderr(p,"Internal error, ParserPush failed!");
		return NULL;
		}

	depth = 0;
	stack[0] = makeNode( pd, EmptyCharStr, Py_None, 0);	/*stealing a reference to Py_None*/
	Py_INCREF(Py_None);					/*so we must correct for it*/
	while(1){
		XBitType bt;
		bit = ReadXBit(p);
		r = handle_bit(p, bit, stack, &depth);
		bt = bit->type;
		FreeXBit(bit);
		if(r) break;
		if (bt == XBIT_eof){
			r=0;
			break;
			}
		}
	if(!r && depth==0){
		PyObject*	l0 = PDGetItem(stack[0],2);
		Py_INCREF(l0);
		Py_DECREF(stack[0]);
		if(!__GetFlag(p,ReturnList)){
			int n = PyList_Size(l0);
			for(i=0;i<n;i++){
				retVal = PyList_GetItem(l0,i);
				if(checkFirstProperNode(pd,retVal)) break;
				}
			if(i==n) retVal = Py_None;
			Py_INCREF(retVal);
			Py_DECREF(l0);
			}
		else {
			retVal = l0;
			}
		PyErr_Clear();
		}
	else {
		PyErr_FromStderr(p,r ? "Parse Failed!" : "Internal error, stack not fully popped!");
		for(i=0;i<=depth;i++){
			Py_DECREF(stack[i]);
			}
		retVal = NULL;
		}
	return retVal;
}

static void myWarnCB(XBit bit, void *info)
{
	ParserDetails*	pd=(ParserDetails*)info;
	PyObject	*arglist;
	PyObject	*result;
	FILE16		*str;
	char		buf[512];

	pd->warnErr++;
	if(pd->warnCB==Py_None) return;

	str = MakeFILE16FromString(buf,sizeof(buf)-1,"w");
	_ParserPerror(str, pd->p, bit);
	Fclose(str);
#if	CHAR_SIZE==16
	{
	struct _FILE16 {
		void *handle;
		int handle2, handle3;
		};
	buf[((struct _FILE16*)str)->handle2] = 0;
	}
#endif
	arglist = Py_BuildValue("(" FMTCHAR ")",buf);
	result = PyEval_CallObject(pd->warnCB, arglist);
	Py_DECREF(arglist);
	if(result){
		Py_DECREF(result);
		}
	else {
		pd->warnCBF++;
		PyErr_Clear();
		}
}

static Char *myUGECB(Char *name, int namelen, void *info)
{
	ParserDetails*	pd=(ParserDetails*)info;
	PyObject	*arglist;
	PyObject	*result;
	PyObject	*uname;
	PyObject	*bytes;
	Char		*r=NULL;
	Py_ssize_t	sz;
	int			err, ir;
	const char	*s;

	if(pd->ugeCB==Py_None) return r;
	uname = PyUnicode_DecodeUTF16((const char *)name, (Py_ssize_t)(sizeof(Char)*namelen), NULL, &g_byteorder);
	if(!uname) return r;
	arglist = Py_BuildValue("(O)",uname);
	Py_DECREF(uname);
	result = PyEval_CallObject(pd->ugeCB, arglist);
	Py_DECREF(arglist);
	if(result){
		if(PyBytes_Check(result)){
			/*if we see bytes we asssume it's utf8 encoded*/
			sz = PyBytes_GET_SIZE(result);
			s = PyBytes_AS_STRING(result);
			uname = result;
			result = PyUnicode_FromStringAndSize(s,sz);
			Py_DECREF(uname);
			}
		if(result){
			if(PyUnicode_Check(result)){
				bytes=PyUnicode_AsEncodedString(result, g_encname, "strict");
				if(bytes){
					err = PyBytes_AsStringAndSize(bytes,(char **)&s,&sz);
					if(!err){
						/*at last we got a bunch of bytes in our encoding*/
						r = (Char*)Malloc(sz+sizeof(Char));
						if(r){
							memcpy((char *)r,s,sz);
							for(ir=0;ir<sizeof(Char);ir++) ((char *)r)[sz+ir]=0;
							}
						}
					Py_DECREF(bytes);
					}
				}
			Py_DECREF(result);
			}
		}
	return r;
}

static PyTypeObject pyRXPParserType;	/*declaration only*/
static void __SetFlag(pyRXPParser* p, ParserFlag flag, int value)
{
	int flagset;
	unsigned int flagbit;

	flagset = (flag >> 5);
	flagbit = (1u << (flag & 31));

	if(value) p->flags[flagset] |= flagbit;
	else p->flags[flagset] &= ~flagbit;
}

static int _set_attr(PyObject** pAttr, PyObject* value)
{
	Py_XDECREF(*pAttr);
	*pAttr = value;
	Py_INCREF(value);
	return 0;
}

static int _set_CB(char* name, PyObject** pCB, PyObject* value)
{
	if(value!=Py_None && !PyCallable_Check(value)){
		char buf[128];
		sprintf(buf,"%s value must be absent, callable or None", name);
		PyErr_SetString(PyExc_ValueError, buf);
		return -1;
		}
	else return _set_attr(pCB,value);
}

static int pyRXPParser_setattr(pyRXPParser *self, char *name, PyObject* value)
{
	char buf[256];
	PyObject*	v;
	int i;

	if(!strcmp(name,"warnCB")) return _set_CB(name,&self->warnCB,value);
	else if(!strcmp(name,"eoCB")) return _set_CB(name,&self->eoCB,value);
	else if(!strcmp(name,"ugeCB")) return _set_CB(name,&self->ugeCB,value);
	else if(!strcmp(name,"fourth")){
		if(value==PPSTATE(self,recordLocation)){
			return _set_attr(&self->fourth,value);
			}
		return _set_CB(name,&self->fourth,value);
		}
	else if(!strcmp(name,"srcName")){
		if(PyUnicode_Check(value)){
			v = PyUnicode_AsEncodedString(value,"utf8","strict");
			if(v){
				_set_attr(&self->srcName,v);
				Py_DECREF(v);
				return 0;
				}
			else{
				PyErr_SetString(PyExc_ValueError, "cannot convert srcName value to utf8");
				return -1;
				}
			}
		else if(!PyBytes_Check(value)){
			PyErr_SetString(PyExc_ValueError, "invalid type for srcName");
			return -1;
			}
		else return _set_attr(&self->srcName,value);
		}
	else {
		for(i=0;flag_vals[i].k;i++){
			if(!strcmp(flag_vals[i].k,name)){
				v = PyNumber_Int(value);
				if(v){
					__SetFlag(self,(ParserFlag)i,PyInt_AsLong(v));
					Py_DECREF(v);
					return 0;
					}
				else{
					sprintf(buf,"%s value must be int", name);
					PyErr_SetString(PyExc_ValueError, buf);
					return -1;
					}
				}
			}
		sprintf(buf,"Unknown attribute %s", name);
		PyErr_SetString(PyExc_AttributeError, buf);
		return -1;
		}
}

static PyObject* pyRXPParser_parse(pyRXPParser* xself, PyObject* args, PyObject* kw)
{
	Py_ssize_t	i;
	FILE16		*f;
	InputSource source;
	PyObject	*retVal=NULL, *osrc=NULL, *dsrc=NULL, *src;
	char		errBuf[512];
	ParserDetails	CB;
	Parser		p;
	Entity		e;
	pyRXPParser	dummy = *xself;
	pyRXPParser*	self = &dummy;
	memset(&CB,0,sizeof(CB));
#ifdef	isPy3
	CB.__self__ = self;
#endif
	if(self->warnCB) Py_INCREF(self->warnCB);
	if(self->eoCB) Py_INCREF(self->eoCB);
	if(self->ugeCB) Py_INCREF(self->ugeCB);
	if(self->fourth) Py_INCREF(self->fourth);
	if(self->srcName) Py_INCREF(self->srcName);

	if(!PyArg_ParseTuple(args, "O", &osrc)) goto L_1;
	if(PyUnicode_Check(osrc)){
		/*unicode*/
#if CHAR_SIZE==16
		if(!(src = PyUnicode_AsUTF16String(osrc))) goto L_1;
#else
		if(!(src = PyUnicode_AsUTF8String(osrc))) goto L_1;
#endif
		dsrc = src;
		}
	else if(PyBytes_Check(osrc)){
		/*bytes*/
		src = osrc;
		}
	else{
		PyErr_SetString(PyExc_TypeError,"parse argument neither str or unicode");
		goto L_1;
		}
	if(kw){
		PyObject *key, *value;
		i = 0;
		while(PyDict_Next(kw,&i,&key,&value))
			if(pyRXPParser_setattr(self, KEY2STR(key), value))	goto L_1;
		}

	if(self->warnCB && self->warnCB!=Py_None){
		CB.warnCB = self->warnCB;
		CB.warnErr = 0;
		CB.warnCBF = 0;
		}
	if(self->eoCB && self->eoCB!=Py_None){
		CB.eoCB = self->eoCB;
		}
	if(self->ugeCB && self->ugeCB!=Py_None){
		CB.ugeCB = self->ugeCB;
		}
	CB.fourth = self->fourth;

	p = NewParser();
	CB.p = p;
	ParserSetWarningCallbackArg(p, &CB);	/*we need this even if we don't have a warnCB*/
	if(self->warnCB && self->warnCB!=Py_None){
		ParserSetWarningCallback(p, myWarnCB);
		}
	if(self->ugeCB && self->ugeCB!=Py_None){
		ParserSetUGEProcArg(p, &CB);
		ParserSetUGEProc(p, myUGECB);
		}
	p->flags[0] = self->flags[0];
	p->flags[1] = self->flags[1];
	if(self->eoCB && self->eoCB!=Py_None){
		ParserSetEntityOpener(p, entity_open);
		ParserSetEntityOpenerArg(p, &CB);
		}
	CB.none_on_empty = !__GetFlag(self,ExpandEmpty);
#if	CHAR_SIZE==16
	CB.utf8 = __GetFlag(self,ReturnUTF8);
#endif
	if(__GetFlag(self,MakeMutableTree)){
		CB.Node_New = PyList_New;
		CB.SetItem = PyList_SetItem;
		CB.GetItem = PyList_GetItem;
		}
	else {
		CB.Node_New = PyTuple_New;
		CB.SetItem = PyTuple_SetItem;
		CB.GetItem = PyTuple_GetItem;
		}

	ParserSetFlag(p,XMLPredefinedEntities,__GetFlag(self,XMLPredefinedEntities));

	/*set up the parsers Stderr stream thing so we get it in a string*/
	Fclose(Stderr);
	Stderr = MakeFILE16FromString(errBuf,sizeof(errBuf)-1,"w");
	f = MakeFILE16FromString(PyBytes_AS_STRING(src),PyBytes_GET_SIZE(src),"r");
	source = SourceFromFILE16(PyBytes_AsString(self->srcName),f);
	retVal = ProcessSource(p,source);
	e = source->entity; /*used during FreeParser closing source!*/
	Fclose(Stderr);
	FreeDtd(p->dtd);
	FreeParser(p);
	FreeEntity(e);
	deinit_parser();
L_1:
	Py_XDECREF(dsrc);
	Py_XDECREF(self->warnCB);
	Py_XDECREF(self->eoCB);
	Py_XDECREF(self->ugeCB);
	Py_XDECREF(self->fourth);
	Py_XDECREF(self->srcName);
	return retVal;
}

static struct PyMethodDef pyRXPParser_methods[] = {
	{"parse", (PyCFunction)pyRXPParser_parse, METH_VARARGS|METH_KEYWORDS, "parse(src,**kw)"},
	{NULL, NULL}		/* sentinel */
};

static PyObject* _get_OB(char* name,PyObject* ob)
{
	char	buf[128];
	if(ob){
		Py_INCREF(ob);
		return ob;
		}
	sprintf(buf,"Unknown attribute %s", name);
	PyErr_SetString(PyExc_AttributeError, buf);
	return NULL;
}

static PyObject* pyRXPParser_getattr(pyRXPParser *self, char *name)
{
	int	i;
	if(!strcmp(name,"warnCB")) return _get_OB(name,self->warnCB);
	else if(!strcmp(name,"eoCB")) return _get_OB(name,self->eoCB);
	else if(!strcmp(name,"fourth")) return _get_OB(name,self->fourth);
	else if(!strcmp(name,"__instance_module__")) return _get_OB(name,self->__instance_module__);
	else if(!strcmp(name,"srcName")){
		Py_INCREF(self->srcName);
		return self->srcName;
		}
	else if(!strcmp(name,"__class__")){
		Py_INCREF((PyObject *)&pyRXPParserType);
		return (PyObject *)&pyRXPParserType;
		}
	else {
		for(i=0;flag_vals[i].k;i++)
			if(!strcmp(flag_vals[i].k,name))
				return PyInt_FromLong(__GetFlag(self,(ParserFlag)i));

		}
	return Py_FindMethod(pyRXPParser_methods, (PyObject *)self, name);
	}

static int pyRXPParser_traverse(pyRXPParser *self, visitproc visit, void *arg){
	Py_VISIT(self->srcName);
	Py_VISIT(self->warnCB);
	Py_VISIT(self->eoCB);
	Py_VISIT(self->fourth);
	Py_VISIT(self->__instance_module__);
	return 0;
	}
static int pyRXPParser_clear(pyRXPParser* self){
	Py_CLEAR(self->srcName);
	Py_CLEAR(self->warnCB);
	Py_CLEAR(self->eoCB);
	Py_CLEAR(self->fourth);
	Py_CLEAR(self->__instance_module__);
	return 0;
	}

static int pyRXPParser_dealloc(pyRXPParser* self){
	pyRXPParser_clear(self);
	Py_TYPE(self)->tp_free((PyObject*)self);
	return 0;
	}

#ifdef isPy3
static struct PyModuleDef moduleDef;
#endif
static int pyRXPParser_init(pyRXPParser* self, PyObject* args, PyObject* kw)
{
	Py_ssize_t	i;

	if(!PyArg_ParseTuple(args, ":Parser")) return -1;
	Py_XDECREF(self->warnCB);
	Py_XDECREF(self->eoCB);
	Py_XDECREF(self->ugeCB);
	Py_XDECREF(self->fourth);
	Py_XDECREF(self->srcName);
	Py_XDECREF(self->__instance_module__);
	self->warnCB = self->eoCB = self->ugeCB = self->fourth = self->srcName = NULL;
#ifdef isPy3
	self->__instance_module__ = PyState_FindModule(&moduleDef);
#else
	self->__instance_module__ = g_module;
#endif
	Py_INCREF(self->__instance_module__);
	if(!(self->srcName=PyBytes_FromString("[unknown]"))){
		PyErr_SetString(MSTATE(self->__instance_module__,moduleError),"Internal error, memory limit reached!");
Lfree:	pyRXPParser_dealloc(self);
		return -1;
		}
	for(i=0;flag_vals[i].k;i++)
		__SetFlag(self,(ParserFlag)i,PyInt_AsLong(PyDict_GetItemString(MSTATE(self->__instance_module__,parser_flags),flag_vals[i].k)));

	if(kw){
		PyObject *key, *value;
		i = 0;
		while(PyDict_Next(kw,&i,&key,&value))
			if(pyRXPParser_setattr(self, KEY2STR(key), value)) goto Lfree;
		}

	return 0;
	}

static PyTypeObject pyRXPParserType = {
	PyVarObject_HEAD_INIT(NULL, 0)

	MODULENAME ".Parser",					/*tp_name*/
	sizeof(pyRXPParser),					/*tp_basicsize*/
	0,										/*tp_itemsize*/
	(destructor)pyRXPParser_dealloc,		/*tp_dealloc*/
	0,										/*tp_print*/
	(getattrfunc)pyRXPParser_getattr,		/*tp_getattr*/
	(setattrfunc)pyRXPParser_setattr,		/*tp_setattr*/
	0,										/*tp_compare*/
	0,										/*tp_repr*/
	0,										/*tp_as_number*/
	0,										/*tp_as_sequence*/
	0,										/*tp_as_mapping*/
	0,										/*tp_hash*/
	(ternaryfunc)pyRXPParser_parse,			/*tp_call*/
	0,										/*tp_str*/
	0,										/*tp_getattro*/
	0,										/*tp_setattro*/
	0,										/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
	"pyRXPParser instance, see " MODULENAME " doc string for details.",
	(traverseproc)pyRXPParser_traverse,		/*tp_traverse*/
	(inquiry)pyRXPParser_clear,				/*tp_clear*/
	0,										/*tp_richcompare*/
	0,										/*tp_weaklistoffset*/
	0,										/*tp_iter*/
	0,										/*tp_iternext*/
	pyRXPParser_methods,					/*tp_methods*/
	0,										/*tp_members*/
	0,										/*tp_getset*/
	0,										/*tp_base*/
	0,										/*tp_dict*/
	0,										/*tp_descr_get*/
	0,										/*tp_descr_set*/
	0,										/*tp_dictoffset*/
	(initproc)pyRXPParser_init,				/*tp_init*/
	0,										/*tp_alloc*/
	0,										/*tp_new*/
	};


#if	defined(_DEBUG) && defined(WIN32)
#	include <crtdbg.h>
#endif
#ifdef isPy3
static int _traverse(PyObject *m, visitproc visit, void *arg) {
	struct module_state *st = GETSTATE(m);
	Py_VISIT(st->moduleError);
	Py_VISIT(st->moduleVersion);
	Py_VISIT(st->RXPVersion);
	Py_VISIT(st->piTagName);
	Py_VISIT(st->recordLocation);
	Py_VISIT(st->parser_flags);
	Py_VISIT(st->parser);
	return 0;
	}

static int _clear(PyObject *m) {
	struct module_state *st = GETSTATE(m);
	Py_CLEAR(st->moduleError);
	Py_CLEAR(st->moduleVersion);
	Py_CLEAR(st->RXPVersion);
	Py_CLEAR(st->piTagName);
	Py_CLEAR(st->recordLocation);
	Py_CLEAR(st->parser_flags);
	Py_CLEAR(st->parser);
	return 0;
	}
static struct PyModuleDef moduleDef = {
	PyModuleDef_HEAD_INIT,
	MODULENAME,
	__DOC__,
	sizeof(struct module_state),
	NULL,
	NULL,
	_traverse,
	_clear,
	NULL
	};
#	if CHAR_SIZE==16
#		define MODULEINIT PyInit_pyRXPU
#	else
#		define MODULEINIT PyInit_pyRXP
#	endif
#	define OK_RET m
#	define ERR_RET NULL
#	define CREATE_MODULE() PyModule_Create(&moduleDef);PyState_AddModule(m,&moduleDef)
PyMODINIT_FUNC MODULEINIT(void)
#else
#	if CHAR_SIZE==16
#		define MODULEINIT initpyRXPU
#	else
#		define MODULEINIT initpyRXP
#	endif
#	define OK_RET
#	define ERR_RET
#	define CREATE_MODULE() Py_InitModule3(MODULENAME, NULL, __DOC__)
DL_EXPORT(void) MODULEINIT(void)
#endif
{
	PyObject *m=NULL, *t, *moduleVersion=NULL, *RXPVersion=NULL, *moduleError=NULL,
			 *piTagName=NULL, *commentTagName=NULL, *CDATATagName=NULL, *recordLocation=NULL,
			 *parser_flags=NULL;
	int	i;
	g_byteorder = InternalCharacterEncoding==CE_UTF_16B?1:-1;
	g_encname = g_byteorder==1?"utf_16_be":"utf_16_le";

#if	defined(_DEBUG) && defined(WIN32)
	i = _CrtSetDbgFlag(_CRTDBG_REPORT_FLAG);
	i |= _CRTDBG_CHECK_ALWAYS_DF;
	_CrtSetDbgFlag(i);
#endif

	pyRXPParserType.tp_new = PyType_GenericNew;
	if(PyType_Ready(&pyRXPParserType)<0)goto err;	/*set up the types by hand*/

	/* Create the module and add the functions */
	m = CREATE_MODULE();
	if(!m)goto err;

#ifndef isPy3
	g_module = m;
#endif

	/* Add some symbolic constants to the module */
	moduleVersion = PyBytes_FromString(VERSION);
	if(!moduleVersion)goto err;
	RXPVersion = PyBytes_FromString(rxp_version_string);
	if(!RXPVersion)goto err;
	moduleError = PyErr_NewException(MODULENAME ".error",NULL,NULL);
	if(!moduleError)goto err;
	piTagName = PYSTRING8("<?");
	if(!piTagName)goto err;
	commentTagName = PYSTRING8("<!--");
	if(!commentTagName)goto err;
	CDATATagName = PYSTRING8("<![CDATA[");
	if(!CDATATagName)goto err;
	recordLocation = PyBytes_FromString("recordLocation");
	if(!recordLocation)goto err;
	parser_flags = PyDict_New();
	if(!parser_flags)goto err;
	for(i=0;flag_vals[i].k;i++){
		t=PyInt_FromLong(flag_vals[i].v);
		if(!t)goto err;
		PyDict_SetItemString(parser_flags, flag_vals[i].k, t);
		Py_DECREF(t);
		}

	/*add in the docstring*/
#define ADD2MODULE(n,o) PyModule_AddObject(m,n,o);MSTATE(m,o)=o
	ADD2MODULE("version", moduleVersion);
	ADD2MODULE("RXPVersion", RXPVersion);
	ADD2MODULE("error",moduleError);
	ADD2MODULE("piTagName", piTagName);
	ADD2MODULE("commentTagName", commentTagName);
	ADD2MODULE("CDATATagName", CDATATagName);
	ADD2MODULE("recordLocation", recordLocation);
	ADD2MODULE("parser_flags", parser_flags);
	Py_INCREF((PyObject *)&pyRXPParserType);
	PyModule_AddObject(m,"Parser", (PyObject *)&pyRXPParserType);
	MSTATE(m,parser) = (PyObject *)&pyRXPParserType;
	return OK_RET;
err:
	Py_XDECREF(moduleVersion);
	Py_XDECREF(RXPVersion);
	Py_XDECREF(moduleError);
	Py_XDECREF(piTagName);
	Py_XDECREF(commentTagName);
	Py_XDECREF(CDATATagName);
	Py_XDECREF(recordLocation);
	Py_XDECREF(parser_flags);
	Py_XDECREF(m);
	return ERR_RET;
}
