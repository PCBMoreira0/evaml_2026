import os
import xml.etree.ElementTree as ET
from rich.progress import Progress, BarColumn
import time

from rich import print, box
from rich.console import Console
from rich.table import Table

console = Console()


XSD_NS = "{http://www.w3.org/2001/XMLSchema}"

def parse_schema(xsd_file, base_path=None, visited=None):
    """Lê um XSD e todos os includes, extraindo defaults e fixed."""
    if visited is None:
        visited = set()
    if base_path is None:
        base_path = os.path.dirname(xsd_file)

    # Evita loops
    if xsd_file in visited:
        return {}
    visited.add(xsd_file)

    tree = ET.parse(xsd_file)
    root = tree.getroot()

    schema_defaults = {}

    # Processa includes
    for inc in root.findall(f"{XSD_NS}include"):
        inc_file = inc.get("schemaLocation")
        if inc_file:
            inc_path = os.path.join(base_path, inc_file)
            schema_defaults.update(parse_schema(inc_path, base_path, visited))

    # Processa elementos e atributos
    for elem in root.findall(f".//{XSD_NS}element"):
        elem_name = elem.get("name")
        if not elem_name:
            continue

        if elem_name not in schema_defaults:
            schema_defaults[elem_name] = {}

        for attr in elem.findall(f".//{XSD_NS}attribute"):
            attr_name = attr.get("name")
            if not attr_name:
                continue

            if "default" in attr.attrib:
                schema_defaults[elem_name][attr_name] = {"default": attr.get("default")}
            if "fixed" in attr.attrib:
                schema_defaults[elem_name][attr_name] = {"fixed": attr.get("fixed")}

    return schema_defaults


def apply_schema_defaults(elem, schema):
    """Aplica os defaults e fixed no XML baseado no schema lido."""
    tag = elem.tag
    if tag in schema:
        for attr, rules in schema[tag].items():
            if "default" in rules and attr not in elem.attrib:
                elem.set(attr, rules["default"])
            if "fixed" in rules:
                elem.set(attr, rules["fixed"])

    for child in elem:
        apply_schema_defaults(child, schema)


def default_fixed_process(xmlschema_file_path, xml_file_ok):
    # Processing default attributes. #########################################################################
    with Progress(
        "[bold blue]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
    ) as progress:
        task = progress.add_task("[b white reverse] STEP 2. Processing Default and Fixed attributes     ", total=30)
        
        for i in range(30):
            progress.update(task, advance=1)
            time.sleep(0.02)

    # Lê schema principal e includes
    schema_defaults = parse_schema(xmlschema_file_path)
    print("")
    table = Table(title="[bold]Table: Default and Fixed attributes in XMLSchema", box=box.DOUBLE_EDGE) # show_header=False, box=None (Some options)
    table.add_column("XML Element")
    table.add_column("Attribute", justify='center')
    table.add_column("Default value", justify='center')
    table.add_column("Fixed value", justify='center')

    for element, attrs in schema_defaults.items():
        if not attrs:  # se não tem atributos, pula
            continue
        for attr_name, attr_rules in attrs.items():
            if "default" in attr_rules:
                table.add_row("[bold yellow]" + element, "[bold cyan ]" + attr_name, "[bold green]" + attr_rules['default'], "---")
                # print(f"{elem}.{attr_name} tem valor default = {attr_rules['default']}")
            elif "fixed" in attr_rules:
                table.add_row("[bold yellow]" + element, "[bold cyan ]" + attr_name, "---", "[bold green]" + attr_rules['fixed'])
                # print(f"{elem}.{attr_name} tem valor fixed = {attr_rules['fixed']}")
    
    console.print(table)

    # Aplica defaults/fixed
    apply_schema_defaults(xml_file_ok.getroot(), schema_defaults)

    return xml_file_ok
