#!/usr/bin/python
# coding: utf-8
# =============================================================================
# Author: Denis Wallerich
# Email: denis.wallerich@datim.fr
# Date: 2012-11-10
# Copyright: This module has been placed in the public domain.
#
# Ibm cobol (sql/cics/dli embedded) pygments Lexer
#
# ========== ==================================================================
# 1.2 - (2013-11-25)
#         - reordering variable,number,operator regex in cics/dli/sql
#	  - Tokenize cobol special-register
#         - codec module cp1147 removed
#         - change in DB2 and COBOL keywords 
#         - if encoding is in ('cp037','cp297','cp1140','cp1047','cp1147','cp500'),
#           it's managed as 'latin-1'
#
# 1.1 - (2012-11-16)
#         - Fix : float regex before integer
#         - Add inline-commentaire '*>' (will be supported in IBM Cobol V5)
#         - cics/dli color change
#         - CICS KEYWORDS extensions
#         - Add EBCDIC features:
#           automatic detection of EBCDIC encoding (cp500,cp1140,...) 
#	    also convert the raw binary input string in fixed utf-8 lines
#           "lrecl=" option can be passed (80 is default source IBM lrecl)
#           if not EBCDIC encoding detected, all lines are justified to
#           'lrecl=80' value (enforce existence of "MargeRight" tokens)
#	  Remarks : "chardet/guess" encoding do not detect EBCDIC chart
#
# ========== ==================================================================
# $TODO      - cobol-picture regex
#            - copy-replacing regex
#            - separate dli/cics/db2 commands/builtins and keywords
#            - performances 
# ========== ==================================================================

import re
from pygments.lexer import RegexLexer, include, bygroups, using, this
from pygments.token import Text, Other, Whitespace, Keyword, Name, Comment, \
                           String, Error, Number, Operator, Generic, Punctuation
from pygments.style import Style
from pygments.util import get_int_opt

class IBMCOBOLStyle(Style):
    """ I
    Ibm cobol mainframe (80 columns) style
    palette close to the TSO ISPF editor with option "hilite cobol"
    """
    default_style = ""
    background_color = "#111111"
    styles = {
        Error:                  'bg:#ff0000 #ffffff',
        Text.Tag:               'bg:#9609e9 border:#777777 #ffffff ',
        # custom tags:
        Text.Scrubol:           'italic #555555',
        Text.ScrubolTag:        'bg:#444444 border:#777777 #ffffff ',
        Text.ScrubolDoc:        '#dcdcdc',
        Text.ScrubolTagDoc:     'bg:#444444 border:#777777 #ffffff ',
        Text.ScrubolWarn:       'italic #555555',
        Text.ScrubolTagWarn:    'bg:#ff0000 border:#ff0000 #ffffff ',
        # 
        Comment.MargeLeft:      '#fcff70', 
        Comment.MargeRight:     '#fcff70', 
        Comment:                '#00c8ff',
        Comment.Debug:          '#0000c9',
        Comment.Continuation:   '#9609e9',
        Comment.Keyword:        'underline #00c8ff',
        Comment.Invisible:      '#252525',
        # cics
        Comment.CicsExec:       '#9609e9',
        Name.Cics:              '#fc9b00',
        Keyword.Cics:           '#fc3000',
        Punctuation.Cics:       '#b1f603',
        Comment.AllCics:        '#901060',
        Operator.Cics:          '#00d300',
        # dli 
        Comment.DliExec:        '#9609e9',
        Name.Dli:               '#fc9b00',
        Keyword.Dli:            '#fc3000',
        Punctuation.Dli:        '#b1f603',
        Comment.AllDli:         '#901060',
        Operator.Dli:           '#00d300',
        # db2    
        Comment.SqlExec:        '#9609e9',
        Comment.AllSql:         '#900060',
        Keyword.Sql:            '#933493',
        Name.Sql:               '#d898f4',
        Punctuation.Sql:        '#b1f603',
        Operator.Sql:           '#933493',
        # cobol
        Keyword:                '#ff0000',
        Keyword.Builtin:        '#9609e9',
        Name.Division:          'underline bold #ff0000',
        Name.CompileOpts:       'bold #ff0000',
        Name.Section:           'underline #ff0000',
        Name.Paragraphe:        'underline #00d300',
        Name:                   '#00d300',
        Name.LabelRef:          '#00f300',
        Name.Function:          '#900090',

        Punctuation:            '#b1f603',
        Number:                 '#f9f821',
        Operator:               '#007300',
        String:                 '#ffffff',
    }

# DB2V9 keywords
DB2_KEYWORDS = [ "ABSOLUTE", "ACCESS", "ACTION", "ACTIVATE", "ADA",
"ADD", "AFTER", "ALIAS", "ALL", "ALLOCATE", "ALLOW", "ALTER",
"ALTERIN", "ALWAYS", "AND", "ANY", "APPEND", "ARE", "AS", "ASC",
"ASCII", "ASSERTION", "ASSOCIATE", "ASUTIME", "AT", "ATOMIC",
"ATTRIBUTES", "AUTHORIZATION", "AUTHID", "AUTOMATIC", "AVG", "BEFORE",
"BEGIN", "BETWEEN", "BINARY", "BIND", "BINDADD","BIT", "BIT_LENGTH",
"BLOB", "BLOCKED", "BOTH", "BUFFERPOOL", "BUFFERPOOLS", "BY","C",
"CACHE", "CALL", "CALLED", "CALLER", "CAPTURE", "CARDINALITY",
"CASCADE", "CASCADED", "CASE", "CAST", "CATALOG", "CATALOG_NAME",
"CHANGE", "CHANGED", "CHANGES", "CHAR", "CHAR_LENGTH", "CHARACTER",
"CHARACTER_LENGTH", "CHECK", "CHECKED", "CLIENT", "CLOB", "CLOSE",
"CLUSTER", "COBOL", "COLLATE", "COLLATION", "COLLECT", "COLLID",
"COLUMN", "COMMENT", "COMMIT", "COMMITTED", "COMPARISONS", "CONCAT",
"CONDITION", "CONDITION_NUMBER","CONNECT", "CONNECTION",
"CONNECTION_NAME", "CONSERVATIVE", "CONSTRAINT", "CONSTRAINTS",
"CONTAINS", "CONTINUE", "CONTROL", "CONVERT", "COPY", "CORRELATION",
"CORR", "CORRESPONDING", "COUNT", "COUNT_BIG", "CPU", "C\+\+",
"CREATE", "CREATEIN", "CREATETAB", "CROSS", "CUBE", "CURRENT",
"CURRENT_DATE", "CURRENT_PATH", "CURRENT_SCHEMA", "CURRENT_SERVER",
"CURRENT_SQLID", "CURRENT_TIME", "CURRENT_TIMESTAMP",
"CURRENT_TIMEZONE", "CURRENT_USER", "CURSOR", "CURSORS",
"CURSOR_NAME", "CYCLE", "DATE", "DATA", "DATABASE", "DATALINK", "DAY",
"DAYS", "DB", "DBADM", "DBCLOB", "DBINFO", "DB2DARI", "DB2GENRL",
"DB2GENERAL", "DB2SQL", "DEADLOCKS", "DEALLOCATE", "DEC", "DECIMAL",
"DECLARE", "DEFAULT", "DEFAULTS", "DEFINE", "DEFINITION", "DEGREE",
"DEFER", "DEFERRABLE", "DEFERRED", "DELETE", "DESC", "DESCRIBE",
"DESCRIPTOR", "DETERMINISTIC", "DIAGNOSTICS", "DIGITS", "DIMENSIONS",
"DISABLE", "DISALLOW", "DISCONNECT", "DISPATCH", "DISTINCT", "DOMAIN",
"DO", "DOUBLE", "DROP", "DROPIN", "DYNAMIC", "EACH", "EBCDIC", "ELSE",
"ELSEIF", "EMPTY", "ENABLE", "END", "END-EXEC", "ERASE", "ESCAPE",
"EUR", "EVENT", "EXACT", "EXCEPT", "EXCEPTION", "EXCLUDE",
"EXCLUDING", "EXCLUSIVE", "EXEC", "EXECUTE", "EXISTS", "EXIT",
"EXPLAIN", "EXTENDED", "EXTENSION", "EXTERNAL", "EXTRACT", "FALSE",
"FEDERATED", "FENCED", "FETCH", "FILE", "FINAL", "FIRST", "FLOAT",
"FLUSH", "FOLLOWING", "FOR", "FORCE", "FOREIGN", "FORTRAN", "FOUND",
"FREEPAGE", "FROM", "FS", "FULL", "FUNCTION", "G", "GBPCACHE",
"GENERAL", "GENERATE", "GENERATED", "GET", "GLOBAL", "GO", "GOTO",
"GRANT", "GRAPHIC", "GROUP", "GROUPING", "HANDLER", "HAVING", "HOLD",
"HOUR", "HOURS", "IDENTITY", "IF", "IMMEDIATE", "IMPLICIT_SCHEMA",
"IN", "INCLUDE", "INCLUDING", "INCREMENT", "INDEX", "INDEXES",
"INDICATOR", "INHERIT", "INITIALLY", "INITIAL_INSTS", "INITIAL_IOS",
"INNER", "INOUT", "INPUT", "INSENSITIVE", "INSERT", "INSTEAD",
"INSTS_PER_ARGBYTE", "INSTS_PER_INVOC", "INT", "INTEGER", "INTEGRITY",
"INTERSECT", "INTERVAL", "INTO", "IOS_PER_ARGBYTE", "IOS_PER_INVOC",
"IS", "ISO", "ITERATE", "ISOLATION", "JAVA", "JIS", "JOIN",
"JULIAN_DAY", "K", "KEY", "KEYS", "LANGUAGE", "LARGE", "LAST",
"LAST_DAY", "LEADING", "LEAVE", "LEFT", "LENGTH", "LEVEL", "LIBRARY",
"LIKE", "LIMIT", "LINK", "LINKTYPE", "LOAD", "LOCAL", "LOCATOR",
"LOCATORS", "LOCK", "LOCKS", "LOCKSIZE", "LOGGED", "LONG", "LONGVAR",
"LOOP", "LOWER", "M", "MAINTAINED", "MAPPING", "MATCH", "MAX",
"MAXVALUE", "MESSAGE_TEXT", "METHOD", "MICROSECOND", "MICROSECONDS",
"MINUTE", "MINUTES", "MINVALUE", "MIXED", "MODE", "MODIFIES",
"MODULE", "MONITOR", "MONTH", "MONTHS", "MORE", "NAMED", "NAMES",
"NATIONAL", "NATURAL", "NCHAR", "NEW", "NEW_TABLE", "NEXT", "NEXTVAL",
"NICKNAME", "NO", "NOCACHE", "NOCYCLE", "NODE", "NOMAXVALUE",
"NOMINVALUE", "NONE", "NOORDER", "NOT", "NULL", "NULLABLE", "NULLS",
"NUMBER", "NUMERIC", "OBJECT", "OF", "OFF", "OLD", "OLD_TABLE", "OLE",
"OLEDB", "ON", "ONCE", "ONLINE", "ONLY", "OPEN", "OPTIMIZATION",
"OPTIMIZE", "OPTION", "OPTIONS", "OR", "ORDER", "OUT", "OUTER",
"OUTPUT", "OVER", "OVERLAPS", "PACKAGE", "PAD", "PARTIAL", "PARALLEL",
"PARAMETER", "PASCAL", "PASSTHRU", "PASSWORD", "PATH", "PARTITION",
"PARTITIONING", "PCTFREE", "PERCENT_ARGBYTES", "PERMISSION",
"PIECESIZE", "PIPE", "PLAN", "PLI", "POSITION", "PRECEDING",
"PRECISION", "PREPARE", "PRESERVE", "PRIMARY", "PRIOR", "PRIQTY",
"PRIVILEGES", "PROCEDURE", "PROGRAM", "PROTOCOL", "PUBLIC", "QUERY",
"QUERYNO", "RANGE", "READ", "READS", "REAL", "RECOMMEND", "RECOVERY",
"REF", "REFERENCE", "REFERENCES", "REFERENCING", "REFRESH",
"REGISTERS", "RELATIVE", "RELEASE", "RENAME", "REPEATABLE", "REPEAT",
"REPLACE", "REPLICATED", "RESET", "RESIDENT", "RESIGNAL", "RESOLVE",
"RESTART", "RESTORE", "RESTRICT", "RESULT", "RESULT_SET_LOCATOR",
"RETURNED_SQLSTATE", "RETAIN", "RETURN", "RETURNS", "RETURN_STATUS",
"REVOKE", "RIGHT", "ROLLBACK", "ROLLUP", "ROUTINE", "ROW",
"ROW_COUNT", "ROWID", "ROWS", "RUN", "S", "SAVEPOINT", "SBCS",
"SCALE", "SCHEMA", "SCOPE", "SCRATCHPAD", "SCROLL", "SEARCH",
"SECOND", "SECONDS", "SECQTY", "SECTION", "SELECT", "SELECTIVITY",
"SELF", "SEQUENCE", "SERIALIZABLE", "SERVER", "SERVER_NAME",
"SESSION", "SESSION_USER", "SET", "SETS", "SHARE", "SHRLEVEL",
"SIGNAL", "SIMPLE", "SIZE", "SMALLINT", "SNAPSHOT", "SOME", "SOURCE",
"SPACE", "SPECIAL", "SPECIFIC", "SQL", "SQLCODE", "SQLERROR",
"SQLEXCEPTION", "SQLWARNING", "SQLID", "SQLSTATE", "START", "STATE",
"STATEMENT", "STATISTICS", "STAY", "STOGROUP", "STORAGE", "STORED",
"STYLE", "SUB", "SUBSTRING", "SUMMARY", "SWITCH", "SYNONYM", "SYSTEM",
"SYSTEM_USER", "TABLE", "TABLES", "TABLE_NAME", "TABLESPACE",
"TABLESPACES", "TEMPLATE", "TEMPORARY", "THEN", "THREADSAFE", "TIME",
"TIMESTAMP", "TIMEZONE", "TIMEZONE_HOUR", "TIMEZONE_MINUTE", "TO",
"TRAILING", "TRANSACTION", "TRANSFORM", "TRANSLATE", "TRANSLATION",
"TREAT", "TRIGGER", "TRIM", "TRUE", "TYPE", "UNBOUNDED",
"UNCOMMITTED", "UNDER", "UNDO", "UNICODE", "UNION", "UNIQUE",
"UNKNOWN", "UNTIL", "UPDATE", "UPPER", "URL", "USA", "USE", "USAGE",
"USER", "USING", "VALUE", "VALUES", "VARCHAR", "VARGRAPHIC",
"VARIANT", "VARYING", "VCAT", "VERSION", "VIEW", "VOLATILE", "WHEN",
"WHENEVER", "WHERE", "WHILE", "WITH", "WITHOUT", "WORK", "WRAPPER",
"WRITE", "YEAR", "YEARS", "YES", "ZONE"]


DLI_KEYWORDS = [
"ACCEPT", "DLET", "GN", "GET", "NEXT", "GNP", "IN", "PARENT", "GU", "UNIQUE",
"ISRT", "INSERT", "POS", "POSITION", "REPL", "REPLACE", "RETRIEVE", "SCHD",
"SCHEDULE", "TERM", "TERMINATE", "CHKP", "CHECKPOINT", "DEQ", "LOAD", "LOG",
"QUERY", "REFRESH", "ROLB", "ROLL", "ROLS", "SETS", "SETU","STAT", "SYMCHKP",
"XRST"]

CICS_KEYWORDS = [ "DATASET", "NOHANDLE", "OF", "DEFAULT", "EOC",
"EOF", "ABCODE", "ABEND", "ABORT", "ABSTIME", "ACCOUNT", "ACCUM",
"ACTIVATE", "ACTPARTN", "ADD", "ADDRESS", "AID", "ALARM", "ALL",
"ALLOCATE", "ALTSCRN", "ANY_CICS", "ANYKEY", "APPLID", "ASIS",
"ASKIP", "ASKTIME", "ASM", "ASSIGN", "ATTACH", "ATTACHID", "ATTRB",
"AUTO", "AUTOPAGE", "AUXILIARY", "BANG", "BAR", "BASE", "BIF",
"BIT_AND", "BLANK", "BLINK", "BLOCK", "BOTTOM", "BOX", "BRT",
"BTRANS", "BUFFER", "BUFSZE", "BUILD", "CANCEL", "CARD", "CASE",
"CBIDERR", "CBUFF", "CCERROR", "CHAR_STRING", "CHARSZE", "CICS",
"CICS_ID", "CICSLETTER", "CLEAR", "CLRPARTN", "CNOTCOMPL", "COBOL",
"COLON", "COLOR", "COLUMN", "COMMA", "COMMAREA", "COMPLETE",
"CONDITION", "CONFIRM", "CONFIRMATION", "CONNECT", "CONSOLE",
"CONTROL", "CONVERSE", "CONVID", "COPY", "CSA", "CTLCHAR", "CTRL",
"CURRENT", "CURSOR", "CWA", "CWALENG", "DATA", "DATAONLY", "DATASTR",
"DATE", "DATEFORM", "DATESEP", "DAYCOUNT", "DAYOFMONTH", "DAYOFWEEK",
"DCT", "DDMMYY", "DEBKEY", "DEBREC", "DEEDIT", "DEFAULT", "DEFINE",
"DEFRESP", "DELAY", "DELETE", "DELETEQ", "DELIMITER", "DEQ", "DEST",
"DESTCOUNT", "DESTID", "DESTIDLENG", "DET", "DFHMDF", "DFHMDI",
"DFHMSD", "DFHPDI", "DFHPSD", "DIGIT", "DISABLED", "DISCONNECT",
"DOT", "DRK", "DSATTS", "DSECT", "DSIDERR", "DSSTAT", "DUMP",
"DUMPCODE", "DUPKEY", "DUPREC", "ECADDR", "EI", "EIB", "END", "ENDBR",
"ENDDATA", "ENDEXEC", "ENDFILE", "ENDINPT", "ENDOUTPUT", "ENQ",
"ENQBUSY", "ENTER", "ENTRY", "ENTRYNAME", "ENVDEFERR", "EOC", "EODS",
"EOF", "EQ", "EQUAL", "ERASE", "ERASEAUP", "ERROR", "ERRTERM",
"EVENT", "EXEC", "EXPIRED", "EXPONENT", "EXTATT", "EXTDS", "EXTRACT",
"FACILITY", "FCI", "FCT", "FIELD", "FIELDS", "FILE", "FINAL", "FIRST",
"FLDSEP", "FLENGTH", "FMH", "FMHPARM", "FORMATTIME", "FORMFEED",
"FREE", "FREEKB", "FREEMAIN", "FROM", "FROMLENGTH", "FRSET", "FSET",
"FULL", "FUNCERR", "GCHARS", "GCODES", "GENERIC", "GETMAIN",
"GRPNAME", "GT", "GTEQ", "HANDLE", "HEADER", "HEXCHAR", "HILIGHT",
"HOLD", "HONEOM", "HOST_ID", "HTAB", "IC", "IGNORE", "IGREQCD",
"IGREQID", "ILLOGIC", "IN", "IN_MULTI_LINE_COMMENT",
"IN_SINGLE_LINE_COMMENT", "INBFMH", "INITIAL", "INITIMG", "INOUT",
"INPARTN", "INTERVAL", "INTO", "INVERRTERM", "INVITE", "INVLDC",
"INVMPSZ", "INVPARTN", "INVPARTNSET", "INVREQ", "INVTSREQ", "IOERR",
"ISCINVREQ", "ISSUE", "ITEM", "ITEMERR", "IUTYPE", "JIDERR",
"JOURNAL", "JUSFIRST", "JUSLAST", "JUSTIFY", "KATAKANA", "KEYLENGTH",
"KEYNUMBER", "L40", "L64", "L80", "LABEL", "LANG", "LAST", "LBRACKET",
"LDC", "LDCMNEM", "LDCNUM", "LEAVEKB", "LEFT", "LENGERR", "LENGTH",
"LETTER", "LIGHTPEN", "LINE", "LINEADDR", "LINK", "LIST", "LOAD",
"LOGONMSG", "LPAREN", "LT", "LUNAME", "LUTYPE62", "MAIN", "MAP",
"MAPATTS", "MAPCOLUMN", "MAPERROR", "MAPFAIL", "MAPHEIGHT", "MAPLINE",
"MAPONLY", "MAPPED", "MAPSET", "MAPSFX", "MAPWIDTH", "MASSINSERT",
"MAXLENGTH", "MESSAGE", "MINIMUM", "MINUS", "MIXED", "MMDDYY", "MODE",
"MONITOR", "MONTHOFYEAR", "MSR", "MSRCONTROL", "MULTI_LINE_COMMENT",
"MUSTENTER", "MUSTFILL", "NAMEERROR", "NETNAME", "NEXT", "NLEOM",
"NO", "NOAUTOPAGE", "NOCHECK", "NOEDIT", "NOJBUFSP", "NOMAPPING",
"NONVAL", "NOPASSBKRD", "NOPASSBKWR", "NOQUEUE", "NORM", "NOSPACE",
"NOSPOOL", "NOSTART", "NOSTG", "NOSUSPEND", "NOTALLOC", "NOTAUTH",
"NOTE", "NOTFND", "NOTOPEN", "NOTRUNCATE", "NOWAIT", "NUM",
"NUM_CONSTANT", "NUMITEMS", "NUMREC", "NUMTAB", "OBFMT", "OCCURS",
"OFF", "ON", "OPCLASS", "OPERID", "OPERKEYS", "OPERPURGE", "OPID",
"OPSECURITY", "OUT", "OUTLINE", "OUTPARTN", "OVER", "OVERFLOW",
"PAGE", "PAGENUM", "PAGING", "PARTN", "PARTNFAIL", "PARTNPAGE",
"PARTNS", "PARTNSET", "PASS", "PASSBK", "PCT", "PERCENT", "PERFORM",
"PGMIDERR", "PICIN", "PICOUT", "PIPLENGTH", "PIPLIST", "PLI", "PLUS",
"POINT", "POP", "POS", "POST", "PPT", "PREPARE", "PRINSYSID", "PRINT",
"PROCESS", "PROCLENGTH", "PROCNAME", "PROFILE", "PROGRAM", "PROT",
"PROTECT", "PS", "PSEUDOBIN", "PURGE", "PUSH", "QBUSY", "QIDERR",
"QNAME", "QUERY", "QUESTION", "QUEUE", "QZERO", "RBA", "RBRACKET",
"RDATT", "READ", "READNEXT", "READPREV", "READQ", "RECEIVE", "RECFM",
"RELEASE", "REPLACE", "REQID", "RESET", "RESETBR", "RESOURCE",
"RESTART", "RETAIN", "RETPAGE", "RETRIEVE", "RETURN", "REVERSE",
"REWRITE", "RIDFLD", "RIGHT", "ROLLBACK", "ROLLEDBACK", "ROUTE",
"RPAREN", "RPG", "RPROCESS", "RRESOURCE", "RRN", "RTEFAIL", "RTERMID",
"RTESOME", "RTRANSID", "SAME", "SCRNHT", "SCRNWD", "SELNERR",
"SEMICOLON", "SEND", "SESSBUSY", "SESSION", "SESSIONERR", "SET",
"SHARED", "SIGDATA", "SIGNAL", "SINGLE", "SINGLE_LINE_COMMENT", "SIT",
"SIZE", "SLASH", "SOSI", "STANDARD", "STAR", "START", "STARTBR",
"STARTCODE", "STATIONID", "STORAGE", "STRFIELD", "SUBADDR", "SUFFIX",
"SUSPEND", "SYNCLEVEL", "SYNCPOINT", "SYSBUSY", "SYSID", "SYSIDERR",
"SYSTEM", "TABLES", "TASK", "TCT", "TCTUA", "TCTUALENG", "TD",
"TELLERID", "TERM", "TERMCODE", "TERMERR", "TERMID", "TERMIDERR",
"TERMINAL", "TEXT", "TIME", "TIMESEP", "TIOAPFX", "TITLE", "TOLENGTH",
"TRACE", "TRACEID", "TRAILER", "TRANSID", "TRANSIDERR", "TRANSP",
"TRIGGER", "TS", "TSIOERR", "TWA", "TWALENG", "TYPE", "UNATTEND",
"UNDER", "UNDERLINE", "UNEXPIN", "UNLOCK", "UNPROT", "UPDATE",
"USER","USERID", "VALIDATION", "VALIDN", "VIEWPOS", "VIEWSZE",
"VOLUME", "VOLUMELENG", "VTAB", "WAIT", "WPMEDIA1", "WPMEDIA2",
"WPMEDIA3", "WPMEDIA4", "WRBRK", "WRITE", "WRITEQ", "WRONGSTAT",
"XCTL", "XINIT", "XOR", "YEAR", "YES", "YYDDD", "YYDDMM", "YYMMDD",
"ZERO"]

COBOL_KEYWORDS = [ "ACCEPT", "ACCESS", "ADD", "ADDRESS", "ADVANCING",
"AFTER", "ALL", "ALPHABET", "ALPHABETIC", "ALPHABETIC-LOWER",
"ALPHABETIC-UPPER", "ALPHANUMERIC", "ALPHANUMERIC-EDITED", "ALSO",
"ALTER", "ALTERNATE", "AND", "ANY", "APPLY", "ARE", "AREA", "AREAS",
"ASCENDING", "ASSIGN", "AT", "AUTHOR", "BACK", "BEFORE", "BEGINNING",
"BINARY", "BLANK", "BLOCK", "BOTTOM", "BY", "CALL", "CANCEL", "CBL",
"CHARACTER", "CHARACTERS", "CLASS", "CLOSE", "CODE-SET", "COLLATING",
"COMMA", "COMMON", "COMP", "COMP-1", "COMP-2", "COMP-3", "COMP-4",
"COMPUTATIONAL", "COMPUTATIONAL-1", "COMPUTATIONAL-2",
"COMPUTATIONAL-3", "COMPUTATIONAL-4", "COMPUTE", "CONFIGURATION",
"CONTAINS", "CONTENT", "CONTINUE", "CONVERTING", "COPY", "CORR",
"CORRESPONDING", "COUNT", "CURRENCY", "DATA", "DATE", "DATE-COMPILED",
"DATE-WRITTEN", "DAY", "DAY-OF-WEEK", "DBCS", "DEBUGGING",
"DECIMAL-POINT", "DECLARATIVES", "DELETE", "DELIMITED", "DELIMITER",
"DEPENDING", "DESCENDING", "DISPLAY", "DISPLAY-1", "DIVIDE",
"DIVISION", "DOWN", "DUPLICATES", "DYNAMIC", "EBCDIC", "EGCS", "ELSE",
"END", "END-ADD", "END-CALL", "END-COMPUTE", "END-DELETE",
"END-DIVIDE", "END-EVALUATE", "END-IF", "END-MULTIPLY", "END-OF-PAGE",
"END-PERFORM", "END-READ", "END-RETURN", "END-REWRITE", "END-SEARCH",
"END-START", "END-STRING", "END-SUBTRACT", "END-UNSTRING",
"END-WRITE", "ENDING", "ENTRY", "ENVIRONMENT", "EOP", "EQUAL",
"ERROR", "EVALUATE", "EVERY", "EXCEPTION", "EXIT", "EXTEND",
"EXTERNAL", "FALSE", "FD", "FILE", "FILE-CONTROL", "GO", "FILLER",
"FIRST", "FOOTING", "FOR", "FROM", "GENERATE", "GIVING", "GLOBAL",
"GOBACK", "GREATER", "HIGH-VALUE", "HIGH-VALUES", "I-O",
"I-O-CONTROL", "ID", "IDENTIFICATION", "IF", "IN", "INDEX", "INDEXED",
"INITIAL", "INITIALIZE", "INPUT", "INPUT-OUTPUT", "INSPECT",
"INSTALLATION", "INTO", "INVALID", "IS", "JUST", "JUSTIFIED", "KANJI",
"KEY", "LABEL", "LEADING", "LEFT", "LENGTH", "LESS", "LINAGE",
"LINAGE-COUNTER", "LINE", "LINES", "LINKAGE", "LOCK", "LOW-VALUE",
"LOW-VALUES", "MEMORY", "MERGE", "MODE", "MODULES", "MORE-LABELS",
"MOVE", "MULTIPLE", "MULTIPLY", "NATIVE", "NEGATIVE", "NEXT", "NO",
"NOT", "NULL", "NULLS", "NUMERIC", "NUMERIC-EDITED",
"OBJECT-COMPUTER", "OCCURS", "OF", "OFF", "OMITTED", "ON", "OPEN",
"OPTIONAL", "OR", "ORDER", "ORGANIZATION", "OTHER", "OUTPUT",
"OVERFLOW", "PACKED-DECIMAL", "PADDING", "PAGE", "PARSE", "PASSWORD",
"PERFORM", "PIC", "PICTURE", "POINTER", "POSITION", "POSITIVE",
"PROCEDURE", "PROCEDURE-POINTER", "PROCEDURES", "PROCEED", "PROCESS",
"PROGRAM", "PROGRAM-ID", "QUOTE", "QUOTES", "RANDOM", "READ",
"RECORD", "RECORD-KEY", "RECORDING", "RECORDS", "RECURSIVE",
"REDEFINES", "REEL", "REFERENCE", "RELATIVE", "RELEASE", "REMAINDER",
"REMARKS", "REMOVAL", "RENAMES", "REPLACING", "RERUN", "RESERVE",
"RETURN", "RETURNING", "REVERSED", "REWIND", "REWRITE", "RIGHT",
"ROUNDED", "RUN", "SAME", "SD", "SEARCH", "SECTION", "SECURITY",
"SEGMENT-LIMIT", "SELECT", "SENTENCE", "SEPARATE", "SEQUENCE",
"SEQUENTIAL", "SET", "SIGN", "SIZE", "SORT", "SORT-MERGE",
"SOURCE-COMPUTER", "SPACE", "SPACES", "SPECIAL-NAMES", "STANDARD",
"STANDARD-1", "STANDARD-2", "START", "STATUS", "STOP", "STRING",
"SUBTRACT", "SUPPRESS", "SYMBOLIC", "SYNC", "SYNCHRONIZED",
"TALLYING", "TAPE", "TEST", "THAN", "THEN", "THROUGH", "THRU", "TIME",
"TIMES", "TO", "TOP", "TRAILING", "TRUE", "TRUETEST", "UNIT",
"UNSTRING", "UNTIL", "UP", "UPON", "USAGE", "USE", "USING", "VALUE",
"VALUES", "VARYING", "WHEN", "WITH", "WORDS", "WORKING-STORAGE",
"WRITE", "WRITE-ONLY", "XML", "ZERO", "ZEROES", "ZEROS"]

COBOL_INTRINSICS = [ "ABS", "ACOS", "ANNUITY", "ASIN", "ATAN", "CHAR",
"CHAR-NATIONAL", "COS", "SIN", "CURRENT-DATE", "DATE-OF-INTEGER",
"DATEVAL", "DATE-TO-YYYYMMDD", "DAY-TO-YYYYDDD", "DAY-OF-INTEGER",
"DISPLAY-OF", "EXP", "EXP10", "FACTORIAL", "FRACTION-PART",
"INTEGER", "INTEGER-OF-BOOLEAN", "INTEGER-OF-DATE", "INTEGER-OF-DAY",
"INTEGER-PART", "LENGTH", "LENGTH-AN", "LOG", "LOG10", "LOWER-CASE",
"NUMVAL", "MAX", "MEAN", "MEDIAN", "MIDRANGE", "MIN", "MOD",
"NATIONAL-OF", "NUMVAL", "NUMVAL-C", "ORD", "ORD-MAX", "ORD-MIN",
"PRESENT-VALUE", "RANDOM", "RANGE", "REM", "REVERSE", "SQRT",
"STANDARD-DEVIATION", "SUM", "TAN", "UNDATE", "UPPER-CASE",
"VARIANCE", "WHEN-COMPILED", "YEAR-TO-YYYY", "YEARWINDOW"]

COBOL_SPECIAL_REGISTERS = [
"DEBUG-ITEM", "XML-EVENT", "XML-TEXT", "XML-NTEXT", "XML-CODE",
"SQLCODE", "TALLY", "ADDRESS\s*OF", "LENGTH", "RETURN-CODE",
"SORT-CONTROL", "SORT-CORE-SIZE", "SORT-FILE-SIZE", "SORT-MESSAGE",
"SORT-MODE-SIZE", "SORT-RETURN", "JNIENVPTR", "LINAGE-COUNTER",
"RETURN-CODE", "SHIFT-OUT", "SHIFT-IN", "WHEN-COMPILED" ]


class IBMCOBOLLexer(RegexLexer):
    """
    Pygments Lexer for the Enterprise Cobol for z/OS and embedded Db2/Cics/DLi
    features. Many early programming languages, including Fortran, Cobol and
    the various IBM assembler languages, used only the first 7-72 columns
    of a 80-column card

 MAINFRAME COBOL CODING FORM:
 ---------------------------
           Columns
           1- 6       Tags, Remarks or Sequence numbers identifying pages or lines of a program
           7          Continuation, comment or starting of a new page
           8 - 72     COBOL program statements
           73- 80     Tags, Remarks or Sequence numbers (often garbage...)
  
   =>    Column 7  * (asterisk) designates entire line as comment
                    / (slash) forces page break when printing source listing
          - (dash) to indicate continuation of nonnumeric literal
   =>    Columns 8-72 divided into two areas
           - Area A - columns 8 to 11
           - Area B - columns 12 to 72
   Division, section and paragraph-names must all begin in Area A and end with a period.

   CBL/PROCESS statement can start in columns 1 through 70
   Code the PROCESS statement before the IDENTIFICATION DIVISION header and before
   any comment lines or compiler-directing statements.

 SOME EBCDIC CODEPAGES:
 ---------------------
    cp037  : Australie, Brésil, Canada, Nouvelle Zélande, Portugal, Afrique du Sud, USA
    cp297  : EBCDIC "France"
    cp500  : francophones (suisses, belges, canadiennes...)
    cp819  : ISO-8859-1 (Latin 1),
    cp1047 : cp037 utilisé dans les services UNIX des S/390 et z/OS, et sous VM/ESA.
    cp1147 : cp297 + Euro sign
    cp1148 : cp500 + Euro sign
"""

    def __init__(self, **options):
        try:
            if options['encoding'] in ('cp037', 'cp297', 'cp1140', 'cp1047',
                                       'cp1147', 'cp500'):
                self.ebcdic_encoding = options['encoding']
                options['encoding'] = 'latin1'
            else:
                self.ebcdic_encoding = None
            RegexLexer.__init__(self, **options)
        except:
            self.ebcdic_encoding = None
            RegexLexer.__init__(self, **options)
        
        self.lrecl    = get_int_opt(options, 'lrecl', default=80)
        self.stripnl  = False
        self.stripall = False
        self.tabsize  = 0
       
        if self.ebcdic_encoding == 'cp1147':
            import cp1147
        if self.encoding == 'chardet':
            self.encoding = 'guess'  # chardet it's not efficient with EBCDIC

            
    def get_tokens_unprocessed(self, text):
        # minimum EBCDIC test (suffisant for text)
        if  text[:1024].count('\x40') > text[:1024].count('\x20'): 
            #print '#EBCDIC' 
            if self.encoding in ('guess','latin1'):
                self.encoding = (self.ebcdic_encoding
                                 or 'cp500') # EBCDIC Latin-1
                text = text.encode('latin1').decode(self.encoding)
            else:
                text = text.encode(self.encoding).decode(self.ebcdic_encoding
                                                       or 'cp500')
                self.encoding = self.ebcdic_encoding or 'cp500' # EBCDIC Latin-1
            #print '#EBCDIC:',self.encoding   
        if (self.encoding != 'guess' and        
            ' 012ABC'.encode(self.encoding) == "\x40\xf0\xf1\xf2\xc1\xc2\xc3"):
            #good EBCDIC
            if self.ensurenl:
                text_len = len(text) - 1 # since ensurenl add '\n'
            else:
                text_len = len(text)
            if text_len % self.lrecl == 0: #to preserve against "MVS VB record"
                text = ''.join([text[i:i+self.lrecl] + '\n' #split block
                                for i in range(0, text_len, self.lrecl)])
            else: 
                raise ValueError("inconsistent textlen %i and lrecl %i (varying"
                                 "record length ?)"% (text_len, self.lrecl))
        else:
            #ASCII:
            text = ''.join([l.ljust(self.lrecl) + '\n'
                            for l in text.splitlines()]) # enforce 80 columns
        
        for item in RegexLexer.get_tokens_unprocessed(self, text): 
            yield item
       

    name = 'ibmcobol'
    aliases = ['cobol', 'ibmcob', 'ibm_cob', 'IBM_COBOL']
    filenames = ['*.cbl', '*.CBL', '*.cob', '*.COB']
    mimetypes = ["text/x-cobol"]
    flags = re.IGNORECASE | re.DOTALL | re.MULTILINE
      
    start_boundarie = r"(?<![-_])\b"
    end_boundarie   = r"(?=\b[^-_])"

    cobol_name = (r'(([0-9]+[\-\_][0-9\-\_]*[A-Za-z][A-Za-z0-9\-\_]*'
                  '[A-Za-z0-9])|([0-9]+[\-][A-Za-z0-9\-\_]*)'                               
                  '|([0-9]*[A-Za-z][A-Za-z0-9\-\_]*[A-Za-z0-9]*))')       

    #(?!.{0,7}\n) => no match in right margin 
    #(?<=\n.{7})  => match in left margin

    custom_tag = "MyTag"
    # custom tags in left margin
    custom_marge_tag0 = r"\(\^[^_^w]\^\)"
    custom_marge_tag1 = r"\(\^_\^\)"
    custom_marge_tag2 = r"\(\^w\^\)"


# $TODO: pictures regex
# ---------------------
# ( "PICTURE" | "PIC" ) [ "IS" ] picture-string
#picture-string =
#currency? (picchar+ repeat?)+ (punctuation (picchar+ repeat?)+)*
#auxiliaries
# begin
#  currency = ~[0-9ABCDPRSVXZa-z\*\+\-\/\,\.\;\(\)\=\'\"\ \n]
#  picchar = 
#   ( [ABEGPSVXZabegpsvxz90\+\-\*\$]
#   | "CR"
#   | "DB" )
#  repeat = "(" [0-9]+ ")"
#  punctuation = [\/\,\.\:]
# end 
    
    tokens = {
     'root':
          [
           include('special-in-cobol-tag'),
           include('inline-comments'),
           (r"(^\s*(CBL|PROCESS)[^\n]*)",  Name.CompileOpts) ,
           (r"(^.{6})([\*\/].{65})(.{8})",
            bygroups(Comment.MargeLeft, Comment, Comment.MargeRight)),
           (r"(^.{6})([D].{65})(.{8})",
            bygroups(Comment.MargeLeft, Comment.Debug, Comment.MargeRight)),
           (r"(^.{6})([ -])",
            bygroups(Comment.MargeLeft ,Comment.Continuation), 'cobol-content'),
           ],

    'cobol-content':
           [
            (r'[^\n]{1,8}\n',   Comment.MargeRight, '#pop'),
            (r'EXEC\s*SQL\s*',  Comment.SqlExec, 'sql-content'),
            (r'\$sql\$\s*',     Comment.Invisible, 'sql-content'), #invisible!
            (r'EXEC\s*CICS\s*', Comment.SqlExec,'cics-content'),
            (r'EXEC\s*DLI\s*',  Comment.SqlExec, 'dli-content'),
            include('inline-comments'),
            include('sec-div'),
            include('pgmid'),
            include('dummy'),
            include('paragraphe'),
            include('label-ref'),  # perform & goto label: href navigation               
            include('intrinsics'),
            include('special-registers'),
            include('strings'),
            include('ponctuation'),
            include('keywords'),
            include('variable'),
            include('numbers'), # numbers after variables !
            include('operator'), # operators after variables !
            (r'[ ]+', Text)
           ],

      'sec-div':[
            (r'(DECLARATIVES|END)(\s+)(DECLARATIVES)',
             bygroups(Name.Division,Text,Name.Division)),
            (r'([a-zA-Z0-9-_]+)(\s+)(DIVISION)',
             bygroups(Name.Division,Text,Name.Division)),
            (r'([a-zA-Z0-9-_]+)(\s+)(SECTION)',
             bygroups(Name.Section,Text,Name.Section)),
            (r'(SPECIAL\-NAMES)',
              bygroups(Name.Section)),
           ],
      
      'paragraphe':[
      (r'((?<=\n.{7})(?!(SKIP.? |EJECT |EXEC |COPY ))[a-zA-Z0-9-_]+)(?=\s*[.])',
       Name.Paragraphe)
       ],

      'label-ref':[
                  (r'(PERFORM|GO)(\s+)((?!(UNTIL |VARYING |TEST |WITH ))'
                   + cobol_name + ')', bygroups(Keyword,Text,Name.LabelRef))
                   ],

      'pgmid':[
                 (r'((?<=\n.{7})PROGRAM-ID|END\s+PROGRAM)(\s*[.]?)([^.^\n]*)',
                      bygroups(Name.Section,Punctuation,Keyword.Builtin))
                   ],
      'dummy':[
       (r'((?<=\n.{7})TITLE|REMARKS|AUTHOR|DATE-COMPILED|DATE-WRITTEN)(\s*[.][^\n]*)',
                      bygroups(Comment.Keyword,Comment))
                   ],
  
      'keywords':[
            (start_boundarie + '(' + '|'.join(COBOL_KEYWORDS) + ')'
             + end_boundarie, Keyword),
            (r'([\=\<\>])',Keyword) 
           ],

      'variable': [(cobol_name,Name)],

      'operator': [(r'((?!.{0,7}\n)[\/\+\-\*])', Operator)],

      'ponctuation': [(r'([~&\^#\|\[\]`!@;,\.():])', Punctuation)],
 
      'intrinsics': [
             (r'FUNCTION\s*' + start_boundarie +
               '(' + '|'.join(COBOL_INTRINSICS) + ')' + end_boundarie,
              Name.Function)
            ],
      'special-registers':[
            (start_boundarie + '(' + '|'.join(COBOL_SPECIAL_REGISTERS) + ')'
             + end_boundarie, Keyword.Builtin),
           ],


      'strings': [
             (r"(\b[xXzZ])?'[^'\\\n]*(\\.[^'\\\n]*)*'?", String.Single),
             (r'(\b[xXzZ])?"[^"\\\n]*(\\.[^"\\\n]*)*"?', String.Double),
            ],

      'numbers': [
             (r'[+-]?\d*\.\d+([eE][-+]?\d+)?', Number),
             (r'[+-]?\d+\.\d*([eE][-+]?\d+)?', Number),
             (r'[+-]?\d+(?![A-Z-_])', Number),
            ],       

     'dli-content': [
            include('special-in-exec-tag'),
            include('comments'),
            (r'END-EXEC',Comment.DliExec,'#pop'),
            (start_boundarie + '(' + '|'.join(DLI_KEYWORDS) + ')'
             + end_boundarie, Keyword.Dli),
            include('strings'),
            (r'[;:()\[\],\.]', Punctuation.Dli),
            (cobol_name,Name.Dli), 
            include('numbers'),
            (r'[+*/<>=~!@#%^&|`?^-]', Operator),
           ],

     'cics-content': [
            include('special-in-exec-tag'),
            include('comments'),
            (r'END-EXEC',Comment.CicsExec,'#pop'),
            (start_boundarie + '(' + '|'.join(CICS_KEYWORDS) + ')'
             + end_boundarie, Keyword.Cics),
            include('strings'),
            (r'[;:()\[\],\.]', Punctuation.Cics),
            (cobol_name,Name.Cics),
            include('numbers'),
            (r'[+*/<>=~!@#%^&|`?^-]', Operator),
           ],
     
     'sql-content': [
            include('special-in-exec-tag'),
            include('comments'),
            (r'END-EXEC',Comment.SqlExec,'#pop'),
            (r'--.*?\n', Comment),
            (start_boundarie + '(' + '|'.join(DB2_KEYWORDS) + ')'
             + end_boundarie, Keyword.Sql),
            include('strings'),
            (r'[;:()\[\],\.]', Punctuation.Sql),     
            (cobol_name,Name.Sql),
            include('numbers'),
            (r'(?!.{0,7}\n)[+*/<>=~!@#%^&|`?^-]', Operator.Sql),
               ],

   'comments': [
            include('inline-comments'),
            (r'(?<=\n).{6}', Comment.MargeLeft),
            (r'[^\n]{0,8}\n', Comment.MargeRight),
            (r'(?<=\n.{6})\*.*?\n', Comment),
            (r'\s+', Text)
              ],    

   'inline-comments': [
            (r"\*\>.*?$", Comment),
            (r"(SKIP.?|EJECT)", Comment) ],    

   'special-in-cobol-tag': [
            (r"(^" + custom_tag + r")(.[^\*])",
              bygroups(Text.Tag, Comment.Continuation),'cobol-content'),
            (r"(^" + custom_marge_tag0 + r")(.[^\*])",
              bygroups(Text.ScrubolTag, Comment.Continuation),'cobol-content'), 
             include('mytags'),
            ],

   'special-in-exec-tag': [
            (r"(^" + custom_tag + r")(.[^\*])",
              bygroups(Text.Tag, Comment.Continuation)), 
            (r"(^" + custom_marge_tag0 + r")(.[^\*])",
              bygroups(Text.ScrubolTag, Comment.Continuation)), 
            include('mytags')
              ],
 
   'mytags': [
             (r"(^" + custom_marge_tag0 + r")(.[^\*])",
              bygroups(Text.Tag, Comment.Continuation)), 
            (r"(^" + custom_marge_tag0 + r")(.\*.*?\n)",
                 bygroups(Text.ScrubolTag, Text.Scrubol)),
            (r"(^" + custom_marge_tag1 + r")(.\*.*?\n)",
                 bygroups(Text.ScrubolTagDoc, Text.ScrubolDoc)),
            (r"(^" + custom_marge_tag2 + r")(.\*.*?\n)",
                 bygroups(Text.ScrubolTagWarn, Text.ScrubolWarn)),
         ],
    }

