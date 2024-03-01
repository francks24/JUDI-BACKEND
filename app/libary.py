# from datetime import datetime as now
# import os
# from azure.storage.blob import BlobServiceClient
# from fastapi import HTTPException
# from app.model import Message
# import openai
# from reportlab.pdfgen import canvas
# from decouple import config

# AZURE_ENDPOINT = config("AZURE_ENDPOINT")
# API_VERSION = config("API_VERSION")
# API_KEY = config("API_KEY")
# STORAGE_ACCOUNT_NAME = config("STORAGE_ACCOUNT_NAME")

# CONNECTION_STRING = config("CONNECTION_STRING")
# CONTAINER_NAME = config("CONTAINER_NAME")

# openai.api_type = "azure"
# # Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
# openai.api_version = "2023-08-01-preview"

# # Azure OpenAI setup
# openai.api_base = "https://judi.openai.azure.com/"
# openai.api_key = "56366effe036483aae6c211a1ef7e119"  # Utilisez directement votre clé API ici
# deployment_id = "judi_FA" # Add your deployment ID here



# # Modifiez la fonction send_chat pour accepter une liste d'objets Message au lieu de dictionnaires JSON
# def send_chat(message_text: list[Message]):
#     # Convertir les objets Message en dictionnaires JSON
#     messages_json = [message.dict() for message in message_text]

#     # Encoder et décoder le contenu des messages en UTF-8
#     for message in messages_json:
#         message['content'] = message['content'].encode('utf-8').decode('utf-8')

#     # Appel à l'API OpenAI
#     completion = openai.ChatCompletion.create(
#         deployment_id=deployment_id,
#         messages=messages_json,
#         temperature=0.7,
#         max_tokens=800,
#         top_p=0.95,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stop=None
#     )
 
#     return completion.choices[0].message.content
 
# # Modifiez le code où vous appelez send_chat pour utiliser des objets Message au lieu de dictionnaires JSON
# message_list = [Message(role="system", content="Tu t'appelle JUDY. Tu es une assistant de chat qui peut repondre à des questions sur les assurances."),
#                 Message(role="user", content="qui est tu ?")]
 
# # Utiliser la liste d'objets Message pour appeler send_chat
# response = send_chat(message_list)



# # Note: This code sample requires OpenAI Python library version 0.28.1 or lower.
# # Note: The openai-python library support for Azure OpenAI is in preview.
# from datetime import datetime as now
import os
from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException
from app.model import Message
from openai import AzureOpenAI
from reportlab.pdfgen import canvas
from decouple import config

AZURE_ENDPOINT = config("AZURE_ENDPOINT")
API_VERSION = config("API_VERSION")
API_KEY = config("API_KEY")
STORAGE_ACCOUNT_NAME = config("STORAGE_ACCOUNT_NAME")


CONNECTION_STRING = config("CONNECTION_STRING")
CONTAINER_NAME = config("CONTAINER_NAME")



client = AzureOpenAI(azure_endpoint="https://judi.openai.azure.com/",
                     api_version="2024-02-15-preview",
                     api_key="56366effe036483aae6c211a1ef7e119")

message_text = [
    {"role": "system", "content": "Tu t'appelle JUDY. Tu es une assistant de chat qui peut repondre à des questions sur les assurances."},
    {"role": "user", "content": "Redige une demande de perte ? a GNA assurances"},
]


def send_chat(messages_list: list[Message]):
    response = client.chat.completions.create(model="judi_FA",
                                              messages=messages_list,
                                              temperature=0.7,
                                              max_tokens=800,
                                              top_p=0.95,
                                              frequency_penalty=0,
                                              presence_penalty=0,
                                              stop=None)

    return response.choices[0].message.content


# Write a function that gets a formated text as input and return a pdf file
async def generate_pdf(text):

    # generate a name for the pdf file thta starts with : Document and has the date inside
    pdf_name = f"Document-{now.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf"

    # Create a PDF document
    pdf_canvas = canvas.Canvas(pdf_name)

    # Set font and size
    pdf_canvas.setFont("Helvetica", 12)

    # Split the text into lines and add to the PDF
    lines = text[3:].split('\n')
    y_position = 750  # Starting position from the top of the page

    for line in lines:
        pdf_canvas.drawString(50, y_position, line)
        y_position -= 12  # Move to the next line

    # Save the PDF file
    pdf_canvas.save()
    path = await uploadtoazure(pdf_name)
    return path


async def uploadtoazure(file_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(
        CONNECTION_STRING)
    try:
        container_client = blob_service_client.get_container_client(
            CONTAINER_NAME)
        with open(file=os.path.join('.', file_name), mode="rb") as data:
            container_client.upload_blob(
                name=file_name, data=data, overwrite=True)
    except Exception as e:
        print(e)
        raise HTTPException(401, "Something went terribly wrong..")

    path_name = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{file_name}"
    return path_name 