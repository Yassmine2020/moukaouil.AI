<div style="text-align: center;">
    <img src="https://github.com/Yassmine2020/SythSis/assets/81428754/655bea69-d5fa-4d36-b59a-dbf552f3dd05" width="100" alt="image">
</div>

## Background and problem statement

The problem addressed by [Almokaoul.AI](http://almokaoul.ai/) is the multitude of challenges faced by pre-seed stage entrepreneurs in Morocco. These challenges often lead to a lack of direction, inefficiencies, and missed opportunities, hindering the potential success of many promising startups. Specifically, the issues include: **Lack of Clear Vision on Business Models, Insufficient Knowledge of Legal Aspects, Uncertainty About Potential Partners/Investors …**

## Our solution

Our project, Almokaoul.AI, mitigates these problems by introducing a comprehensive app tailored specifically for pre-seed stage entrepreneurs in Morocco. The app provides a complete overview of essential knowledge and tools, addressing various aspects of startup development. Key features include:

1. **Business Model Generation**: The app offers guided assistance in creating business models.
2. The app offers tools for generating graphs and plots based on the user's data. These visualizations which enables the entrepreneur to make informed decisions
3. **Interactive Chatbot**: A sophisticated chatbot interacts with users to understand their needs and provide personalized guidance. Whether the user needs help with legal aspects, business model generation, or data management, the chatbot offers relevant advice and resources tailored to the Moroccan context.

## Team

[Yassmine ED-DYB](https://www.linkedin.com/in/yassmineeddyb/)

[Oussama QOUTI](https://www.linkedin.com/in/oussama-qouti-105bb820a/)

## Pipeline:
This diagram shows the flow of user interactions within the Almokaoul.AI system.

```mermaid
graph TD
  A[User Prompt] --> B[Chatbot]
  B --> C[Model's Processing]
  C --> D[RAG & Web Search]
  D --> E{Response Type}
  E --> |Business Model| F[Business Model Page]
  E --> |Counseling| G[Counseling Response]
  E --> |Data Plots| H[Data Visualization Page]
'''
### The models:

The core of our system consists of :

- LLM (Large language Model): *OpenAI API or [Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)*

### Personalization on the morocans context (**using retrieval augmented generation)**

- In this segment, the following steps were taken:
1. We feed our model by:
    1.  **File.txt**: This file, scraped from the web, contains general information about startup aspects and information in Morocco.
    2. **Websites and Blogs**: These sources provide insights into competitors in fintech, potential partners, and other relevant and more specified startup aspects in Morocco.
    
    Example of URLs providing general information about startups in Morocco:
    
    ```
    urls_general = [
        "https://www.healyconsultants.com/morocco-company-registration/setup-llc/",
        "https://life-in-morocco.com/registering-company-in-morocco",
        "https://moroccofintech.uk/regulatory-bodies/",
        "https://casablancafinancecity.com/fintech/?lang=en",
        "https://africanlegalfactory.com/2022/01/28/comment-creer-sa-startup-au-maroc/",
        "https://wecount.ma/en/morocco-company-formation-start-a-business-in-morocco",
        "https://africanlegalfactory.com/2024/01/30/le-guide-startup-maroc-2024/",
    ]
    ```
    
2. The final dataset was embedded and stored in a vector database using *[ChromaDB](https://github.com/chroma-core/chroma)*.
3. The model uses this embedded data to provide more personalized and contextually relevant answers to users, tailored to the Moroccan startup environment

## Comparing Benchmark

To evaluate whether to use GPT-4 or the open-source Llama as the heart of our project, we conducted a comparison based on human feedback.

1. **Prompt Testing**:
    - We used the same prompt on both models:
        
        ```css
        "I want to build a fintech startup that provides accessible, efficient, and affordable financial services to SMEs and the underbanked population in Morocco. What might be the competitors?"
        ```
        
2. **Model Responses**:
    - **GPT-4**:
        
        ```css
        "Potential competitors for your fintech startup in Morocco targeting SMEs and the underbanked population may include CASHPLUS, S2M, and Gini. It would be beneficial to conduct a more in-depth analysis of these companies to understand their offerings and market positioning better."
        ```
        
    - **Llama**:
        
        ```vbnet
        "The potential fintech competitors in Morocco include HPS, Onepay, Peaqock Financials, Inwi Money, Karny, M2M Group, and other fintech companies in Morocco. It is crucial to understand the competitive landscape and identify the unique value proposition of your fintech startup to succeed in the Moroccan fintech market. It is also essential to research and analyze the fintech companies in Morocco, their products and services, target market, and competitive strategy to gain a deeper understanding of the competitive landscape."
        ```
        
3. **Feedback Collection**:
    - We asked our classmates and mentors to review the answers and indicate their preference.
4. **Results**:
    - The majority preferred the GPT-4 answer over Llama's answer, so we linked the gbt-4 with our UI

## Demo
