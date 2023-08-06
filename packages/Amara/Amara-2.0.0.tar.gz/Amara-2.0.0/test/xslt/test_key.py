########################################################################
# test/xslt/test_key.py
import os
from amara.xslt import XsltError

from xslt_support import _run_xml, _run_html, _run_text

module_name = os.path.dirname(__file__)
filename = os.path.join(module_name, "addr_book1.xml")
FILE_SOURCE_XML = open(filename).read()
FILE_URI = "file:" + filename
TRANSFORM_URI = "file:" + __file__

def test_key_1():
    """basic keys"""
    _run_html(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- silly bit of overkill for key usage, but executes the basic test -->
  <xsl:key name='name' match='ENTRY' use='NAME'/>

  <xsl:template match="/">
    <HTML>
      <HEAD>
        <TITLE>Address Book</TITLE>
      </HEAD>
      <BODY>
        <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
        <TABLE><xsl:apply-templates/></TABLE>
      </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
    <TR>
      <xsl:apply-templates select='NAME'/>
    </TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B ID='{key("name", .)/EMAIL}'><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
\x20\x20\x20\x20
      <TR>
        <TD ALIGN='CENTER'><B ID='pieter.aaron@inter.net'>Pieter Aaron</B></TD>
      </TR>
\x20\x20\x20\x20
      <TR>
        <TD ALIGN='CENTER'><B ID='endubuisi@spamtron.com'>Emeka Ndubuisi</B></TD>
      </TR>
\x20\x20\x20\x20
      <TR>
        <TD ALIGN='CENTER'><B ID='vxz@magog.ru'>Vasia Zhugenev</B></TD>
      </TR>

    </TABLE>
  </BODY>
</HTML>""")

def test_key_2():
    """keys scoped to context document"""
    _run_text(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method='text'/>

  <xsl:key name='name' match='*' use='name()'/>

  <xsl:template match="/">
    <xsl:for-each select=".">
      Entries from keys: <xsl:value-of select="count(key('name', 'ENTRY'))"/>
      Template from keys: <xsl:value-of select="count(key('name', 'xsl:template'))"/>
    </xsl:for-each>
    <xsl:for-each select="document('')">
      Entries from keys: <xsl:value-of select="count(key('name', 'ENTRY'))"/>
      Template from keys: <xsl:value-of select="count(key('name', 'xsl:template'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """
      Entries from keys: 3
      Template from keys: 0
      Entries from keys: 0
      Template from keys: 1"""
        )

def test_key_3():
    """keys using patterns of form `ns:*`"""
    _run_text(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com"
>

  <xsl:output method="text"/>

  <xsl:key name='k1' match='xsl:*' use='name()'/>
  <xsl:key name='k2' match='x:*' use='@id'/>

  <x:grail id="ein"/>
  <x:grail id="zwo"/>
  <x:knicht id="drei"/>
  <x:knicht id="vier"/>

  <xsl:template match="/">
    <xsl:for-each select="document('')">
    Entries from key 1: <xsl:copy-of select="count(key('k1', 'xsl:template'))"/>
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """
    Entries from key 1: 1
    Entries from key 2: 1"""
        )

def test_key_4():
    """imported keys"""
    _run_text(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="test-key-import-1.xslt"/>

  <xsl:output method="text"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="$sty-doc">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """
    Entries from key 1: 1
    Entries from key 2: 1"""
        )

def test_key_5():
    """included keys (test_key_5)"""
    _run_text(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:include href="test-key-import-1.xslt"/>

  <xsl:output method="text"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="$sty-doc">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """
    Entries from key 1: 1
    Entries from key 2: 1"""
        )

def test_key_6():
    """included keys (test_key_6)"""
    _run_text(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="test-key-import-1.xslt"/>

  <xsl:output method="text"/>

  <!--
    creates a silly key which indexes all ENTRY elements in the doc
    as 'pa' just to be different from the key in the import with the
    same name
    -->
  <xsl:key name='k1' match='ENTRY' use="'pa'"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="$sty-doc">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """
    Entries from key 1: 3
    Entries from key 2: 1""")


def test_key_7():
    """included keys (test_key_7)"""
    _run_xml(
        source_xml = FILE_SOURCE_XML,
        source_uri = FILE_URI,
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com/x"
>

  <xsl:output method="xml"/>

  <xsl:key name='k1' match='x:*' use='local-name()'/>
  <xsl:key name='k1' match='x:*' use='@id'/>

  <x:vier id="ein"/>
  <x:drei id="zwo"/>
  <x:zwo id="drei"/>
  <x:ein id="vier"/>

  <xsl:template match="/">
    <result>
      <xsl:for-each select="document('')">
        <xsl:copy-of select="key('k1', 'drei')"/>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:x="http://spam.com/x"><x:drei id="zwo"/><x:zwo id="drei"/></result>"""
        )


def test_key_8():
    """included keys (test_key_8)"""
    _run_xml(
        source_xml = "<dummy/>",
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com/x"
  xmlns:y="http://spam.com/y"
>

  <xsl:output method="xml"/>

  <xsl:key name='k1' match='x:*' use='@id'/>
  <xsl:key name='k1' match='y:*' use='@id'/>

  <x:vier id="ein"/>
  <x:drei id="zwo"/>
  <x:zwo id="drei"/>
  <x:ein id="vier"/>
  <y:vier id="ein"/>
  <y:drei id="zwo"/>
  <y:zwo id="drei"/>
  <y:ein id="vier"/>

  <xsl:template match="/">
    <result>
      <xsl:for-each select="document('')">
        <xsl:copy-of select="key('k1', 'drei')"/>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:x="http://spam.com/x" xmlns:y="http://spam.com/y"><x:zwo id="drei"/><y:zwo id="drei"/></result>"""
        )


def test_key_9():
    """included keys (test_key_9)"""
    _run_xml(
        source_xml = "<dummy/>",
        transform_uri = TRANSFORM_URI,
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com/x"
  xmlns:y="http://spam.com/y"
>

  <xsl:import href="test-key-import-2.xslt"/>

  <xsl:output method="xml"/>

  <xsl:key name='k1' match='x:*' use='@id'/>

  <x:vier id="ein"/>
  <x:drei id="zwo"/>
  <x:zwo id="drei"/>
  <x:ein id="vier"/>
  <y:vier id="ein"/>
  <y:drei id="zwo"/>
  <y:zwo id="drei"/>
  <y:ein id="vier"/>

  <xsl:template match="/">
    <result>
      <xsl:for-each select="document('')">
        <xsl:copy-of select="key('k1', 'drei')"/>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:stylesheet>
""",
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<result xmlns:x="http://spam.com/x" xmlns:y="http://spam.com/y"><x:zwo id="drei"/><y:zwo id="drei"/></result>"""
        )


def test_key_error_1():
    """keys using patterns of form `ns:*`"""
    try:
        _run_xml(
            source_xml = FILE_SOURCE_XML,
            source_uri = FILE_URI,
            transform_uri = TRANSFORM_URI,
            transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:x="http://spam.com"
>

  <xsl:import href="test-key-import-error.xslt"/>

  <x:grail id="ein"/>
  <x:grail id="zwo"/>
  <x:knicht id="drei"/>
  <x:knicht id="vier"/>

  <xsl:template match="/">
    Entries from key 1: <xsl:value-of select="count(key('k1', 'pa'))"/>
    <xsl:for-each select="document('')">
    Entries from key 2: <xsl:copy-of select="count(key('k2', 'drei'))"/>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
""",
            expected = None)
    except XsltError, err:
        assert err.code == XsltError.UNDEFINED_PREFIX
    else:
        raise AssertionError("should have failed!")

if __name__ == '__main__':
    raise SystemExit("use nosetests")
