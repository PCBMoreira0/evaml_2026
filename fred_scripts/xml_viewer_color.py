from lxml import etree
import graphviz
import hashlib

def xml_to_graphviz_colored(elemento, graph, parent_id=None, contador=[0], cores=None, cores_cache=None):
    # Inicializar dicionário de cores e cache se não fornecidos
    if cores is None:
        # Você pode personalizar este dicionário com as cores desejadas para tags específicas
        cores = {
            "light": "lightblue",
            "led": "lightgreen",
            "wait": "lightyellow",
            "evaEmotion": "lightpink",
            "goto": "lightcoral"
            # Adicione mais mapeamentos de tag para cor conforme necessário
        }
    
    if cores_cache is None:
        cores_cache = {}
    
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
    
    # Determinar a cor para este tipo de nó
    tag = elemento.tag
    
    # Removendo namespace se existir (formato {namespace}tag)
    if "}" in tag:
        tag = tag.split("}")[1]
    
    # Usar cor definida ou gerar uma cor consistente baseada na tag
    if tag in cores:
        cor = cores[tag]
    else:
        # Se a tag não tiver uma cor definida, gerar uma cor baseada no hash da tag
        if tag not in cores_cache:
            # Usar um hash da tag para gerar uma cor consistente para cada tipo de tag
            hash_obj = hashlib.md5(tag.encode())
            hash_val = int(hash_obj.hexdigest(), 16)
            # Gerar cor HSL com saturação e luminosidade fixas para boa visibilidade
            hue = hash_val % 360
            cores_cache[tag] = f"0.{hue} 0.3 0.85"  # HSL no formato que o Graphviz aceita
        cor = cores_cache[tag]
    
    # Adicionar nó ao grafo com a cor apropriada
    graph.node(node_id, node_label, style="filled", fillcolor=cor)
    
    # Conectar ao pai
    if parent_id:
        graph.edge(parent_id, node_id)
    
    # Processar filhos
    for filho in elemento:
        xml_to_graphviz_colored(filho, graph, node_id, contador, cores, cores_cache)
    
    return node_id

# Carregar o XML
tree = etree.parse("tabuada_nova.xml")
root = tree.getroot()

# Criar grafo
dot = graphviz.Digraph(comment='XML Tree Visualization', format='svg')
dot.attr('node', shape='box')
dot.attr('graph', rankdir='LR')  # Layout da esquerda para a direita

# Construir a visualização
xml_to_graphviz_colored(root, dot)

# Renderizar para arquivo
dot.render('xml_tree_colored', cleanup=True)
print("Imagem colorida gerada como 'xml_tree_colored.png'")