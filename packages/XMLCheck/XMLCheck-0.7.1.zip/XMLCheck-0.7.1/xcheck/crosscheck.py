#!/usr/bin/env python

"""xcheck cross check

Rules for checking integrity between elements of a node
"""

import xcheck
##print xcheck

submission_checker =xcheck.load_checker("""<xcheck name="submission">
<attributes>
<int name="id" />
</attributes>
<children>
    <text name="story"/>
    <selection name="storycode" values="a, b, c, d" />
    <selection name="marketcode" values="1, 2, 3, 4" />
    <datetime name="datesent" format="%Y-%m-%d"/>
    <datetime name="dateback" min_occurs="0" format="%Y-%m-%d" allow_none="True" />
    <selection name="status" values="inmail, reject, sold, withdrawn">
        <attributes>
            <selection name="grade" required="false"
                values="inmail, reject, sold, soldplus, marketdead, toolong" />
        </attributes>
    </selection>
    <selection name="method" values="mail, email, upload"/>
    <decimal name="cost"/>
    <text name="notes" min_occurs="0"/>
</children>
</xcheck>
""")

##print submission_checker

test_sub = """<submission id="1">
    <story>Uncle Charlie Goes Fishing</story>
    <storycode>a</storycode>
    <marketcode>1</marketcode>
    <datesent>2013-06-04</datesent>
    <status grade="reject">reject</status>
    <method>email</method>
    <cost>1.72</cost>
    <notes />
  </submission>"""

##print submission_checker(test_sub)


test_node = xcheck.ET.fromstring(test_sub)

value_keys = ('status', 'grade')
value_pairs = (
    ('inmail', ('inmail',)),
    ('reject', ('reject',)),
    ('sold', ('sold', 'soldplus')),
    ('withdrawn', ('marketdead', 'toolong'))
    )

values_to_check = []
for key in value_keys:
    name, att = submission_checker.path_to(key)
    if att is None:
        name = name
    else:
        name =  "%s[@%s]" % (name, att)

    child = test_node.find(name)


##    print key, child.get(att) if att else child.text
    values_to_check.append(child.get(att) if att else child.text)

key_dict = dict(zip(value_keys, values_to_check))
print key_dict
value_dict = dict(value_pairs)
print values_to_check[1] in value_dict[values_to_check[0]]
