from rich import print



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    # Verifica se o <goto> tem o atributo "target" definido
    target_value = node.get('target')
    if target_value == None:
        print("[red bold]Target ID no found on <goto>.")
        exit(1)

    # Procura pelo id em tab_ids
    for key, value in memory.tab_ids.items():
        if key == node.get("target"):
            print("[b white]State:[/] Jumping ↪️  to the element [b white]" + value[1].tag.capitalize() + "[/] with [b white]id=" + value[1].get("id") + "[/].")
            return value[1] # Retorna o elemento associado ao id encontrado.
    
    # Não encontrou o "id"
    print("[red bold]It was not possible to find the target: " + target_value)
    exit(1)
