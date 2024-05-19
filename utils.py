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
from langchain.llms import HuggingFaceEndpoint
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from PIL import Image
import streamlit as st
from langchain.document_loaders.text import TextLoader
from langchain.schema import Document

os.environ['huggingfacehub_api_token'] = st.secrets['huggingfacehub_api_token']
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_API_KEY']
tavily_api_key = os.environ['TAVILY_API_KEY']
openai_api_key = os.environ['OPENAI_API_KEY']

embeddings = OpenAIEmbeddings()

urls_general = [
    "https://www.healyconsultants.com/morocco-company-registration/setup-llc/",
    "https://life-in-morocco.com/registering-company-in-morocco",
    "https://moroccofintech.uk/regulatory-bodies/",
    "https://casablancafinancecity.com/fintech/?lang=en",
    "https://africanlegalfactory.com/2022/01/28/comment-creer-sa-startup-au-maroc/",
    "https://wecount.ma/en/morocco-company-formation-start-a-business-in-morocco",
    "https://africanlegalfactory.com/2024/01/30/le-guide-startup-maroc-2024/",
]

urls_comp = [
    "https://www.f6s.com/companies/fintech/morocco/co",
    "https://startuplist.africa/industry/fintech/morocco",
    "https://resilient.digital-africa.co/blog/2021/06/29/agritech-cle-de-lagriculture-du-futur-au-maroc/#:~:text=2020%20aura%20%C3%A9t%C3%A9%20une%20ann%C3%A9e,devrait%20se%20poursuivre%20en%202021.",
    "https://tracxn.com/d/explore/agritech-startups-in-morocco/__FhjmYrCrw4MQvSQeCBFMFXRQtq1uN5o-UZjDTlzMt00/companies",
    "https://www.f6s.com/companies/agriculture/morocco/co",
    "https://afrique.latribune.fr/africa-tech/startups/2023-06-09/innovation-l-ia-et-l-iot-au-service-de-l-agritech-made-in-maroc-964932.html",
    "https://tracxn.com/d/explore/healthtech-startups-in-morocco/__To2buAuPiiHCHsVSUIMf37PgGQsHNFndjYnq5Utxm-I/companies",
    "https://www.f6s.com/companies/health-medical/morocco/co",
    "https://tracxn.com/d/explore/sports-tech-startups-in-morocco/__mYRCTewf8geq20Y0tyJkHipqy0ChVH-RFRyWKra6BeA/companies",
    "https://www.xyzlab.com/post/startup-accelerators-incubators-in-morocco#google_vignette"
]

docs_general = [WebBaseLoader(url).load() for url in urls_general]
docs_list_gene = [item for sublist in docs_general for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)
doc_splits_gene = text_splitter.split_documents(docs_list_gene)

docs_comp = [WebBaseLoader(url).load() for url in urls_comp]
docs_list_comp = [item for sublist in docs_comp for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)
doc_competitors = text_splitter.split_documents(docs_list_comp)

#doc text
#loader = TextLoader("/content/drive/MyDrive/Data_blog.txt")

loader = TextLoader("test.txt")
pages = loader.load()

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

chunks_text = split_text(pages)
docs_text = [doc for doc in chunks_text]
#doc text
docs = doc_splits_gene + docs_text

# Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=docs,
    collection_name="rag-chroma",
    embedding=embeddings,
)
retriever = vectorstore.as_retriever()

# Add to vectorDB
vectorstore_comp = Chroma.from_documents(
    documents=doc_competitors,
    collection_name="rag-chroma",
    embedding=embeddings,
)
retriever_comp = vectorstore_comp.as_retriever()

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
    retriever = vectorstore.as_retriever(),
    verbose=False
)

qa_comp = RetrievalQA.from_chain_type(
    llm=cfg.llm,
    chain_type="stuff",
    retriever = vectorstore_comp.as_retriever(),
    verbose=False
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
            name="knowledge search for competitors",
            func=qa_comp.run,
            description="useful for when you need advanced search option to answer questions about competitors of a certain type of company in morocco. "
        ),
        Tool(
            name="general knowledge search",
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
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory,
        handle_parsing_errors=True
    )


