import collections
import cybox
import sets
from cybox.core import Object
from cybox.common.properties import BaseProperty

# Dictionary of all object types (as lists)
objects_dict = {}

# Returns the value contained in a TypedField or its nested members, if applicable
def get_typedfield_values(val, name, values):
    # If it's a BaseProperty instance, then we're done. Return it.
    if isinstance(val, BaseProperty):
        values.add(name + ":" + str(val))
    # If it's a list, then we need to iterate through each of its members
    elif isinstance(val, collections.MutableSequence):
        for list_item in val:
            for list_item_property in list_item._get_vars():
                get_typedfield_values(getattr(list_item, str(list_item_property)), name + "/" + str(list_item_property), values)
    # If it's a cybox.Entity, then we need to iterate through its properties
    elif isinstance(val, cybox.Entity):
        for item_property in val._get_vars():
            get_typedfield_values(getattr(val, str(item_property)), name + "/" + str(item_property), values) 

# Get the values specified for an object's properties as a set
def get_object_values(obj):
    values = set()
    for typed_field in obj.properties._get_vars():
        # Make sure the typed field is comparable
        if typed_field.comparable:
            val = getattr(obj.properties, str(typed_field))
            if val is not None:
                get_typedfield_values(val, str(typed_field), values)
    return values

# Find a matching object, if it exists
def find_matching_object(obj):
    object_values = get_object_values(obj)
    xsi_type = obj.properties._XSI_TYPE 
    if xsi_type and xsi_type in objects_dict:
        types_dict = objects_dict[xsi_type]
        # See if we already have an identical object in the dictionary
        for obj_id, obj_values in types_dict.items():
            if obj_values == object_values:
                # If so, return its ID for use in the IDREF
                return obj_id
        # If not, add it to the dictionary
        types_dict[obj.id_] = object_values
    elif xsi_type and xsi_type not in objects_dict:
        types_dict = {obj.id_:object_values}
        objects_dict[xsi_type] = types_dict
    return None

obj_dict = {'id':'maec-test-obj-1', 'properties': {'xsi:type':'FileObjectType', 'file_path':'c:\something', 'file_name':'xyz.dll',
                           'hashes': [{'type':'sha1', 'simple_hash_value':'ffff'},
                                      {'type':'md5', 'simple_hash_value':'asdasd'}]}}
obj_dict_2 = {'id':'maec-test-obj-2', 'properties': {'xsi:type':'FileObjectType', 'file_name':'xyz.dll', 'file_path':'c:\something',
                           'hashes': [{'type':'md5', 'simple_hash_value':'asdasd'},
                                      {'type':'sha1', 'simple_hash_value':'ffff'}]}}
obj_dict_3 = {'id':'maec-test-obj-3', 'properties': {'xsi:type':'FileObjectType', 'file_name':'xyz.dll', 'file_path':'c:\something',
                           'size_in_bytes': '123456', 'hashes': [{'type':'md5', 'simple_hash_value':'asdasd'},
                                                                 {'type':'sha1', 'simple_hash_value':'ffff'}]}}


#obj_dict_3 = {'id':'maec-test-obj-3', 'properties': {'xsi:type':'SystemObjectType', 'os': {'bitness':'64', 'build_number':'123456'}}}
#obj_dict_4 = {'id':'maec-test-obj-4', 'properties': {'xsi:type':'SystemObjectType', 'os': {'bitness':'64', 'build_number':'123456'}}}

obj1 = Object.from_dict(obj_dict)
obj2 = Object.from_dict(obj_dict_2)
obj3 = Object.from_dict(obj_dict_3)

set1 = get_object_values(obj1)
set2 = get_object_values(obj2)
set3 = get_object_values(obj3)


print set1
print set2
print set3

print obj_dict == obj_dict_2
print obj_dict == obj_dict_3
print set1 == set2
print set1 == set3