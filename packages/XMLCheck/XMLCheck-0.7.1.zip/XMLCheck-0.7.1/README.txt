XCheck

XMLChecker objects that can validate text, xml-formatted text,
or an elementtree.ElementTree node. XCheck objects can also
return checked data in a normalized form (BoolCheck, for example,
returns Boolean values, IntCheck returns an integer)

XCheck objects can manipulate Element objects.

You can define an XCheck object using an xml-formatted text:

checker_text = """<xcheck contact>
<children>
<text name="Name" />
<email name="Email" max_occurs=4 />
</children>
</xcheck>"""

checker = xcheck.load_checker(checker_text)

checker("<contact><name>Josh</name><email>me@work.net</email></contact>") 
# returns True



