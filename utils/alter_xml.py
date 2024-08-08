import os

from lxml import etree

from plugins.FabMaMiCo.utils.format_xml import format_xml

###############################################################################
## CREATE CONFIGURATIONS
###############################################################################

def alter_xml(dir_path, data, write=None):
    parser = etree.XMLParser(remove_comments=False)
    my_xml = etree.parse(os.path.join(dir_path, data['template']), parser=parser)
    root = my_xml.getroot()
    for key, value in data.items():
        if key == "name" or key == "template":
            continue
        path, field = "/".join(key.split("/")[:-1]), key.split("/")[-1]
        root.find(path).set(field, str(value))
    xml_content = format_xml(root, root.tag)

    if write is not None:
        this_config_path = os.path.join(dir_path, "SWEEP", data['name'])
        os.makedirs(this_config_path, exist_ok=True)
        with open(os.path.join(this_config_path, "couette.xml"), 'w') as file:
            file.write(xml_content)

    return xml_content