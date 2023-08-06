<?xml version='1.0'?>
<!--
Namespace tracer from Pawson, David <DPawson@rnib.org.uk> on 10 March 
2000, with a version using the namespace axis from David Carlisle.
-->

<xsl:stylesheet 
   version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:ns-test="http://ns1.com"
   xmlns:ns1="http://ns1.com"
   xmlns:ns2="http://ns2.com"
   xmlns:long-namespace="http://ns3.com"
   exclude-result-prefixes="ns1 ns2 long-namespace"
>

<xsl:output method="xml" indent="yes"/>

<xsl:template match="*">
  <!--<xsl:message><xsl:value-of select="name(.)"/></xsl:message>-->
  <tag>Namespace:<xsl:choose><xsl:when test="namespace-uri(.)"><xsl:value-of select="namespace-uri(.)"/>
      </xsl:when>
      <xsl:otherwise> Null namespace</xsl:otherwise>
    </xsl:choose>
  </tag>
  <tag>name: <xsl:value-of select="name(.)"/></tag>
  <tag>local-name: <xsl:value-of select="local-name(.)"/></tag>
  <tag>Content: <xsl:value-of select="text()"/></tag>
  <xsl:if test="./*"><xsl:apply-templates/></xsl:if>
</xsl:template>

</xsl:stylesheet>
