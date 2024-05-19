import streamlit as st
import streamlit.components.v1 as components
import json
from langchain.prompts import PromptTemplate
from utils import setup_agent
from PIL import Image
import pandas as pd
import json


agent_executor = setup_agent()
#agent_executor2 = setup_agent()


template = """You are an expert assistant for fintech entrepreneurs. Your role is to generate a Business Model Canvas tailored to the user's business.

Business Model Canvas Customization Details:

- Customer Segments: Identify and describe the primary target groups.
- Value Propositions: Outline the unique value or benefits provided.
- Channels: Specify the delivery methods for products or services.
- Customer Relationships: Describe the types of relationships established.
- Revenue Streams: Detail the ways the business generates revenue.
- Key Resources: List crucial assets needed for the business model.
- Key Activities: Identify essential actions for delivering value and maintaining operations.
- Key Partnerships: Highlight important suppliers, partners, or collaborators.
- Cost Structure: Describe major costs, including fixed and variable expenditures.

\n You have access to the following tools:
- knowledge search: For general questions about startups in the Morocan context and To identify the potential competitors of the business
- web search: For advanced search needs beyond the knowledge base.


\n Process:

1. Keep asking follow-up questions until you have all the necessary details.
2. Customize the answer for Morocco, based on knowledge search results.

Use the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [knowledge search, knowledge search for competitors, web search]\n
Action Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat 20 times)

Don't exceed 20 iterations
you have a limit of 20 follow up questions then answer with what you got \n
Thought: I now know the final answer\n
Final Answer: the final answer to the original input question in json format\n\nBegin!\n\n

Question: {input}
Thought: {agent_scratchpad}"""

template2 = """You are "Moukawil.AI," an expert assistant for entrepreneurs in morocco. Your role is to help the user with their business-related questions and all the information related to making running a in Morocco .
You have access to the following tools:
- knowledge search: For company related questions.
- web search: For advanced search needs beyond the knowledge base.

Process:

1. Keep asking follow-up questions until you have all the necessary details.
2. Customize the answer for Morocco, including relevant regulations and information.

Use the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [knowledge search, web search]\n
Action Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat 3 times)
you have the limit of 3 iterations if you don't know the answer then ask follow up questions 
you have a limit of 3 follow up questions then answer with what you got \n
Thought: I now know the final answer\n
Final Answer: the final answer to the original input question\n\nBegin!\n\n

Question: {input}
Thought: {agent_scratchpad}"""

promptup = PromptTemplate(
    input_variables=['agent_scratchpad', 'input'],
    template = template
)
promptup2 = PromptTemplate(
    input_variables=['agent_scratchpad', 'input'],
    template = template2
)


agent_executor.agent.llm_chain.prompt = promptup
#agent_executor2.agent.llm_chain.prompt = promptup2

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    agent_executor.memory.clear()


# Set the page configuration at the start of the script
st.set_page_config(page_title="Moukaouil.AI is Here 🤖💼",
                   page_icon="🤖",
                   layout="wide",
                   initial_sidebar_state="expanded")

def generate_html_content(data_str):
    data = json.loads(data_str)
    with open("canvas.html", "r", encoding='utf-8') as file:
        html_template = file.read()
    # Replace placeholders with data from the chatbot
    for key, value in data.items():
        placeholder = "{{" + key.lower() + "}}"
        # Convert the value to a string if it is not already
        if isinstance(value, list):
            value = ', '.join(value)  # Join list items into a single string
        html_template = html_template.replace(placeholder, value)
    return html_template
# Define the home page function
def page_home():
    # Display the logo
    logo_image_path = "images/logo.png"
    logo_image = Image.open(logo_image_path)
    resized_logo_image = logo_image.resize((1000, 1000))
    st.image(logo_image, use_column_width=True)
    if st.button("Say hello"):
        st.write("Why hello there")
    else:
        st.write("Goodbye")

    # Chat interaction
    avatar_img = "images/avatar.png"

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    # Display or clear chat messages
    for message in st.session_state.messages:
        if message["role"] == "user" :
          with st.chat_message(message["role"]):
              st.write(message["content"])
        else : 
          with st.chat_message(message["role"],avatar = avatar_img ):
              st.write(message["content"])

    # User-provided prompt
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
      with st.chat_message("assistant", avatar="images/logo.png"):
        with st.spinner("Thinking..."):
            content = str(st.session_state.messages[-1]["content"])
            response = agent_executor.invoke(content)
        placeholder = st.empty()
        full_response = ' '
        for item in response['output']:
            full_response += item
            placeholder.markdown(full_response)
        placeholder.markdown(full_response)
      message = {"role": "assistant", "content": full_response}
      st.session_state["last_response"] = full_response
      st.session_state.messages.append(message)
# Define the example page function
def page_bmc():
    if "last_response" in st.session_state:
        html_content = generate_html_content(st.session_state["last_response"])
        components.html(html_content, height=1050, width=900)
        # components.html(html_content)  
    else:
        st.write("No data available. Please interact with the chatbot in the Home page.")

def page_insights():
# Sample data
  data = {'Série 1': [20, 20, 20, 20, 20],
          'Série 2': [20, 20, 20, 20, 20]}


  # Sample data for the bar chart
  data_bar = {'Élément 1': [1, 3, 2, 5, 1],
              'Élément 2': [2, 3, 1, 7, 4],
              'Élément 3': [4, 2, 5, 3, 8]}

  df_bar = pd.DataFrame(data_bar)

  # Sample data for line chart
  data_line = {'Élément 1': [11, 32, 54, 78, 2],
          'Élement 2': [23, 33, 45, 56, 7],
          'Element 3': [43, 78, 23, 45, 89],
          'Élément 4': [87, 23, 54, 12, 90],
          'Element 5': [56, 98, 12, 34, 78]}

  df_line = pd.DataFrame(data_line)

  # Title 
  st.title('Sample Streamlit Dashboard')

  # Layout for columns
  col1, col2,col3,col4= st.columns(4)

  # Bar chart
  with col1:
      st.subheader('Répartition par élément')
      st.bar_chart(df_bar)
  # Line chart
  with col2:
      st.subheader('Evolution')
      st.line_chart(df_line)
  # Display raw data for the bar chart
  with col3:
      st.subheader('Données brutes')
      st.dataframe(df_bar)
  with col4:
      st.header("Some KPI")
      st.write("This is a key performance indicator value.")
def gene_chatbot():
    # # Display the logo
    # logo_image_path = "images/logo.jpeg"
    # logo_image = Image.open(logo_image_path)
    # resized_logo_image = logo_image.resize((400, 400))
    # st.image(resized_logo_image, use_column_width=True)

    # Chat interaction
    avatar_img = "images/avatar.png"

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "bach n3awnk lyom?"}]
    # Display or clear chat messages
    for message in st.session_state.messages:
        if message["role"] == "user" :
          with st.chat_message(message["role"]):
              st.write(message["content"])
        else : 
          with st.chat_message(message["role"],avatar = avatar_img):
              st.write(message["content"])

    # User-provided prompt
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
      with st.chat_message("assistant", avatar="images/logo.png"):
        with st.spinner("Thinking..."):
            content = str(st.session_state.messages[-1]["content"])
            response = agent_executor2.invoke(content)
        placeholder = st.empty()
        full_response = ' '
        for item in response['output']:
            full_response += item
            placeholder.markdown(full_response)
        placeholder.markdown(full_response)
      message = {"role": "assistant", "content": full_response}
      st.session_state.messages.append(message)
# Sidebar navigation setup
with st.sidebar:
    st.title('Meet Moukaouil.AI 🤖💼')
    page = st.selectbox("Choose your page", ["Chatbot 🤖💬", "General Chatbot 🤖💬","Business Model Canvas 📊","Insights 💡"])
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
    st.markdown("""

### Empowering Entrepreneurs at the Pre-Seed Stage 🌱

**Moukaouil.AI** is a cutting-edge Gen AI application designed to support entrepreneurs in the pre-seed stage of their startups. We understand the unique challenges you face, from navigating legal requirements to refining your business model, and our platform is here to help you overcome these hurdles with ease.

### Key Features 🔑

- **Comprehensive Legal Guidance 📜**
  - Gain insights into the legal requirements necessary for starting your business. Our AI provides tailored information to ensure you're compliant with all relevant regulations.

- **Business Model Optimization 📈**
  - Struggling to define a clear and viable business model? Our AI tools analyze your ideas and market data to help you craft a robust business strategy.

- **Risk Assessment ⚠️**
  - Identify and mitigate potential risks early on. Our application evaluates various factors that could impact your startup's success and offers actionable advice.

- **Competitive Analysis 🕵️**
  - Stay ahead of the competition with our in-depth competitor analysis. Discover who your potential competitors are and learn how to differentiate your offerings.


### Why Choose Moukaouil.AI? 🌟

- **Personalized Insights 🎯**
  - Receive recommendations and information tailored specifically to your startup's needs.

- **User-Friendly Interface 🖥️**
  - Our intuitive platform makes it easy to access and understand the information you need, even if you're new to the entrepreneurial world.

### Get Started 🚀

Embark on your entrepreneurial journey with confidence. Let **Moukaouil.AI** be your guide to navigating the complexities of the pre-seed stage and setting the foundation for a successful startup.    """)


# Routing logic based on sidebar selection
if page == 'Chatbot 🤖💬':
    page_home()
# if page == 'General Chatbot 🤖💬':
#     gene_chatbot()
elif page == 'Business Model Canvas 📊':
    page_bmc()
elif page == 'Insights 💡':
    page_insights()
