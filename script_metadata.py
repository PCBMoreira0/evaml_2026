from rich import print, box
from rich.console import Console
from rich.table import Table

console = Console()

class ScriptMetadata():

    def identify_targets(self, xml_root, verbose_mode=False):
        tab_ids = {}
        for element in xml_root.iter():
            # If element.get("id") and element.tag != "macro": # Cria a tabela com os elementos que possuem o atributo "id" excluindo as macros.
            if element.get("id"):
                tab_ids[element.get("id")] = [element.tag, element]
        if verbose_mode:
            print("")
            table = Table(title="[b]Table: Element Identifiers (IDs)[/]")
            table.add_column("Identifier")
            table.add_column("Element type")
            for item in sorted(tab_ids):
                table.add_row("[bold yellow]" + tab_ids[item][1].get("id"), "[bold cyan ]" + str(tab_ids[item][0]))
            console.print(table)
        return tab_ids



    
