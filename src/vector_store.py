from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings

import os
import json

intents = []
directory_path = r"src\data"

for filename in os.listdir(directory_path):
    if filename.endswith(".json"):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, "r") as file:
            data = json.load(file)
            if isinstance(data, dict):
                intents.extend(data.get("intents", []))


def prepare_documents(intents):
    documents = []
    for intent in intents:
        for pattern in intent["patterns"]:
            documents.append(
                Document(
                    page_content=pattern,
                    metadata={
                        "tag": intent["tag"][0],
                        "responses": str(intent["responses"]),
                    },
                )
            )
    return documents


documents = prepare_documents(intents)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

persist_directory = os.path.join(os.getcwd(), "chroma_db")

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=HuggingFaceEmbeddings(),
    persist_directory=persist_directory,
)

vectorstore.persist()
