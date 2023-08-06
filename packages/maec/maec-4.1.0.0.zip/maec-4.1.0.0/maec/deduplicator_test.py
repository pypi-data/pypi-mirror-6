from maec.bindings import maec_bundle, maec_package
from maec.bundle.bundle import Bundle
from maec.package.package import Package

package_binding_obj = maec_package.parse("sample_report_maec.xml")
package_obj = Package.from_obj(package_binding_obj)

# Deduplicate all Malware Subjects in the Package
# Right now this works only for Objects
for malware_subject in package_obj.malware_subjects:
    malware_subject.deduplicate_bundles()

# Write out the deduplicated file
package_obj.to_xml_file("deduplicated_maec.xml")