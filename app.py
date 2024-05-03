import base64
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from PIL import Image
import os
import openai


def initialize_session_state():
    if 'vectorstore' not in st.session_state:
        st.session_state['vectorstore'] = FAISS.load_local("faiss_index", embeddings=OpenAIEmbeddings())


def answer(question, vectorstore, qa_chain):
    relevant_docs = vectorstore.similarity_search(question)
    context = ""
    relevant_images = []
    for d in relevant_docs:
        if d.metadata['type'] == 'text':
            context += '[text]' + d.metadata['original_content']
        elif d.metadata['type'] == 'table':
            context += '[table]' + d.metadata['original_content']
        elif d.metadata['type'] == 'image':
            context += '[image]' + d.page_content
            relevant_images.append(d.metadata['original_content'])
    result = qa_chain.run({'context': context, 'question': question})

    return result, relevant_images


def create_conversational_chain():
    # Create llm
    prompt_template = """
    You are an expert Ophthalmologist who treat eye diseases and their management.
    Answer the question based only on the following context, which can include text, images and tables:
    {context}
    Question: {question}
    Don't answer if you are not sure and decline to answer and say "Sorry, I don't have much information about it."
    Just return the helpful answer in as much as detailed possible.
    Answer:
    """

    qa_chain = LLMChain(llm=ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1024),
                        prompt=PromptTemplate.from_template(prompt_template))
    
    return qa_chain

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def main():
    load_dotenv(find_dotenv()) # read local .env file
    openai.api_key  = os.getenv('OPENAI_API_KEY')

    # Initialize Streamlit
    st.set_page_config(page_title="Eye Specialist Bot",
                       page_icon=":male-doctor:",
                       layout='wide',
                       initial_sidebar_state="expanded")
    
    img = get_img_as_base64("Background.png")
    
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img}");
    background-size: 150%;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: local;
    }}

    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}

    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
    # Add a header  
    st.markdown("""
    <style>
    .header {
        position:;
        top:0;
        left:0;
        width:100%;
        background-color: #CC3399;
        color:white;
        text-align:center;
        height:55px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="header" style="display:flex; align-items: center;">
                <h2 style="font-family:ariel; color:white; margin-left:0px; height:75px; font-size:32">Eye Specialist Bot 👨‍⚕️</h2>
        </div>
    """, unsafe_allow_html=True)


    st.markdown("""
                <p2 style="font-family:ariel; color:white; margin-left:0px; height:75px; font-size:32"></p2>
        """, unsafe_allow_html=True)
    
    # Initialize session state & get vectordb
    initialize_session_state()

    #st.header("Eye Specialist Bot :male-doctor:")
    
    # Create the chain object
    chain = create_conversational_chain()

    # Get response
    user_question = st.text_input("Ask any query related to eye diseases :eye:")
    
    if st.button(":green[Search] :stethoscope:"):
        with st.spinner("Searching..."):
            with st.chat_message('Momos', avatar="🤖"):
                response,image = answer(user_question,st.session_state['vectorstore'],chain)
                st.write(response)
                if len(image)>0 and "Sorry, I don't have much information about it" not in response:
                    st.image(image[0])

    # Add a footer  
    st.markdown("""
    <style>
    .footer {
        position:fixed;
        left:0;
        bottom:0;
        width:100%;
        background-color: #CC3399;
        color:white;
        text-align:center;
        height:30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div class="footer">
                <p>Copyright \u00A9 Meril</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()