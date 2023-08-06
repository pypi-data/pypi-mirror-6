#MAEC Action Equivalence Class

#Copyright (c) 2014, The MITRE Corporation
#All rights reserved

#Compatible with MAEC v4.1
#Last updated 02/18/2014

import maec
import maec.bindings.maec_package as package_binding
from cybox.core import ActionReference


class ActionEquivalence(maec.Entity):
     _binding = package_binding
     _binding_class = package_binding.ActionEquivalenceType
     _namespace = maec.package._namespace

     id = maec.TypedField('id')
     action_reference = maec.TypedField('Action_Reference', ActionReference, multiple = True)

        
class ActionEquivalenceList(maec.EntityList):
    _contained_type = ActionEquivalence
    _binding_class = package_binding.ActionEquivalenceListType
    _binding_var = "Action_Equivalence"
    _namespace = maec.package._namespace