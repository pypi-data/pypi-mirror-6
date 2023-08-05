# -*- coding: utf-8 -*-

from pptx.oxml import parse_xml_bytes

import pdb

from .unitutil import serialize_xml

nsmap = 'http://schemas.openxmlformats.org/presentationml/2006/main'

xml = '<p:sp xmlns:p="%s"><p:nvSpPr/></p:sp>' % nsmap
sp = parse_xml_bytes(xml)
pdb.set_trace()
msg = 'got:\n\n%s' % serialize_xml(sp)
