import openai
import os

openai.api_version = "2023-08-01-preview"
openai.api_type = "azure"
openai.api_base = "https://judi.openai.azure.com/" 
openai.api_key = "56366effe036483aae6c211a1ef7e119"
deployment_id = "judi_FA"
search_endpoint = "https://energygpt.search.windows.net"
search_key = os.getenv("")
search_index_name = "judi"

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}


async def send_chat(message_text):
    # Convertir les objets Message en dictionnaires avant de les envoyer à OpenAI
    serialized_messages = [message.to_dict() for message in message_text]
    
    response = openai.Completion.create(
        engine="text-davinci-002",  # Spécifiez le moteur à utiliser
        deployment_id=deployment_id,
        messages=serialized_messages,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    
    return response.choices[0].message.content
