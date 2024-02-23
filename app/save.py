import openai
import os
import requests

openai.api_type = "azure"
# Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
openai.api_version = "2023-08-01-preview"

# Azure OpenAI setup
openai.api_base = "https://judi.openai.azure.com/"  # Add your endpoint here
openai.api_key = "56366effe036483aae6c211a1ef7e119"  # Add your OpenAI API key here
deployment_id = "judibot"  # Add your deployment ID here

# Azure AI Search setup
# Add your Azure AI Search endpoint here
search_endpoint = "https://energygpt.search.windows.net"
search_key = "oxLPc2bptZfgW9INOH71qdps3atu6EhaNaUtCBi4yZAzSeDih7tG"  # Add your Azure AI Search admin key here
search_index_name = "judi"  # Add your Azure AI Search index name here


def setup_byod(deployment_id: str) -> None:
    """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.

    :param deployment_id: The deployment ID for the model to use with your own data.

    To remove this configuration, simply set openai.requestssession to None.
    """

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `deployment_id`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )

    openai.requestssession = session


setup_byod(deployment_id)


message_text = [
    {"role": "user", "content": "What are the differences between Azure Machine Learning and Azure AI services?"}]

completion = openai.ChatCompletion.create(
    messages=message_text,
    deployment_id=deployment_id,
    dataSources=[  # camelCase is intentional, as this is the format the API expects
        {
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": "$search_endpoint",
                "indexName": "$search_index",
                "semanticConfiguration": "default",
                "queryType": "vector",
                "fieldsMapping": {},
                "inScope": True,
                "roleInformation": "Tu t'appelle Judi, tu es un assistant qui a été trainé sur des données de droit afin de repondre a1 des questions.\nTu ne repondras qu'en francais et tes reponses doivent être basées sur ",
                "filter": None,
                "strictness": 3,
                "topNDocuments": 5,
                "key": "$search_key",
                "embeddingDeploymentName": "embeding"
            }
        }
    ],
    enhancements=None,
    temperature=0,
    top_p=1,
    max_tokens=800,
    stop=None,
    stream=True

)
print(completion)