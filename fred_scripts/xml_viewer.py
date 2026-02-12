from lxml import etree
import graphviz

def xml_to_graphviz(elemento, graph, parent_id=None, contador=[0]):
    # Gerar ID único para o nó
    contador[0] += 1
    node_id = f"node{contador[0]}"
    
    # Criar label do nó
    attrs = ""
    if elemento.attrib:
        attrs = "\\n" + "\\n".join([f'{k}="{v}"' for k, v in elemento.attrib.items()])
    
    node_label = f"{elemento.tag}{attrs}"
    if elemento.text and elemento.text.strip():
        node_label += f"\\n\"{elemento.text.strip()}\""
    
    # Adicionar nó ao grafo
    graph.node(node_id, node_label)
    
    # Conectar ao pai
    if parent_id:
        graph.edge(parent_id, node_id)
    
    # Processar filhos
    for filho in elemento:
        xml_to_graphviz(filho, graph, node_id, contador)
    
    return node_id

# Carregar o XML
tree = etree.parse("tabuada_nova.xml")
root = tree.getroot()

# Criar grafo
dot = graphviz.Digraph(comment='XML Tree Visualization')
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')

# Construir a visualização
xml_to_graphviz(root, dot)

# Renderizar para arquivo
dot.render('xml_tree', format='svg', cleanup=True)
print("Imagem gerada como 'xml_tree.svg'")