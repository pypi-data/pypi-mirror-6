from maec.package.action_equivalence import ActionEquivalence

test_dict = {"id" : "123456", "action_reference" : [{"action_id" : "123456" }, {"action_id" : "25678"}]}
actioneq = ActionEquivalence.from_dict(test_dict)
print actioneq.to_xml()