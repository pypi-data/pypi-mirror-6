import maec
import sys
from maec.bundle.bundle import ObjectHistory

maec_objects = maec.parse_xml_instance(sys.argv[1])
maec_package = maec_objects['api']

for malware_subject in maec_package.malware_subjects:
    findings_bundles = malware_subject.findings_bundles
    for findings_bundle in findings_bundles.bundles:
        if not findings_bundle.content_type or findings_bundle.content_type == 'dynamic analysis tool output':
            object_history = ObjectHistory()
            object_history.build(findings_bundle)
            print 'Object Type, API Call(s)'
            for history_entry in object_history.entries:
                object_dict = history_entry.object.properties.to_dict()
                object_xsi_type = object_dict['xsi:type']
                object_dict.pop('xsi:type')
                object_value_string = ''
                action_name_string = ''
                for action_name in history_entry.get_action_names():
                    action_name_string += action_name + '|'
                print object_xsi_type + ',' + action_name_string[:len(action_name_string)-1]