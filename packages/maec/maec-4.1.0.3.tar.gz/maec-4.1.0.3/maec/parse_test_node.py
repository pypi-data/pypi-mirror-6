import sys
from lxml import etree


parser = etree.ETCompatXMLParser(huge_tree=True)
tree = etree.parse(sys.argv[1], parser=parser)
root = tree.getroot()
print root.tag