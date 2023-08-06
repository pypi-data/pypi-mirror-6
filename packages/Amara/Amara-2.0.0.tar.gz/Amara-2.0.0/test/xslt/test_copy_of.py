########################################################################
# test/xslt/test_copy_of.py

import os
from xslt_support import _run_xml

module_dirname = os.path.dirname(__file__)

def test_copy_of_1():
    """copy element and contents"""
    _run_xml(
        source_xml = """<?xml version="1.0"?>
<foo>Embedded <html><a href='link'>go</a>.</html></foo>""",
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="html">
  <xsl:copy-of select="."/>
</xsl:template>
<xsl:template match="*">
  <xsl:apply-templates select="*"/>
</xsl:template>
</xsl:stylesheet>
""",
        expected = """<html><a href='link'>go</a>.</html>"""
        )

def test_copy_of_2():
    """copy external document"""
    _run_xml(
        source_xml = """<?xml version="1.0"?><dummy/>""",
        transform_uri = "file:" + module_dirname + "/test_copy_of.py",
        transform_xml = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
  <xsl:copy-of select="document('svgeg.svg')"/>
</xsl:template>

</xsl:stylesheet>
""",
    expected = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" height="10cm" width="10cm" contentStyleType="text/css" preserveAspectRatio="xMidYMid meet" zoomAndPan="magnify" viewBox="0 0 800 800" contentScriptType="text/ecmascript">
  <desc content="structured text">SVG Sample for SunWorld Article</desc>

  <style xml:space="preserve" type="text/css">
    .Lagos { fill: white; stroke: green; stroke-width: 30 }
    .ViaAppia { fill: none; stroke: black; stroke-width: 10 }
    .OrthoLogos { font-size: 32; font-family: helvetica }
  </style>

  <ellipse style="fill: brown; stroke: yellow; stroke-width: 10" rx="250" transform="translate(500 200)" ry="100"/>

  <polygon points="350,75 379,161 469,161 397,215 423,301 350,250 277,                    301 303,215 231,161 321,161" transform="translate(100 200) rotate(45)" class="Lagos"/>

  <text y="400" x="400" class="OrthoLogos">TO KALON</text>

  <path d="M500,600 C500,500 650,500 650,600                             S800,700 800,600" class="ViaAppia"/>
</svg>""")

# XXX This was in the older tests, but it doesn't seem to be used for anything. ??
if 0:
    expected_offline = """<?xml version="1.0" encoding="UTF-8"?>
<svg height="10cm" width="10cm" viewBox="0 0 800 800">
  <desc>SVG Sample for SunWorld Article</desc>

  <style type="text/css">
    .Lagos { fill: white; stroke: green; stroke-width: 30 }
    .ViaAppia { fill: none; stroke: black; stroke-width: 10 }
    .OrthoLogos { font-size: 32; font-family: helvetica }
  </style>

  <ellipse style="fill: brown; stroke: yellow; stroke-width: 10" rx="250" transform="translate(500 200)" ry="100"/>

  <polygon points="350,75 379,161 469,161 397,215 423,301 350,250 277,                    301 303,215 231,161 321,161" transform="translate(100 200) rotate(45)" class="Lagos"/>

  <text y="400" x="400" class="OrthoLogos">TO KALON</text>

  <path d="M500,600 C500,500 650,500 650,600                             S800,700 800,600" class="ViaAppia"/>
</svg>"""

if __name__ == '__main__':
    raise SystemExit("Use nosetests")
