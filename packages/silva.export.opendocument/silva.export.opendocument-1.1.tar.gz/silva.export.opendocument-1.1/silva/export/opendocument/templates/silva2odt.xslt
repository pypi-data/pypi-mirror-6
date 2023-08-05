<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content silva-extra"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" 
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" 
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" 
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" 
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" 
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" 
  xmlns:xlink="http://www.w3.org/1999/xlink" 
  xmlns:dc="http://purl.org/dc/elements/1.1/" 
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" 
  xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" 
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" 
  xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" 
  xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" 
  xmlns:math="http://www.w3.org/1998/Math/MathML" 
  xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" 
  xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" 
  xmlns:ooo="http://openoffice.org/2004/office" 
  xmlns:ooow="http://openoffice.org/2004/writer" 
  xmlns:oooc="http://openoffice.org/2004/calc" 
  xmlns:dom="http://www.w3.org/2001/xml-events" 
  xmlns:xforms="http://www.w3.org/2002/xforms" 
  xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
  
  xmlns:silva="http://infrae.com/ns/silva"
  xmlns:doc="http://infrae.com/ns/silva_document" 
  xmlns:silva-content="http://infrae.com/namespaces/metadata/silva"
  xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra"
  
  version="1.0">

  <!-- Base document -->
  <xsl:template match="/">
    <office:document-content 
       office:version="1.0">

      <office:scripts/>
      <office:font-face-decls>
        <style:font-face style:name="starbats" 
                         svg:font-family="starbats" 
                         style:font-charset="x-symbol"/>
        <style:font-face style:name="Bitstream Vera Serif" 
                         svg:font-family="&apos;Bitstream Vera Serif&apos;" 
                         style:font-family-generic="roman" 
                         style:font-pitch="variable"/>
        <style:font-face style:name="Arial" 
                         svg:font-family="Arial" 
                         style:font-family-generic="swiss" 
                         style:font-pitch="variable"/>
        <style:font-face style:name="Andale Sans UI" 
                         svg:font-family="&apos;Andale Sans UI&apos;" 
                         style:font-family-generic="system" 
                         style:font-pitch="variable"/>
        <style:font-face style:name="Arial1" 
                         svg:font-family="Arial" 
                         style:font-family-generic="system" 
                         style:font-pitch="variable"/>
        <style:font-face style:name="Bitstream Vera Sans" 
                         svg:font-family="&apos;Bitstream Vera Sans&apos;" 
                         style:font-family-generic="system" 
                         style:font-pitch="variable"/>
      </office:font-face-decls>
      <office:automatic-styles>
        <style:style style:name="P1" 
                     style:family="paragraph" 
                     style:parent-style-name="Standard" 
                     style:list-style-name="L1"/>
        <style:style style:name="P2" 
                     style:family="paragraph" 
                     style:parent-style-name="Standard" 
                     style:list-style-name="L1"/>
        <style:style style:name="P3" 
                     style:family="paragraph" 
                     style:parent-style-name="Standard" 
                     style:list-style-name="L1"/>
        <style:style style:name="T1" 
                     style:family="text">
          <style:text-properties fo:font-weight="bold" 
                                 style:font-weight-asian="bold" 
                                 style:font-weight-complex="bold"/>
        </style:style>
        <style:style style:name="T2" 
                     style:family="text">
          <style:text-properties 
             fo:font-style="italic" 
             style:font-style-asian="italic" 
             style:font-style-complex="italic"/>
        </style:style>
        <style:style style:name="T3" 
                     style:family="text">
          <style:text-properties fo:font-style="normal" 
                                 style:font-style-asian="normal" 
                                 style:font-style-complex="normal"/>
        </style:style>
        <style:style style:name="T4" 
                     style:family="text">
          <style:text-properties style:text-underline-style="solid" 
                                 style:text-underline-width="auto" 
                                 style:text-underline-color="font-color"/>
        </style:style>
        <style:style style:name="fr1" 
                     style:family="graphic" 
                     style:parent-style-name="Graphics">
          <style:graphic-properties style:mirror="none" 
                                    fo:clip="rect(0cm 0cm 0cm 0cm)" 
                                    draw:luminance="0%" 
                                    draw:contrast="0%" 
                                    draw:red="0%" 
                                    draw:green="0%" 
                                    draw:blue="0%" 
                                    draw:gamma="100%" 
                                    draw:color-inversion="false" 
                                    draw:image-opacity="100%" 
                                    draw:color-mode="standard"/>
        </style:style>
        <text:list-style style:name="L1">
          <text:list-level-style-bullet text:level="1" 
                                        text:style-name="Bullet_20_Symbols" 
                                        style:num-suffix="." 
                                        text:bullet-char="•">
            <style:list-level-properties text:space-before="0.635cm" 
                                         text:min-label-width="0.635cm"/>
            <style:text-properties style:font-name="starbats"/>
          </text:list-level-style-bullet>
          <text:list-level-style-bullet text:level="2" 
                                        text:style-name="Bullet_20_Symbols" 
                                        style:num-suffix="." 
                                        text:bullet-char="•">
            <style:list-level-properties text:space-before="1.27cm" 
                                         text:min-label-width="0.635cm"/>
            <style:text-properties style:font-name="starbats"/>
          </text:list-level-style-bullet>
          <text:list-level-style-bullet text:level="3" 
                                        text:style-name="Bullet_20_Symbols" 
                                        style:num-suffix="." 
                                        text:bullet-char="•">
            <style:list-level-properties text:space-before="1.905cm" 
                                         text:min-label-width="0.635cm"/>
            <style:text-properties style:font-name="starbats"/>
          </text:list-level-style-bullet>
          <text:list-level-style-bullet text:level="4" 
                                        text:style-name="Bullet_20_Symbols" 
                                        style:num-suffix="." 
                                        text:bullet-char="•">
            <style:list-level-properties text:space-before="2.54cm" 
                                         text:min-label-width="0.635cm"/>
            <style:text-properties style:font-name="starbats"/>
          </text:list-level-style-bullet>
          <!-- Number for sample -->
          <text:list-level-style-number text:level="5" 
                                        style:num-suffix="." 
                                        style:num-format="1">
            <style:list-level-properties text:space-before="3.175cm" 
                                         text:min-label-width="0.635cm"/>
          </text:list-level-style-number>
        </text:list-style>


        <!-- Style for tables -->


        <xsl:for-each select="//doc:table">
          <style:style style:name="{concat('table_', generate-id())}"
                       style:family="table">
            <style:table-properties style:width="17.5cm" />
          </style:style>
        </xsl:for-each>
        <xsl:for-each select="//doc:col">
          <style:style style:name="{concat('col_', generate-id())}"
                       style:family="table-column">
            <style:table-column-properties> 
              <xsl:variable name="width"
                            select="number(substring-before(@width, '%'))" />
               <xsl:attribute name="column-width"
                              namespace="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
                 <xsl:value-of select="concat(string(0.175 * $width), 'cm')" />
               </xsl:attribute>
               <xsl:attribute name="rel-column-width"
                              namespace="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
                 <xsl:value-of select="concat($width, '*')" />
               </xsl:attribute>
            </style:table-column-properties>
          </style:style>
        </xsl:for-each>

      </office:automatic-styles>
      <office:body>
        <office:text>
          <xsl:apply-templates />
        </office:text>
      </office:body>
    </office:document-content>
  </xsl:template>

  <!-- Remove workflow information -->
  <xsl:template match="silva:workflow" />

  <!-- Metadata -->
  <!-- We keep only document titles -->
  <xsl:template match="silva:document//silva-content:maintitle">
    <text:h text:style-name="Heading"
            text:outline-level="1">
      <xsl:value-of select="." />
    </text:h>
  </xsl:template>
  <xsl:template match="silva:metadata/silva:set/*" />

  <!-- We don't want theses content types -->
  <xsl:template match="silva:image_asset" />
  <xsl:template match="silva:auto_toc" />
  <xsl:template match="silva:unknown_content" />


  
  <xsl:template match="silva:publication">
    <text:h text:style-name="Heading">
      <xsl:value-of select="silva:metadata/silva:set[@id='silva-content']/silva-content:maintitle" />
    </text:h>
    <text:table-of-content>
      <text:table-of-content-source text:outline-level="2"
                                    text:index-scope="document" />
    </text:table-of-content>
    <xsl:apply-templates />
  </xsl:template>

  <!-- Text style -->
  <xsl:template match="doc:heading[@type='normal']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:h text:style-name="Heading_20_4" 
                text:outline-level="4">
          <xsl:apply-templates />
        </text:h>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="doc:heading[@type='sub']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:h text:style-name="Heading_20_5" 
                text:outline-level="5">
          <xsl:apply-templates />
        </text:h>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subsub']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:h text:style-name="Heading_20_6" 
                text:outline-level="6">
          <xsl:apply-templates />
        </text:h>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='paragraph']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:h text:style-name="Heading_20_7" 
                text:outline-level="7">
          <xsl:apply-templates />
        </text:h>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subparagraph']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:h text:style-name="Heading_20_8" 
                text:outline-level="8">
          <xsl:apply-templates />
        </text:h>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>  

  <xsl:template match="doc:p">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:p text:style-name="Standard">
          <xsl:apply-templates />
        </text:p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:pre">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <text:p text:style-name="Pre">
          <xsl:apply-templates />
        </text:p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:p[@type='annotation']" />
  
  <xsl:template match="doc:br">
    <text:line-break/>
  </xsl:template>

  <!-- Text style -->
  <xsl:template match="doc:strong">
    <text:span text:style-name="T1">
      <xsl:apply-templates/>
    </text:span>
  </xsl:template>
  
  <xsl:template match="doc:em">
    <text:span text:style-name="T2">
      <xsl:apply-templates />
    </text:span>
  </xsl:template>
  
  <xsl:template match="doc:underline">
    <text:span text:style-name="T4">
      <xsl:apply-templates />
    </text:span>
  </xsl:template>
  
  <xsl:template match="doc:index">
    <text:bookmark text:name="{@name}"/>
  </xsl:template>
  
  <!-- List -->
  <xsl:template match="doc:list | doc:nlist">
    <text:list text:style-name="L1">
      <xsl:for-each select="doc:li">
        <text:list-item>
          <xsl:choose>
            <xsl:when test="text()[normalize-space(.)]">
              <text:p text:style-name="Standard">
                <xsl:value-of select="." />
              </text:p>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates />
            </xsl:otherwise>
          </xsl:choose>
        </text:list-item>
      </xsl:for-each>
    </text:list>
  </xsl:template>

  <!-- Link -->
  <xsl:template match="doc:link">
    <text:a xlink:href="{@rewritten_url}"
            office:target-frame-name="{@target}"
            office:name="{@title}">
      <xsl:value-of select="." />
    </text:a>
  </xsl:template>

  <!-- Image -->
  <xsl:template match="doc:image">
    <text:p>
      <xsl:variable name="width"
                    select="number(@width) div 38.0" />
      <draw:frame draw:style-name="fr1"
                  draw:name="{concat('cap_img_', generate-id())}"
                  svg:width="{$width}cm"
                  text:text-anchor-type="as-char"
                  draw:z-indez="1">
        <draw:text-box>
          <text:p text:style-name="Illustration">
            <draw:frame draw:style-name="fr1"
                        draw:name="{concat('img_', generate-id())}"
                        svg:height="{number(@height) div 38.0}cm"
                        svg:width="{$width}cm"
                        text:text-anchor-type="paragraph"
                        draw:z-index="2">
              <draw:image xlink:href="Pictures/{@path}"
                          xlink:type="simple"
                          xlink:show="embed"
                          xlink:actuate="onLoad" />
            </draw:frame>
            <xsl:value-of select="following-sibling::doc:p[@type='annotation']" />
          </text:p>
        </draw:text-box>
      </draw:frame>
    </text:p>
  </xsl:template>

  <!-- Table -->
  <xsl:template match="doc:table">
    <table:table table:name="{generate-id()}"
                 table:style-name="{concat('table_', generate-id())}">
      <table:table-columns>
        <xsl:for-each select="doc:col">
          <table:table-column table:style-name="{concat('col_', generate-id())}" />
        </xsl:for-each>
      </table:table-columns>
      <table:table-rows>
        <xsl:for-each select="doc:row">
          <table:table-row>
            <xsl:for-each select="doc:field">
              <table:table-cell>
                <xsl:apply-templates />
              </table:table-cell>
            </xsl:for-each>
          </table:table-row>
        </xsl:for-each>
      </table:table-rows>
    </table:table>
  </xsl:template>
  
</xsl:stylesheet>
