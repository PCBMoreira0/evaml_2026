import sys
import os
import copy # lib for generating copies of objects

import xml.etree.ElementTree as ET
import xmlschema # xmlschema validation

from lxml import etree

from rich import print
from rich.console import Console
from rich.progress import Progress, BarColumn

import time

import config

console = Console()



# EvaML script validation function. #########################################################
def evaml_validator(evaml_file):
  global tree
  try:
    valido = True
    val = schema.iter_errors(evaml_file)
    for idx, validation_error in enumerate(val, start=1):
      print(f'  [{idx}] path: [red b]{validation_error.path}[/] | reason: {validation_error.reason}')
      valido = False
  except Exception as e:
    print(val)
    print(e)
    return None
  else:
    if valido == True:
      # Valida e injeta os defaults, salvando o novo arquivo
      return ET.parse(evaml_file) #
    else:
      return None


###############################################################################
# (Parsing) Command processing (loop)                                         #
###############################################################################
def parse_loop(script_node):
    global id_loop_number
    for i in range(len(script_node)):
      if len(script_node[i]) != 0: parse_loop(script_node[i])
      if script_node[i].tag == "loop":
        id_loop_number += 1 # Var used to create names for some automatic variables. Starts with 1.
        loop_copy = copy.deepcopy(script_node[i]) # Copy the <loop> element.
        c = ET.Element("counter") # Creates the <counter> that initializes the iteration var with the value zero.
        if script_node[i].get("id") != None: # If the <loop> is the target of a goto.
          id_loop = script_node[i].attrib["id"] 
          c.attrib["id"] = id_loop
        if script_node[i].get("var") != None: 
          var_loop = script_node[i].attrib["var"] 
          c.attrib["var"] = var_loop
        else: # If the user does not define a variable for the iteration, the default variable "ITERATION_VAR...." will be created.
          var_loop = "ITERATION_VAR" + str(id_loop_number) 

        times_loop = script_node[i].attrib["times"] 
        c.attrib["var"] = var_loop 
        c.attrib["op"] = "=" 
        c.attrib["value"] = "1"  # Initialize the counter variable to zero

        script_node.remove(script_node[i]) # Remove the <loop> element as it is no longer needed (we have a copy of it in )
        script_node.insert(i, c)  # Add the <counter> that initializes the iteration variable

        s = ET.Element("switch")  # Create the <switch> element
        s.attrib["id"] = "LOOP_ID" + str(id_loop_number) + "_" + var_loop  # Default prefix of the automatic id generated for the loop _LOOP_ID_
        s.attrib["var"] = var_loop 
        script_node.insert(i + 1, s)  # Adds the <switch>, with its children, to the script element

        cs = ET.Element("case") # Create the <case> element
        cs.attrib["op"] = "lte" 
        cs.attrib["value"] = times_loop 
        cs.extend(loop_copy)  # extend only adds the loop children

        c = ET.Element("counter")  # Creates the <counter> that increments the iteration variable
        c.attrib["var"] = var_loop
        c.attrib["op"] = "+"
        c.attrib["value"] = "1"
        cs.append(c)

        g = ET.Element("goto")  # Create the <goto> that makes the loop happen
        g.attrib["target"] = "LOOP_ID" + str(id_loop_number) + "_" + var_loop  # default prefix of the automatic id generated for the loop _LOOP_ID_

        cs.append(g)  # Add the <goto> (which causes the repetition) to the end of the <case>

        s.insert(0, cs)  # Inserts the <case> with the body inside the <switch>

        parse_loop(script_node) # Processing a loop changes the initial structure of the scriptnode and needs to be revisited


xmlschema_file = os.getcwd() + "/" + config.ROBOT_PACKAGE_FOLDER + "/xml_schema/evaml_schema.xsd"
schema = xmlschema.XMLSchema(xmlschema_file)



script_file = sys.argv[1]

console.clear()
console.rule("\n🤖 [yellow reverse b]  Parsing the script: " + script_file.split("/")[-1] + "  [/] 🤖")
print()


### STEP 01 ###
# Validating the script. #########################################################################
with Progress(
    "[bold blue]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
) as progress:
    task = progress.add_task("[b white reverse] STEP 1. Validating the script     ", total=30)
    
    for i in range(30):
        progress.update(task, advance=1)
        time.sleep(0.02)
        
xml_file_ok = evaml_validator(script_file)


if not xml_file_ok:
  print("\n[b white on red blink] VALIDATION ERROR 👆 [/]: The script [b cyan]" + script_file.split("/")[-1] + " [/][b white]failed[/]. Please, [b white]check[/] the info above.\n")
  exit(1)
else:
  print(" ✅ [b green reverse] The script was validated! [/]\n")


##################################


####################################

## STEP 02 ###
# Parsing (Loop processing)
with Progress(
    "[bold blue]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
) as progress:
    task = progress.add_task("[b white reverse] STEP 2. Parsing the script file   ", total=30)
    
    for i in range(30):
        progress.update(task, advance=1)
        time.sleep(0.02)

id_loop_number = 0  # Id used to create loop ids.
root = xml_file_ok.getroot() # Evaml root node.
# root = etree.fromstring(ET.tostring(new_xml_element))
script_node = root.find("script")
parse_loop(script_node)

print(" ✅ [b green reverse] Done! [/]\n")


# Generates the file with the expanded loops (if any).
with Progress(
    "[bold blue]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
) as progress:
    task = progress.add_task("[b white reverse] STEP 3. Generating the EvaML file [/]", total=30)
    
    for i in range(30):
        progress.update(task, advance=1)
        time.sleep(0.02)

print(" ✅ [b green reverse] The file " +  script_file.split('/')[-1][:-4] + "_evaml.xml" + " was created! [/]\n\n")

print(type(xml_file_ok))
xml_file_ok.write(script_file[:-4] + "_evaml.xml", "UTF-8")
