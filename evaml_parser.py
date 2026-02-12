import sys
import os

import xml.etree.ElementTree as ET
import xmlschema # xmlschema validation

from rich import print
from rich.console import Console
from rich.progress import Progress, BarColumn

import config

# Importing parser steps modules
from parser_step1 import evaml_validation # STEP 1
from parser_step2 import default_fixed_process # STEP 2
from parser_step3 import parse_loop # STEP 3
from parser_step4 import generate_evaml_file # STEP 4


console = Console()

xmlschema_file_path = os.getcwd() + "/" + config.ROBOT_PACKAGE_FOLDER + "/xml_schema/evaml_schema.xsd"

schema = xmlschema.XMLSchema(xmlschema_file_path)

script_file = sys.argv[1]

console.clear()
console.rule("\n🤖 [yellow reverse b]  Parsing the script: " + script_file.split("/")[-1] + "  [/] 🤖")
print()

# STEP 1 - Validation
xml_file_ok = evaml_validation(ET, schema, script_file)
print("")

# STEP 2 - Default attributes process
xml_file_ok = default_fixed_process(xmlschema_file_path, xml_file_ok)
print("")

# STEP 3 - Parsing <loop> elements
xml_file_ok = parse_loop(ET, xml_file_ok)
print("")

# STEP 4 - Parsing <loop> elements
generate_evaml_file(xml_file_ok, script_file)

