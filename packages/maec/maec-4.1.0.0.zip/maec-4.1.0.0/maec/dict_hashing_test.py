obj_dict = {'properties': {'xsi:type':'FileObjectType', 'file_name':'xyz.dll', 'file_path':'c:\something',
                           'hashes': [{'type':'md5', 'simple_hash_value':'ffff'},
                                       {'type':'sha1', 'simple_hash_value':'asdasd'}]}}

obj_dict2 = {'properties': {'xsi:type':'FileObjectType', 'file_name':'xyz.dll', 'file_path':'c:\something',
                           'hashes': [{'type':'sha1', 'simple_hash_value':'asdasd'},
                                       {'type':'md5', 'simple_hash_value':'ffff'}]}}


embedded_dict = {}
embedded_dict['obj_dict'] = obj_dict
if obj_dict in embedded_dict.values():
    print "Found"
