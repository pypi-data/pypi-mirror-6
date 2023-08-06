import sys
import maec

bindings_obj = maec.parse_xml_instance(sys.argv[1])
if bindings_obj[0] : print "package"
if bindings_obj[1] : print "bundle"