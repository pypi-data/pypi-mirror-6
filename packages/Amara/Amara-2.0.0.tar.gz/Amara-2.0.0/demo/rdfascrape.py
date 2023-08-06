"""
Scrape RDFa [1] [2] [3] from an XHTML Web page
Works on any HTML, though people who put what they call RDFa into tag soup are naughty and need their ears boxed

[1] http://en.wikipedia.org/wiki/RDFa
[2] http://www.alistapart.com/articles/introduction-to-rdfa/
[3] http://www.alistapart.com/articles/introduction-to-rdfa-ii/

Sample usage:

python rdfascrape.py data/xhtmlrdfa.html
python rdfascrape.py http://www.ivan-herman.net/foaf.html

Prints 4-tuples: (subject, predicate, object, data-type).  data-type may be None

For other examples see: http://esw.w3.org/topic/RDFa/Examples
"""

import sys
from itertools import chain

from amara.bindery import html
from amara.writers.struct import *
from amara.namespaces import *
from amara.lib.xmlstring import *
from amara.lib.iri import absolutize
#from amara.bindery.model import *

#Give Amara an example so it knows what structure to expect
#label_model = examplotron_model('data/xhtmlrdfa.html')

def absolutize(uriref, docuri):
    try:
        return absolutize(uriref, docuri)
    except:
        return uriref

def expand(data, context=None):
    if context:
        nss = context.xml_namespaces.copy()
        prefix, qname = splitqname(unicode(data))
        if prefix and prefix in nss:
            return nss[prefix] + qname
    return data

def handle_statement(elem, docuri):
    subject = elem.xml_select(u'ancestor::*/@about')
    subject = absolutize(subject[0].xml_value, docuri) if subject else docuri
    
    datatype = unicode(elem.xml_select(u'string(@datatype)'))
    if datatype: datatype = expand(datatype, elem)
    
    if elem.xml_select(u'@property') and elem.xml_select(u'@content'):
        return ( subject , expand(elem.property, elem), elem.content, datatype or None )
    elif elem.xml_select(u'@property'):
        return ( subject, expand(elem.property, elem), expand(unicode(elem)), datatype or None )
    elif elem.xml_select(u'@rel') and elem.xml_select(u'@resource'):
        return ( subject, expand(elem.rel, elem), elem.resource, datatype or None )
    elif elem.xml_select(u'@rel') and elem.xml_select(u'@href'):
        return ( subject, expand(elem.rel, elem), elem.href, datatype or None )
    elif elem.xml_select(u'@rel'):
        return ( subject, expand(elem.rel, elem), elem.href, datatype or None )
    else:
        return ()

def rdfascrape(source):
    from amara.lib import inputsource
    source = inputsource(source, None)
    doc = html.parse(source.stream)
    try:
        docuri = doc.html.head.base.href
    except:
        docuri = source.uri
 
    #https://github.com/zepheira/amara/issues/8
    #statement_elems = doc.xml_select(u'//*[@property|@resource|@rel]')
    statement_elems = chain(doc.xml_select(u'//*[@property]'), doc.xml_select(u'//*[@resource]'), doc.xml_select(u'//*[@rel]'))
    triples = ( handle_statement(elem, docuri) for elem in statement_elems )
    return triples

RDFA11_EXAMPLE = """\
<div vocab="http://schema.org/"
     typeof="Person">
  <span property="name">Manu Sporny</span>
  <img rel="image" src="manu.jpg" />

  <span property="jobTitle">CEO</span>

  <div rel="address">
    <span property="streetAddress">
     1700 Kraft Drive, Suite 2408
    </span>
    ...
  </div>

  <a rel="url"
     href="http://manu.sporny.org/">
       manu.sporny.org
  </a>
</div>
"""

if __name__ == '__main__':
    #doc = html.parse(DOCURI, model=label_model)
    for triple in rdfascrape(RDFA11_EXAMPLE):
        print triple

    for triple in rdfascrape(sys.argv[1]):
        print triple

