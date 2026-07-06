from rich import print as rprint



def node_processing(node, memory, client_mqtt):
    """ Função de tratamento do nó """

    # Verifica se a <macro> tem o atributo "id" definido
    macro_id = node.get('macro')
    if macro_id == None:
        rprint("[red bold]Macro ID was not found on <useMacro>.")
        exit(1)

    # Procura pelo id em tab_ids
    for key, value in memory.tab_ids.items():
        if key == node.get("macro"):
            rprint("[b white]State:[/] Using macro [b white]" + key + "[/].")
            return value[1] # Retorna a macro associada ao "id" encontrado.
    
    # Não encontrou o "id"
    rprint("[red bold]It was not possible to find the macro: " + key)
    exit(1)

    
