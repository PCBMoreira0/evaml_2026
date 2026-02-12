from communicator_interface import CommunicatorInterface
import requests

class HttpCommunicator(CommunicatorInterface):
    """
    Estratégia para comunicação via HTTP, usando httpbin.org para teste.
    """
    def __init__(self, xml_node):

        self.xml_node = xml_node
        self.base_url = self.xml_node.get("url")
        print(f"[HTTP]: Conectado à URL base '{self.base_url}'.")
    
    def send(self, **kwargs):
        """
        Envia dados usando um POST e lida com possíveis erros.
        """
        try:
            url = f"{self.base_url}/post"
            response = requests.post(url, json=data)
            response.raise_for_status() # Lança um erro se o status for 4xx ou 5xx
            print(f"[HTTP]: Enviado com sucesso para '{url}'.")
        except requests.exceptions.RequestException as e:
            print(f"[ERRO HTTP]: Falha no envio: {e}")
            raise

    def receive(self) -> dict:
        """
        Recebe dados usando um GET e lida com a resposta.
        """
        try:
            url = f"{self.base_url}/get"
            response = requests.get(url)
            response.raise_for_status()
            
            # Retorna o JSON da resposta
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"[ERRO HTTP]: Falha no recebimento: {e}")
            return {"status": "error", "message": f"Erro na requisição: {e}"}