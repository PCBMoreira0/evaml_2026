import os
import xml.etree.ElementTree as ET


NS = {"xs": "http://www.w3.org/2001/XMLSchema"}

def extrair_defaults_de_xsd(xsd_path, visitados=None):
    """
    Extrai defaults de atributos nos elementos de um XSD, 
    percorrendo includes recursivamente.
    """
    if visitados is None:
        visitados = set()

    xsd_path = os.path.abspath(xsd_path)
    if xsd_path in visitados:
        return {}

    visitados.add(xsd_path)

    tree = ET.parse(xsd_path)
    root = tree.getroot()

    defaults = {}

    # Extrair defaults de atributos
    for elem in root.findall(".//xs:element", NS):
        elem_name = elem.get("name")
        if elem_name:
            attrs_defaults = {}
            for attr in elem.findall(".//xs:attribute", NS):
                name = attr.get("name")
                default = attr.get("default")
                if default is not None:
                    attrs_defaults[name] = default
            if attrs_defaults:
                defaults[elem_name] = attrs_defaults

    # Percorrer includes
    base_dir = os.path.dirname(xsd_path)
    for inc in root.findall(".//xs:include", NS):
        inc_file = inc.get("schemaLocation")
        if inc_file:
            inc_path = os.path.join(base_dir, inc_file)
            inc_defaults = extrair_defaults_de_xsd(inc_path, visitados)
            defaults.update(inc_defaults)

    return defaults


def aplicar_defaults(xml_path, defaults, out_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for elem in root.iter():
        tag = elem.tag
        if tag in defaults:
            for attr, val in defaults[tag].items():
                if attr not in elem.attrib:
                    elem.set(attr, val)

    tree.write(out_path, encoding="utf-8", xml_declaration=True)


# ==== Exemplo de uso ====
xsd_path = "/home/marcelo/evaml_2025/robot_package/xml_schema/evaml_schema.xsd"
xml_path = "/home/marcelo/evaml_2025/eva_scripts/pcb2.xml"
out_path = "/home/marcelo/evaml_2025/eva_scripts/meu_script_expandido.xml"

defaults = extrair_defaults_de_xsd(xsd_path)
print("Defaults encontrados:", defaults)

aplicar_defaults(xml_path, defaults, out_path)
print(f"XML expandido salvo em: {out_path}")
