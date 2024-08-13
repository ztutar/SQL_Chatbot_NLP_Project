from langchain_community.llms import Ollama
import streamlit as st
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain_community.utilities import  SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.callbacks import StreamlitCallbackHandler
from sqlalchemy import create_engine
import sqlite3
import langchain
import re
from pathlib import Path
langchain.debug = True

st.set_page_config(page_title="Chat with SQL DB", page_icon="🤖")
st.title("📦  Chat with SQL DB  🤖")

INJECTION_WARNING = """
                    SQL agent can be vulnerable to prompt injection. Use a DB role with limited permissions.
                    Read more [here](https://python.langchain.com/docs/security).
                    """
LOCALDB = "USE_LOCALDB"

# Initialize history & model
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "This is a SQL Database Chain that can answer questions about a database. \
        Please input your question below:"}]
if "model" not in st.session_state:
    st.session_state["model"] = ""

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# MODEL SELECTION
models = [model["name"] for model in Ollama.list()["models"]]
st.session_state["model"] = st.sidebar.selectbox("Choose your model:", models)

# DATABASE SELECTION
sql_url = st.sidebar.text_input("SQL URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")
































def sql_to_text(sql_url: str, question: str, model_input: None) -> str:
    """
    Converts an input question into a SQL query, executes the query on a database, and returns the answer.Args:
        sql_url (str): The URL of the SQL database.
        question (str): The input question.
        model_input (str): The model input to use for the language model.
    Returns:
        str: The final answer.
    Raises:
        Exception: If the specified model is not found.
    """
    # setup llm
    llm = Ollama(temperature=0, model=model_input)

    # Prompt LLM
    QUERY = """
    Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
    Use the following format:
    "Question": "Question here"
    "SQLQuery": "SQL Query to run"
    "SQLResult": "Result of the SQLQuery"
    "Answer": "Final answer here"
    "Command: {question}"
    """
    # setup database
    db = SQLDatabase.from_uri(sql_url)
    # Setup the database chain
    db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=False)
    # input prompt 
    question = QUERY.format(question=question)
    result = db_chain.run(question)
    #st.write("Result: ")
    st.write(result)


# database input
def configure_db(sql_url):
    if sql_url == LOCALDB:
        # Make the DB connection read-only to reduce risk of injection attacks
        # See: https://python.langchain.com/docs/security
        db_filepath = (Path(__file__).parent / "database/Chinook.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    return SQLDatabase.from_uri(database_uri=sql_url)


# User inputs
radio_opt = ["Use sample database: Chinook.db", "Connect to your SQL database"]
selected_opt = st.sidebar.radio(label="Choose a suitable DB option:", options=radio_opt)
if radio_opt.index(selected_opt) == 1:
    st.sidebar.warning(INJECTION_WARNING, icon="⚠️")
    sql_url = st.sidebar.text_input(
        label="Database URL", placeholder="mysql://user:pass@hostname:port/db")
else:
    sql_url = LOCALDB
    
# Check user inputs
if not sql_url:
    st.info("Please enter database URL to connect to your database.")
    st.stop()

model = st.sidebar.text_input(label="Choose an Ollama Model:", placeholder="ex:      codellama:7b")

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "This is a SQL Database Chain that can answer questions about a database. \
        Please input your question below:"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Hi! How can I help you?")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container())
        response = sql_to_text(sql_url=sql_url, question=user_query, model_input=model)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)