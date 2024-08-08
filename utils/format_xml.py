from lxml import etree

###############################################################################
## FORMAT OF THE COUETTE.XML FILE
###############################################################################

m_encoding = 'UTF-8'

multiline = [
    'scenario-configuration/couette-test/domain',
    'scenario-configuration/couette-test/coupling',
    'scenario-configuration/couette-test/macroscopic-solver',
    'scenario-configuration/couette-test/microscopic-solver',
    'scenario-configuration/mamico/macroscopic-cell-configuration',
    'scenario-configuration/molecular-dynamics/molecule-configuration',
    'scenario-configuration/molecular-dynamics/simulation-configuration',
]

special_line = [
    'scenario-configuration/molecular-dynamics/domain-configuration',
]


def _node_to_multiline(node, indent=0):
    res = ""
    tag = node.tag
    attr = node.attrib
    formatted_string = '\n'.join(f"{'  ' * (indent+1)}{attr}=\"{value}\"" for attr, value in attr.items())
    res += "  " * indent + f"<{tag}\n"
    res += formatted_string + "\n"
    res += "  " * indent + "/>"
    return res


def _node_to_specialline(node, indent=0):
    res = ""
    tag = node.tag
    res += "  " * indent + f"<{tag}\n"
    attr, vals = node.attrib.keys(), node.attrib.values()
    idx = 0
    while attr[idx] != "bottom-south-west":
        res += "  " * (indent+1) + f"{attr[idx]}=\"{vals[idx]}\"\n"
        idx += 1

    x = 0
    res += "  " * (indent+1)
    while idx < len(attr)-1:
        if attr[idx] == "east":
            res += f"{' ' * 32}"
            x += 1
        a = f"{attr[idx]}=\"{vals[idx]}\""
        res += f"{a:<32}"
        idx += 1
        x += 1
        if x % 3 == 0:
            res += "\n" + "  " * (indent+1)
    res += f"{attr[idx]}=\"{vals[idx]}\"\n"

    # formatted_string = '\n'.join(f"{'  ' * (indent+1)}{attr}=\"{value}\"" for attr, value in attr.items())
    # res += "  " * indent + f"<{tag}\n"
    # res += formatted_string + "\n"
    res += "  " * indent + "/>"
    return res


def _rec_iter(node, level, path):
    res = ""
    for el in node:
        if type(el) == etree._Comment:
            res += "  " * level + etree.tostring(el, encoding=m_encoding, with_tail=False).decode(m_encoding) + "\n"
        else:
            children = len([child for child in el if type(child) != etree._Comment])
            if children > 0:
                res += "  " * level + "<" + el.tag
                if len(el.attrib) > 0:
                    res += "".join([f" {key}=\"{value}\"" for key, value in el.attrib.items()])
                res += ">\n"
                res += _rec_iter(el, level+1, path + [el.tag])
                res += "  " * level + "</" + el.tag + ">\n"
                continue
            my_path = "/".join(path + [el.tag])

            if my_path in multiline:
                res += _node_to_multiline(el, level) + "\n"
            elif my_path in special_line:
                res += _node_to_specialline(el, level) + "\n"
            else:
                res += "  " * level + etree.tostring(el, encoding=m_encoding, with_tail=False).decode(m_encoding) + "\n"
            
    return res


def format_xml(node, root_tag):
    res  =  '<?xml version="1.0"?>\n\n'
    res += f'<{root_tag}>\n'
    res += _rec_iter(node, 1, [root_tag])
    res += f'</{root_tag}>'
    return res
