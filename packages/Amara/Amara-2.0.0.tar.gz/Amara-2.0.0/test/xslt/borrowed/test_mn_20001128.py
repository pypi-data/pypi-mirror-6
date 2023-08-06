########################################################################
# test/xslt/mn_20001128.py
# Miloslav Nic <nicmila@idoox.com> has a cool element/attribute stats tool

import os

from amara.test.xslt.xslt_support import _run_text

module_dir = os.path.dirname(__file__)
SLIDES4SVG_XML = os.path.join(module_dir, "resources", "slides4svg.xml")

def test_xslt_debug_1_mn_20001128():
    transform = """<xsl:stylesheet xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
version = "1.0" > 
   <xsl:output method="text"/>

   <xsl:key name="elements" match="*" use="name()"/>
   <xsl:key name="attributes" match="@*"
use="concat(name(parent::*),':::',name())"/>
<xsl:key name="allSameAttributes" match="@*" use="name(parent::*)"/>

   <xsl:template match = "*" > 
     <xsl:if test="generate-id() = generate-id(key('elements',name()))">
       <xsl:text>&#xA;</xsl:text>
       <xsl:value-of select="name()"/>
       <xsl:apply-templates select="key('allSameAttributes',name())">
         <xsl:sort select='name()'/>
       </xsl:apply-templates>
     </xsl:if>
     <xsl:apply-templates/>
   </xsl:template> 

   <xsl:template match="@*">
     <xsl:if test="position()=1">
       <xsl:text> [ </xsl:text>
     </xsl:if>

     <xsl:if test="generate-id() =
generate-id(key('attributes',concat(name(parent::*),':::',name())))">
       <xsl:value-of select="name()"/>
       <xsl:text> </xsl:text>
     </xsl:if>

     <xsl:if test="position()=last()">
       <xsl:text> ] </xsl:text>
     </xsl:if>
   </xsl:template>

   <xsl:template match="text()"/>
 </xsl:stylesheet>"""
    expected = """
slideshow
title
metadata
speaker
jobTitle
organization
presentationDate
presentationLocation
occasion
slideset
slide [ id  ] 
item
speakerNote
emphasis [ role  ] 
heading
bulletlist
preformatted
graphic [ file height width  ] 
link [ href  ] 
para"""
    _run_text(
        source_xml = SLIDES4SVG_XML,
        transform_xml = transform,
        expected = expected,
        )

def test_xslt_debug_2_mn_20001128():
    transform = """<xsl:stylesheet xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
 version =
 "1.0" > 
    <xsl:output method="text"/>

    <xsl:key name="elements" match="*" use="name()"/>
    <xsl:key name="attributes" match="@*"
 use="concat(name(parent::*),':::',name())"/>
    <xsl:key name="allSameAttributes" match="@*" use="name(parent::*)"/>

    <xsl:template match="/">
      <xsl:apply-templates select="//*">
        <xsl:sort select="name()"/>
      </xsl:apply-templates>
    </xsl:template>

    <xsl:template match = "*" >
      <xsl:if test="generate-id() = generate-id(key('elements',name()))">
        <xsl:text>&#xA;</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:apply-templates select="key('allSameAttributes',name())">
          <xsl:sort select="name()"/>
        </xsl:apply-templates>
      </xsl:if>
    </xsl:template> 

    <xsl:template match="@*">
      <xsl:if test="generate-id() =
 generate-id(key('attributes',concat(name(parent::*),':::',name())))">
        <xsl:text>&#xA;     </xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>: </xsl:text>
        <xsl:apply-templates
 select="key('attributes',concat(name(parent::*),':::',name()))"
 mode="values">
          <xsl:sort/>
        </xsl:apply-templates>
      </xsl:if>
    </xsl:template>

    <xsl:template match="@*" mode="values">
      <xsl:variable name="sameValues" 
        select="key('attributes',concat(name(parent::*),':::',name()))[.
 = current()]" />

        <xsl:if test="generate-id() = generate-id($sameValues)">
          <xsl:value-of select="."/>
          <xsl:text>(</xsl:text>
          <xsl:value-of select="count($sameValues)"/>
          <xsl:text>) </xsl:text>
        </xsl:if>

    </xsl:template>

    <xsl:template match="text()"/>
  </xsl:stylesheet>"""

    expected = """
bulletlist
emphasis
     role: note(3) 
graphic
     file: sample.svg(1) 
     height: 800(1) 
     width: 800(1) 
heading
item
jobTitle
link
     href: http://dmoz.org/Computers/Data_Formats/Graphics/Vector/SVG/(1) http://www.sun.com/xml/developers/svg-slidetoolkit/(1) http://www.w3.org/Graphics/SVG(1) 
metadata
occasion
organization
para
preformatted
presentationDate
presentationLocation
slide
     id: I.1(1) II.1(1) II.2(1) II.3(1) III.1(1) III.2(1) 
slideset
slideshow
speaker
speakerNote
title"""

    _run_text(
        source_xml = SLIDES4SVG_XML,
        transform_xml = transform,
        expected = expected,
        )        


if __name__ == '__main__':
    raise SystemExit("Use nosetests")
