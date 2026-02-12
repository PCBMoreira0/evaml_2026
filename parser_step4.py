
import time
from rich.progress import Progress, BarColumn
from rich import print


def generate_evaml_file(xml_file_ok, script_file):
  # Generates the file with the expanded loops (if any).
  with Progress(
      "[bold blue]{task.description}",
      BarColumn(),
      "[progress.percentage]{task.percentage:>3.0f}%",
  ) as progress:
      task = progress.add_task("[b white reverse] STEP 4. Generating the EvaML file [/]", total=30)
      
      for i in range(30):
          progress.update(task, advance=1)
          time.sleep(0.02)

  print(" ✅ [b green reverse] The file " +  script_file.split('/')[-1][:-4] + "_evaml.xml" + " was created! [/]\n\n")

  xml_file_ok.write(script_file[:-4] + "_evaml.xml", "UTF-8")


