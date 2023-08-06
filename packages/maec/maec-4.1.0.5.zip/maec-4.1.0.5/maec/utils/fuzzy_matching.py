# MAEC String Distance Matching Utility
# v0.10 BETA

import maec
import cybox
import difflib
import sys
import collections
import itertools
from cybox.common.properties import BaseProperty

try:
    from fuzzywuzzy import fuzz
except ImportError:
    print "Error importing required fuzzywuzzy module (https://github.com/seatgeek/fuzzywuzzy). Exiting"
    sys.exit(0)

# Returns the value contained in a TypedField or its nested members, if applicable
def get_typedfield_values(val, values):
    # If it's a BaseProperty instance, then we're done. Return it.
    if isinstance(val, BaseProperty):
        values.append(str(val))
    # If it's a list, then we need to iterate through each of its members
    elif isinstance(val, collections.MutableSequence):
        for list_item in val:
            for list_item_property in list_item._get_vars():
                get_typedfield_values(getattr(list_item, str(list_item_property)), values)
    # If it's a cybox.Entity, then we need to iterate through its properties
    elif isinstance(val, cybox.Entity):
        for item_property in val._get_vars():
            get_typedfield_values(getattr(val, str(item_property)), values) 

# Get the values specified for an object's properties as a set
def get_object_values(obj):
    values = []
    if obj.properties:
        for typed_field in obj.properties._get_vars():
            # Make sure the typed field is comparable
            if typed_field.comparable:
                val = getattr(obj.properties, str(typed_field))
                if val is not None:
                    get_typedfield_values(val, values)
        return values

# Prune the Object Properties for more coherent matches
def prune_object_properties(property_list, min_length = 4):
    for property in list(property_list):
        # Length Check
        if len(property) < min_length:
            property_list.remove(property)
        # Other Checks
        if "HKEY" in property:
            property_list.remove(property)
    return property_list

# Test the various fuzzy matching ratios
def threshold_test(ratio_tuple, threshold = 60):
    # Do the basic threshold test
    if ratio_tuple[0] < threshold:
        return False
    # Test to make sure at least two ratios return a complete (100) match
    if ratio_tuple.count(100) > 1:
        return True
    else:
        return False

# Perform the fuzzy matching comparison between two Object properties
def perform_property_comparison(property_tuple):
    first_property = property_tuple[0].lower()
    second_property = property_tuple[1].lower()
    ratio = fuzz.ratio(first_property, second_property)
    sort_ratio = fuzz.token_sort_ratio(first_property, second_property)
    partial_ratio = fuzz.partial_ratio(first_property, second_property)
    set_ratio = fuzz.token_set_ratio(first_property, second_property)
    return (ratio, sort_ratio, partial_ratio, set_ratio)

# Find the cartesian product between two lists
def get_cartesian_product(first_list, second_list):
    combined_list = [first_list, second_list]
    return itertools.product(*combined_list)

# Perform the object property fuzzy comparison between different types of objects
def perform_dissimilar_comparison(binned_objects):
    properties_combinations = itertools.combinations(binned_objects, 2)
    for tuple in properties_combinations:
        first_type = tuple[0]
        second_type = tuple[1]
        first_values = binned_objects[first_type]
        second_values = binned_objects[second_type]
        list_product = get_cartesian_product(first_values, second_values)
        for list_product_tuple in list_product:
            first_object_values = prune_object_properties(get_object_values(list_product_tuple[0]))
            second_object_values = prune_object_properties(get_object_values(list_product_tuple[1]))
            properties_tuple = get_cartesian_product(first_object_values, second_object_values)
            results_dict = {}
            matching_properties = []
            for property_tuple in properties_tuple:
                # Assumes one match per object->object pair (valid?)
                if threshold_test(perform_property_comparison(property_tuple)):
                    matching_properties.append(property_tuple[0])
                    matching_properties.append(property_tuple[1])
                    break

            if matching_properties:
                comparison_results.append([(list_product_tuple[0], matching_properties[0]), (list_product_tuple[1], matching_properties[1])])

# Build up a multi-object (N>2) relationship chain
def build_chain(chain_built, result_tuple, comparison_results):
    updated_matching_list = []
    for results_tuple in result_tuple[0] + result_tuple[1]:
        if results_tuple not in updated_matching_list:
            updated_matching_list.append(results_tuple)
    if result_tuple[0] in comparison_results:
        comparison_results = [x for x in comparison_results if x != result_tuple[0]]
    if result_tuple[1] in comparison_results:
        comparison_results = [x for x in comparison_results if x != result_tuple[1]]
    if updated_matching_list not in comparison_results:
        comparison_results.append(updated_matching_list)
        chain_built = True
    return (chain_built, comparison_results)

# Find and build any multi-object (N>2) relationship chains
def find_chains(comparison_results):
    chain_built = True
    # Loop through until no more chains are built
    while chain_built == True:
        chain_built = False
        result_combinations = list(itertools.combinations(comparison_results, 2))
        for result_tuple in result_combinations:
            if chain_built:
                break
            # TBD - clean this up?
            first_values = []
            second_values = []
            for i in range(0, len(result_tuple[0])):
                first_values.append(result_tuple[0][i][1])
            for i in range(0, len(result_tuple[1])):
                second_values.append(result_tuple[1][i][1])
            list_product = list(get_cartesian_product(first_values, second_values))
            num_matches = 0
            for values_tuple in list_product:
                if threshold_test(perform_property_comparison(values_tuple)):
                    num_matches += 1
            # Only build the chain if ALL matches succeed
            if num_matches == len(list_product):
                chain_built, comparison_results = build_chain(chain_built, result_tuple, comparison_results)

    return comparison_results

# Print out the resulting matches
def print_matches(comparison_results):
    for comparison_result in comparison_results:
        print "**** MATCHING SET ******************************************"
        for object_tuple in comparison_result:
            print object_tuple[0].properties._XSI_TYPE
            print get_object_values(object_tuple[0])
            print "--------------------------------------------"
        print "************************************************************"

objects = maec.parse_xml_instance(sys.argv[1], check_version=False)
api_obj = objects['api']
binned_objects = {}
# List of comparison results as lists
comparison_results = []

# Get all of the properties of the objects in the document
for malware_subject in api_obj.malware_subjects:
    if malware_subject.findings_bundles.bundles:
        for bundle in malware_subject.findings_bundles.bundles:
            binned_objects = bundle.get_all_objects(include_actions=True, bin=True)

# Perform the initial comparison between non-identical objects
perform_dissimilar_comparison(binned_objects)
# Expand the initial results to find any matching "chains"
comparison_results = find_chains(comparison_results)
# Print the resulting matches
print_matches(comparison_results)