
import time
from rich.progress import Progress, BarColumn
from rich import print
import copy # lib for generating copies of objects

# ###############################################################################
# (Parsing) Command processing (loop)                                         #
###############################################################################
def process_loop(ET, script_node, id_loop_number):
  for i in range(len(script_node)):
    if len(script_node[i]) != 0: process_loop(ET, script_node[i], id_loop_number)
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

      process_loop(ET, script_node, id_loop_number) # Processing a loop changes the initial structure of the scriptnode and needs to be revisited



#### STEP 2 ##### Default Attributes Processing
#########################################################
# Parsing (Loop processing)
def parse_loop(ET, xml_file_ok):
  with Progress(
      "[bold blue]{task.description}",
      BarColumn(),
      "[progress.percentage]{task.percentage:>3.0f}%",
  ) as progress:
      task = progress.add_task("[b white reverse] STEP 3. Parsing <loop> elements   ", total=30)
      
      for i in range(30):
          progress.update(task, advance=1)
          time.sleep(0.02)


  id_loop_number = 0  # Id used to create loop ids.
  root = xml_file_ok.getroot() # Evaml root node.
  script_node = root.find("script")
  process_loop(ET, script_node, id_loop_number)

  print(" ✅ [b green reverse] Done! [/]\n")

  return xml_file_ok



