import os
import xml.etree.ElementTree as ET
from rich.progress import Progress, BarColumn
import time

from rich import print, box
from rich.console import Console
from rich.table import Table

console = Console()

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


def aplicar_defaults(xml_file_ok, defaults):
    # xml_file_ok = ET.parse(xml_path)
    root = xml_file_ok.getroot()
    for elem in root.iter():
        tag = elem.tag
        if tag in defaults:
            for attr, val in defaults[tag].items():
                if attr not in elem.attrib:
                    elem.set(attr, val)

    return xml_file_ok


def process_default_attributes(xsd_path, xml_file_ok):
    # Processing default attributes. #########################################################################
    with Progress(
        "[bold blue]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    ) as progress:
        task = progress.add_task("[b white reverse] STEP 2. Processing default attributes     ", total=30)
        
        for i in range(30):
            progress.update(task, advance=1)
            time.sleep(0.02)
            
    defaults = extrair_defaults_de_xsd(xsd_path)
    print("")
    table = Table(title="[bold]Table: Default Attributes in XMLSchema", box=box.DOUBLE_EDGE) # show_header=False, box=None (Some options)
    table.add_column("XML Element")
    table.add_column("Attribute", justify='center')
    table.add_column("Default value")
    for element, attrs in defaults.items():
        for attr, value in attrs.items():
            table.add_row("[bold yellow]" + element, "[bold cyan ]" + attr, "[bold green]" + value)
    console.print(table)

    print(" ✅ [b green reverse] The default attributes was injected! [/]\n")

    return aplicar_defaults(xml_file_ok, defaults)




# # ==== Exemplo de uso ====
# xsd_path = "/home/marcelo/evaml_2025/robot_package/xml_schema/evaml_schema.xsd"
# xml_path = "/home/marcelo/evaml_2025/eva_scripts/pcb2.xml"
# out_path = "/home/marcelo/evaml_2025/eva_scripts/meu_script_expandido.xml"

# defaults = extrair_defaults_de_xsd(xsd_path)
# print("Defaults encontrados:", defaults)

# aplicar_defaults(xml_path, defaults, out_path)
# print(f"XML expandido salvo em: {out_path}")
