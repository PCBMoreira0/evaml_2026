from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint para simular o recebimento de dados via GET
@app.route('/get', methods=['GET'])
def handle_get():
    # Retorna uma resposta JSON simples.
    return jsonify({"status": "ok", "message": "Dados do servidor de teste."})

# Endpoint para simular o envio de dados via POST
@app.route('/post', methods=['POST'])
def handle_post():
    # O servidor recebe os dados JSON e os devolve na resposta.
    data = request.json
    print(f"Servidor: Recebida requisição POST com dados -> {data}")
    return jsonify({"received_data": data})

if __name__ == '__main__':
    # Inicia o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)