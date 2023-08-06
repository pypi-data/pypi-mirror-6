#include <stdio.h>
#include <stdlib.h>

#ifdef FOR_LT

#include "lt-memory.h"

#define Malloc salloc
#define Free sfree

#else

#include "system.h"

#endif

#include "charset.h"
#include "string16.h"

int iso_to_unicode[NISO][256];		/* 8859-2 ... 8859-15 */
int iso_max_val[NISO];
char8 *unicode_to_iso[NISO];

/* This table is used to initialise the above arrays */

static int latin_table[NISO-1][96] = {

/* 8859-2 */
{
#include "iso-8859/iso-8859-2"
},

/* 8859-3 */
{
#include "iso-8859/iso-8859-3"
},

/* 8859-4 */
{
#include "iso-8859/iso-8859-4"
},

/* 8859-5 */
{
#include "iso-8859/iso-8859-5"
},

/* 8859-6 */
{
#include "iso-8859/iso-8859-6"
},

/* 8859-7 */
{
#include "iso-8859/iso-8859-7"
},

/* 8859-8 */
{
#include "iso-8859/iso-8859-8"
},

/* 8859-9 */
{
#include "iso-8859/iso-8859-9"
},

/* 8859-10 */
{
#include "iso-8859/iso-8859-10"
},

/* 8859-11 */
{
#include "iso-8859/iso-8859-11"
},

/* 8859-12 (doesn't exist)*/
{
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
},

/* 8859-13 */
{
#include "iso-8859/iso-8859-13"
},

/* 8859-14 */
{
#include "iso-8859/iso-8859-14"
},

/* 8859-15 */
{
#include "iso-8859/iso-8859-15"
}
};
static int cp_1252_table[32]=
{
0x20ac, -00001, 0x201a, 0x0192, 0x201e, 0x2026, 0x2020, 0x2021,
0x02c6, 0x2030, 0x0160, 0x2039, 0x0152, -00001, 0x017d, -00001,
-00001, 0x2018, 0x2019, 0x201c, 0x201d, 0x2022, 0x2013, 0x2014,
0x02dc, 0x2122, 0x0161, 0x203a, 0x0153, -00001, 0x017e, 0x0178,
};


const char8 *CharacterEncodingName[CE_enum_count] = {
    "unknown",
    "unspecified-ascii-superset",

    "UTF-8",
    "ISO-646",

    "ISO-8859-1",
    "ISO-8859-2",
    "ISO-8859-3",
    "ISO-8859-4",
    "ISO-8859-5",
    "ISO-8859-6",
    "ISO-8859-7",
    "ISO-8859-8",
    "ISO-8859-9",
    "ISO-8859-10",
    "ISO-8859-11",
    "***ISO-8859-12***",
    "ISO-8859-13",
    "ISO-8859-14",
    "ISO-8859-15",
	"CP-1252",

    "UTF-16",
    "UTF-16",
    "ISO-10646-UCS-2",
    "ISO-10646-UCS-2",
};

const char8 *CharacterEncodingNameAndByteOrder[CE_enum_count] = {
    "unknown",
    "unspecified_ascii_superset",

    "UTF-8",
    "ISO-646",

    "ISO-8859-1",
    "ISO-8859-2",
    "ISO-8859-3",
    "ISO-8859-4",
    "ISO-8859-5",
    "ISO-8859-6",
    "ISO-8859-7",
    "ISO-8859-8",
    "ISO-8859-9",
    "ISO-8859-10",
    "ISO-8859-11",
    "***ISO-8859-12***",
    "ISO-8859-13",
    "ISO-8859-14",
    "ISO-8859-15",
	"CP-1252",

    "UTF-16-B",
    "UTF-16-L",
    "ISO-10646-UCS-2-B",
    "ISO-10646-UCS-2-L",
};

struct character_encoding_alias CharacterEncodingAlias[] = {
    {"ASCII", CE_ISO_646},
    {"US-ASCII", CE_ISO_646},
    {"WINDOWS-1252", CE_CP_1252},
    {"ISO-Latin-1", CE_ISO_8859_1},
    {"ISO-Latin-2", CE_ISO_8859_2},
    {"ISO-Latin-3", CE_ISO_8859_3},
    {"ISO-Latin-4", CE_ISO_8859_4},
    {"UCS-2", CE_ISO_10646_UCS_2B},
};
const int CE_alias_count =
    sizeof(CharacterEncodingAlias)/sizeof(CharacterEncodingAlias[0]);

CharacterEncoding InternalCharacterEncoding;

static int charset_initialised = 0;

static int alloc_unicode_to_iso(int i, int max)
{
	if(!(unicode_to_iso[i] = Malloc(max+1))){
	    fprintf(stderr, "Malloc failed in charset initialisation\n");
	    return -1;
		}
	return 0;
}

static void identity_iso_to_unicode(int i,int j,int jlim)
{
	for(; j<jlim; j++) iso_to_unicode[i][j] = j;
}

static void table_to_iso_to_unicode(int i, int *table, int j0, int jlim, int *cmax)
{
	int j, max= *cmax;
	for(j=j0; j<jlim; j++){
	    int code = table[j-j0];
	    iso_to_unicode[i][j] = code;
	    if(code > max) max = code;
		}
	*cmax = max;
}

static void identity_unicode_to_iso(int i,int j,int jlim)
{
	for(; j<jlim; j++) unicode_to_iso[i][j] = j;
}

static void unknown_unicode_to_iso(int i,int j,int jlim)
{
	for(; j<jlim; j++) unicode_to_iso[i][j] = '?';
}

static void table_to_unicode_to_iso(int i, int *table, int j0, int jlim)
{
	int j;
	for(j=j0; j<jlim; j++){
	    int code = table[j-j0];
	    if(code != -1)
		unicode_to_iso[i][code] = j;
		}
}

int init_charset(void)
{
    int i, max;
    union {char b[2]; short s;} bytes;

    if(charset_initialised)
	return 0;
    charset_initialised = 1;

    /* Determine internal encoding */

    bytes.s = 1;

#if CHAR_SIZE == 8
    InternalCharacterEncoding = CE_unspecified_ascii_superset;
#else
    InternalCharacterEncoding = (bytes.b[0] == 0) ? CE_UTF_16B : CE_UTF_16L;
#endif

    /* Make ISO-Latin-N tables */
    for(i=0; i<(NISO-1); i++){
		max = 0x9f;
		identity_iso_to_unicode(i,0,0xa0);
		table_to_iso_to_unicode(i,latin_table[i],0xa0,0x100,&max);

		iso_max_val[i] = max;
		if(alloc_unicode_to_iso(i,max)) return -1;
		identity_unicode_to_iso(i,0,0xa0);
		unknown_unicode_to_iso(i,0xa0,max);
		table_to_unicode_to_iso(i,latin_table[i],0xa0,0x100);
    	}


	/*cp-1252*/
	max = 0xff;
	i = NISO-1;
	identity_iso_to_unicode(i,0,0x80);
	table_to_iso_to_unicode(i,cp_1252_table,0x80,0xa0,&max);
	identity_iso_to_unicode(i,0xa0,0x100);

	iso_max_val[i] = max;
	if(alloc_unicode_to_iso(i,max)) return -1;
	identity_unicode_to_iso(i,0,0x80);
	unknown_unicode_to_iso(i,0x80,max);
	identity_unicode_to_iso(i,0xa0,0x100);
	table_to_unicode_to_iso(i,cp_1252_table,0x80,0xa0);

    return 0;
}

void deinit_charset(void)
{
    int i;
    if(!charset_initialised) return;
    charset_initialised = 0;
    for(i=0; i<NISO; i++) Free(unicode_to_iso[i]);
}

/* Return true if the encoding has 8-bit input units and is the same
   as ascii for characters <= 127 */

int EncodingIsAsciiSuperset(CharacterEncoding enc)
{
    return enc >= CE_unspecified_ascii_superset && enc <= CE_CP_1252;
}

/* 
 * Return true if enc1 and enc2 have the same size input units, and are
 * the same for Unicode <= 127.
 * If so, *enc3 is set to enc2 modified to have the same byte order as enc1.
 */

int EncodingsCompatible(CharacterEncoding enc1, CharacterEncoding enc2,
			CharacterEncoding *enc3)
{
    if(EncodingIsAsciiSuperset(enc1))
    {
	if(EncodingIsAsciiSuperset(enc2))
	{
	    *enc3 = enc2;
	    return 1;
	}
	return 0;
    }

    if(enc1 == CE_UTF_16B || enc1 == CE_ISO_10646_UCS_2B)
    {
	if(enc2 == CE_UTF_16B || enc2 == CE_UTF_16L)
	    *enc3 = CE_UTF_16B;
	else if(enc2 == CE_ISO_10646_UCS_2B || enc2 == CE_ISO_10646_UCS_2L)
	    *enc3 = CE_ISO_10646_UCS_2B;
	else
	    return 0;
	return 1;
    }

    if(enc1 == CE_UTF_16L || enc1 == CE_ISO_10646_UCS_2L)
    {
	if(enc2 == CE_UTF_16B || enc2 == CE_UTF_16L)
	    *enc3 = CE_UTF_16L;
	else if(enc2 == CE_ISO_10646_UCS_2B || enc2 == CE_ISO_10646_UCS_2L)
	    *enc3 = CE_ISO_10646_UCS_2L;
	else
	    return 0;
	return 1;
    }

    return 0;
}

CharacterEncoding FindEncoding(char8 *name)
{
    int i;

    for(i=0; i<CE_enum_count; i++)
	if(strcasecmp8(name, CharacterEncodingNameAndByteOrder[i]) == 0)
	    return (CharacterEncoding)i;

    for(i=0; i<CE_enum_count; i++)
	if(strcasecmp8(name, CharacterEncodingName[i]) == 0)
	    return (CharacterEncoding)i;

    for(i=0; i<CE_alias_count; i++)
	if(strcasecmp8(name, CharacterEncodingAlias[i].name) == 0)
	    return CharacterEncodingAlias[i].enc;

    return CE_unknown;
}

