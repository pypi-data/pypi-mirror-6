<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!--
http://www.w3.org/TR/1999/REC-xml-names-19990114/#NT-NCName

[4] 	NCName	 	::=	(Letter | '_') (NCNameChar)*	 /*	An XML Name, minus the ":" */
[5] 	NCNameChar	::=	Letter | Digit | '.' | '-' | '_' | CombiningChar | Extender
-->
	<xsl:template name="makeNCName">
		<xsl:param name="str"/>
		<xsl:param name="pos" select="1"/>

		<xsl:variable name="tables" select="document('tables.xml')"/>
		<xsl:variable name="BaseChar" select="$tables/root/BaseChar/text()"/>
		<xsl:variable name="Ideographic" select="$tables/root/Ideographic/text()"/>
		<xsl:variable name="CombiningChar" select="$tables/root/CombiningChar/text()"/>
		<xsl:variable name="Extender" select="$tables/root/Extender/text()"/>
		<xsl:variable name="Digit" select="$tables/root/Digit/text()"/>
		<xsl:variable name="Letter" select="concat($BaseChar, $Ideographic)"/>
		<xsl:variable name="FirstChar" select="concat($Letter, '_')"/>
		<xsl:variable name="NCNameChar" select="concat($Letter, $Digit, '.', '-', '_', $CombiningChar, $Extender)"/>

		<xsl:variable name="ch" select="substring($str, $pos, 1)"/>

		<xsl:if test="$pos &lt;= string-length($str)">
			<xsl:choose>
				<xsl:when test="$pos = 1 and not(contains($FirstChar, $ch)) or $pos &gt; 1 and not(contains($NCNameChar, $ch))">
					<xsl:value-of select="'_'"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="$ch"/>
				</xsl:otherwise>
			</xsl:choose>

			<xsl:call-template name="makeNCName">
				<xsl:with-param name="str" select="$str"/>
				<xsl:with-param name="pos" select="$pos + 1"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>

	<xsl:template match="/">
		<root>
			<xsl:for-each select="/root/nc/text()">
				<xsl:variable name="nc">
					<xsl:call-template name="makeNCName">
						<xsl:with-param name="str" select="."/>
					</xsl:call-template>
				</xsl:variable>
				<xsl:element name="{$nc}"/>
			</xsl:for-each>
		</root>
	</xsl:template>
</xsl:stylesheet><!-- Stylus Studio meta-information - (c) 2004-2009. Progress Software Corporation. All rights reserved.

<metaInformation>
	<scenarios>
		<scenario default="yes" name="Scenario1" userelativepaths="yes" externalpreview="no" url="ncnames.xml" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth="" profilelength="" urlprofilexml=""
		          commandline="" additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal" customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
	</scenarios>
	<MapperMetaTag>
		<MapperInfo srcSchemaPathIsRelative="yes" srcSchemaInterpretAsXML="no" destSchemaPath="" destSchemaRoot="" destSchemaPathIsRelative="yes" destSchemaInterpretAsXML="no"/>
		<MapperBlockPosition></MapperBlockPosition>
		<TemplateContext></TemplateContext>
		<MapperFilter side="source"></MapperFilter>
	</MapperMetaTag>
</metaInformation>
-->
