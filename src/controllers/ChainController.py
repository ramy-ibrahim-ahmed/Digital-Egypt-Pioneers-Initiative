from ..helpers import get_settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
import os
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChainController:
    def __init__(self):
        self.prompt = None
        self.llm = None
        self.rag_chain = None
        self.transcript = None
        self.retriever = None

        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.vector_database_dir = "database"

    def prepare_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["context", "student_query"],
            template="""You are an AI assistant helping university students. Here is a student's question and relevant information to assist them:

            {context}

            Student Question:
            {student_query}

            Provide a clear, friendly, and natural answer to the student's question based on the context without any further questions or asking for information about him.
            provide the answer in the same language as the Student Question.
            """,
        )

    def set_transcript(self, transcript: str):
        logger.info("Setting transcript...")
        self.transcript = transcript
        logger.info("Transcript set successfully.")

    def prepare_llm(self):
        api_key = get_settings().GEMINI_API_KEY
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-002",
            temperature=0,
            api_key=api_key,
        )

        self.llm = model

    def load_retriever(self):
        try:
            logger.info("Loading retriever...")
            if os.path.exists(self.vector_database_dir):
                logger.info("Loading existing Chroma database...")
                vector_store = Chroma(
                    persist_directory=self.vector_database_dir,
                    embedding_function=self.embedding_model,
                )
                logger.info("Chroma database loaded successfully.")
            else:
                logger.error(
                    "Chroma database not found. Please create the vector store first."
                )
                raise FileNotFoundError("Vector store not found.")
            return vector_store.as_retriever()
        except Exception as e:
            logger.exception("Failed to load retriever.")
            raise RuntimeError("Retriever loading error") from e

    def prepare_agent(self):
        def get_student_data(input=""):
            return self.transcript

        get_student_informations = Tool(
            name="GradeTool",
            func=get_student_data,
            description="Invoke this tool when a student asks for something related to their courses or grades or information or GPA.",
        )

        self.llm = initialize_agent(
            tools=[get_student_informations],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
        )

    def prepare_rag_chain(self):
        def format_docs(docs):
            return "\n\n".join(doc.metadata["responses"] for doc in docs)

        def ensure_string(input_dict):
            return str(self.prompt.format(**input_dict))

        self.retriever = self.load_retriever()

        self.rag_chain = (
            {
                "context": self.retriever | RunnableLambda(format_docs),
                "student_query": RunnablePassthrough(),
            }
            | RunnableLambda(ensure_string)  # Convert to string here
            | self.llm
            | RunnableLambda(lambda x: x["output"])  # Ensure the output is a string
            | StrOutputParser()
        )

    def process(self, query):
        self.prepare_llm()
        self.prepare_agent()
        self.prepare_prompt()
        self.prepare_rag_chain()

        try:
            full_response = self.rag_chain.invoke(query)
        except Exception as e:
            logger.error("Error processing query: %s", e)  # Log the error for debugging
            return "I can't answer."  # Return the specific string on error

        return full_response
