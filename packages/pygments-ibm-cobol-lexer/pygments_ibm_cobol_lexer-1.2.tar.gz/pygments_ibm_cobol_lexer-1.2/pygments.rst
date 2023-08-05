=============================================
Cobol IBM Mainframe syntax lexer for Pygments
=============================================        
**This package contains a Pygments Lexer for mainframe cobol.**

**The lexer parses the Enterprise Cobol dialect (V3R4) for z/OS, including utilizing embedded  Db2/Sql, Cics and DLi**

.. contents:: Contents
    :depth: 5

mainframe cobol coding form
===========================
Many early programming languages, including PL/1, Fortran, Cobol and the various IBM assembler languages,
used only the first 7-72 columns of a 80-column card

    +----------+--------------------------------------------------------------------------+
    | Columns  |                                                                          |
    +==========+==========================================================================+
    | 1- 6     |Tags, Remarks or Sequence numbers identifying pages or lines of a program |
    +----------+--------------------------------------------------------------------------+
    | 7        | - ``*`` (asterisk) designates entire line as comment                     |
    |          | - ``/`` (slash) forces page break when printing source listing           |
    |          | - ``-`` (dash) to indicate continuation of nonnumeric literal            |
    |          | - ``D``  to indicate debug line cobol statements                         |
    +----------+--------------------------------------------------------------------------+
    | 8 - 72   |COBOL program statements, divided into two areas :                        |
    |          | - Area A : columns 8 to 11                                               |
    |          | - Area B : columns 12 to 72                                              |
    +----------+--------------------------------------------------------------------------+
    | 73 - 80  |   Tags, Remarks or Sequence numbers (often garbage...)                   |
    +----------+------------+-------------------------------------------------------------+

Division, section and paragraph-names must all begin in Area A and end with a period.

``CBL/PROCESS`` directives statement can start in columns 1 through 70
       
Installation
============ 
The lexer is available as a Pip package:
    
``$ sudo pip install pygments_ibm_cobol_lexer``

Or using easy_install:

``$ sudo easy_install pygments_ibm_cobol_lexer``
        
Usage
===== 
After installation the ibmcobol Lexer and ibmcobol Style automatically registers itself for files with the ".cbl" extensions.

 Therefore, cmdline usage is easy:
   + Ascii input :

    ``pygmentize -O full,style=ibmcobol,encoding=latin1 -o HORREUR.html HORREUR.ascii.cbl``

   + Ebcdic input (in this case it's necessary to specify outencoding value): 

    ``pygmentize -O full,style=ibmcobol,encoding=cp1147,outencoding=latin1 -o COB001.html COB001.cp1147.cbl``

 Or as library usage:
 
 .. sourcecode :: python

      from pygments import highlight
      from pygments.formatters import HtmlFormatter
      from pygments_ibm_cobol_lexer import IBMCOBOLLexer, IBMCOBOLStyle
      my_code = open("cobol_ebcdic.cbl",'rb').read()
      highlight(my_code,IBMCOBOLLexer(encoding='cp1140'),
	          HtmlFormatter(style=IBMCOBOLStyle, full=True),
	          open('test.html','w'))

 Also see the ``pygments_tests/`` directory

  
About cp1147
============
 I have files coded IBM1147 (EBCDIC french + euro sign), I was forced to write my own codec ``cp1147``, very close  to the ``cp500`` (Canada, Belgium), it diverges on the characters "@\°{}§ùµ£à[€`¨#]~éè¦ç" :
 
This codec is available as a Pip package:
    
``$ sudo pip install cp1147``

Changelog
=========
 1.2 - (2013-11-25)
         - reordering variable,number,operator regex in cics/dli/sql
         - Tokenize cobol special-register
         - codec module cp1147 removed
         - change in DB2 and COBOL keywords 
         - if encoding is in ('cp037','cp297','cp1140','cp1047','cp1147','cp500'), it's managed as 'latin-1' 

 1.1 - (2012-11-19)
 Minor Fix + EBCDIC enhancements:

	 - Fix : float regex detection before integer detection
         - Add inline-commentaire ``*>`` (not the IBM default)
         - Change cics/dli keywords color...
         - Extend CICS_KEYWORDS, remove EJECT/SKIP from COBOL_KEYWORDS (treated as comments)
         - each ASCII input lines is padded to 80 columns
         - Add EBCDIC features:

           * add my own french codec cp1147
           * if EBCDIC encoding is passed (cp500,cp1140,...) or detected,convert the binary input raw text in 80 columns fixed lines
           * ``encoding=chardet`` (slowly) does not detect EBCDIC chart,it's override with ``encoding=guess`` 
           * "guess EBCDIC" is defaulted to ``self.encoding='cp500'``

 1.0 - (2012-11-12) 
 Initial release.





