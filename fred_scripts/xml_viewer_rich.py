from rich.console import Console
from rich.tree import Tree
from lxml import etree

def xml_to_tree(elemento, tree):
    # Adicionar atributos, se existirem
    attrs = ""
    if elemento.attrib:
        attrs = " " + " ".join([f'{k}="{v}"' for k, v in elemento.attrib.items()])
    
    # Criar nó da árvore
    node_text = f"[bold cyan]{elemento.tag}[/bold cyan]{attrs}"
    node = tree.add(node_text)
    
    # Adicionar texto, se houver
    if elemento.text and elemento.text.strip():
        node.add(f"[green]\"{elemento.text.strip()}\"[/green]")
    
    # Adicionar filhos recursivamente
    for filho in elemento:
        xml_to_tree(filho, node)

# Carregar o XML
tree = etree.parse("teste_case.xml")
root = tree.getroot()

# Criar árvore visual
console = Console()
visual_tree = Tree(f"[bold magenta]{root.tag}[/bold magenta]")

# Construir a visualização
for child in root:
    xml_to_tree(child, visual_tree)

# Exibir
console.print(visual_tree)