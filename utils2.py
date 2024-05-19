from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.chains import RetrievalQA
from typing import Tuple, Dict
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import MessagesPlaceholder
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentExecutor
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.document_loaders.text import TextLoader
from langchain.schema import Document
import os
from PIL import Image
import streamlit as st

os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_API_KEY']
tavily_api_key = os.environ['TAVILY_API_KEY']
openai_api_key = os.environ['OPENAI_API_KEY']

embeddings = OpenAIEmbeddings()

# Load the documents

loader = TextLoader("Data_blog.txt")
pages = loader.load()

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

chunks_text = split_text(pages)
docs_text = [doc.page_content for doc in chunks_text]


# Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=docs_text,
    collection_name="rag-chroma",
    embedding=embeddings,
)

class Config():
    """
    Contains the configuration of the LLM.
    """
    model = 'gpt-4-turbo'
    llm = ChatOpenAI(temperature=0, model=model)
cfg = Config()
qa = RetrievalQA.from_chain_type(
    llm=cfg.llm,
    chain_type="stuff",
    retriever = vectorstore.as_retriever()
)

def setup_memory() -> Tuple[Dict, ConversationBufferMemory]:
    """
    Sets up memory for the open ai functions agent.
    :return a tuple with the agent keyword pairs and the conversation memory.
    """
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    return agent_kwargs, memory

def setup_agent() -> AgentExecutor:
    """
    Sets up the tools for a function based chain.
    We have here the following tools:

    """
    cfg = Config()
    tools = [
        Tool(
            name="knowledge search",
            func=qa.run,
            description="useful for when you need advanced search option to answer questions about making a company in morocco. "
        ),
        Tool(
        name='web search',
        func=TavilySearchResults(api_key=tavily_api_key).run,
        description=(
            '''use this tool when you can't find the content in the knowledge base and you need more advenced search functionalities '''
        ))
        
    ]
    agent_kwargs, memory = setup_memory()

    return initialize_agent(
        tools,
        cfg.llm,
        verbose=False,
        agent_kwargs=agent_kwargs,
        memory=memory,
        handle_parsing_errors=True
    )


