
import time
from rich.progress import Progress, BarColumn
from rich import print

#### STEP 1 ##### XML Validation
# EvaML script validation function. #########################################################
def evaml_validation(ET, schema, evaml_file):
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

  try:
    valido = True
    val = schema.iter_errors(evaml_file)
    for idx, validation_error in enumerate(val, start=1):
      print(f'  [{idx}] path: [red b]{validation_error.path}[/] | reason: {validation_error.reason}')
      valido = False
  except Exception as e:
    print(val)
    print(e)
    print("\n[b white on red blink] VALIDATION ERROR 👆 [/]: The script [b cyan]" + evaml_file.split("/")[-1] + " [/][b white]failed[/]. Please, [b white]check[/] the info above.\n")
    exit(1)
  else:
    if valido == True:
      print(" ✅ [b green reverse] The script was validated! [/]\n")
      return ET.parse(evaml_file) #
    else:
      print("\n[b white on red blink] VALIDATION ERROR 👆 [/]: The script [b cyan]" + evaml_file.split("/")[-1] + " [/][b white]failed[/]. Please, [b white]check[/] the info above.\n")
      print("")
      exit(1)