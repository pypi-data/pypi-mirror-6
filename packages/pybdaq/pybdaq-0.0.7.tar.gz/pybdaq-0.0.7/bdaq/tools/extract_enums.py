import os.path
import argparse

from xml.etree import ElementTree as ET


class ExtractedEnum(object):
    def __init__(self, tag_name, value_names):
        self.tag_name = tag_name
        self.value_names = value_names

    def write_pxd(self, file_):
        file_.write("\n    ctypedef enum {}:\n".format(self.tag_name))

        for name in self.value_names:
            file_.write(" " * 8 + "{}\n".format(name))

    def write_pyx(self, file_):
        file_.write("\nclass {}(enum.Enum):\n".format(self.tag_name))

        for name in self.value_names:
            file_.write(" " * 4 + "{0} = _c.{0}\n".format(name))

    @staticmethod
    def from_xml(element, typedefs):
        value_names = [v.attrib["name"] for v in element.findall("EnumValue")]

        return ExtractedEnum(
            typedefs[element.attrib["id"]],
            value_names)


def find_enums(file_or_path):
    # parse XML
    tree = ET.parse(file_or_path)

    # extract typedefs
    typedefs = {}

    for element in tree.findall("Typedef"):
        typedefs[element.attrib["type"]] = element.attrib["name"]

    # extract enums
    enums = []

    for element in tree.findall("Enumeration"):
        enums.append(ExtractedEnum.from_xml(element, typedefs))

    print "Found {} enums to extract.".format(len(enums))

    return enums


def write_cython(pyx_file, pxd_file, enums):
    # write pxd file header
    pxd_file.write("# GENERATED FILE; DO NOT MODIFY\n\n")
    pxd_file.write(
        'cdef extern from "bdaqctrl.h" namespace "Automation::BDaq":')

    # write pyx file header
    pyx_file.write("# GENERATED FILE; DO NOT MODIFY\n\n")
    pyx_file.write("import enum\n\n")
    pyx_file.write("cimport wrapper_enums_c as _c\n\n")

    # write enums
    for extracted in enums:
        print "Extracting definition of {}...".format(extracted.tag_name)

        extracted.write_pyx(pyx_file)
        extracted.write_pxd(pxd_file)

    print "Done extracting definitions."


def main():
    # parse script arguments
    parser = argparse.ArgumentParser(
        description="Extract enum definitions from header.")

    parser.add_argument(
        "--xml-in",
        default="bdaqctrl.h.xml",
        help="path to gccxml result")
    parser.add_argument(
        "--path-out",
        default=".",
        help="path to output directory")

    args = parser.parse_args()

    # extract enums
    enums = find_enums(args.xml_in)
    out_pyx_path = os.path.join(args.path_out, "wrapper_enums.pyx")
    out_pxd_path = os.path.join(args.path_out, "wrapper_enums_c.pxd")

    with open(out_pyx_path, "wb") as out_pyx_file:
        with open(out_pxd_path, "wb") as out_pxd_file:
            write_cython(out_pyx_file, out_pxd_file, enums)

if __name__ == "__main__":
    main()
