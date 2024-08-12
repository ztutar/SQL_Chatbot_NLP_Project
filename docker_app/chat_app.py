from langchain_community.llms import Ollama
import streamlit as st
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain_community.utilities import  SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
import sqlite3
import langchain
from pathlib import Path
langchain.debug = True


st.set_page_config(page_title="Chat with SQL DB", page_icon="🤖")
st.title("📦  Chat with SQL DB  🤖")

INJECTION_WARNING = """
                    SQL agent can be vulnerable to prompt injection. Use a DB role with limited permissions.
                    Read more [here](https://python.langchain.com/docs/security).
                    """
LOCALDB = "USE_LOCALDB"

# User inputs
radio_opt = ["Use sample database - Chinook.db", "Connect to your SQL database"]
selected_opt = st.sidebar.radio(label="Choose suitable option", options=radio_opt)
if radio_opt.index(selected_opt) == 1:
    st.sidebar.warning(INJECTION_WARNING, icon="⚠️")
    db_uri = st.sidebar.text_input(
        label="Database URI", placeholder="mysql://user:pass@hostname:port/db"
    )
else:
    db_uri = LOCALDB
    
# Check user inputs
if not db_uri:
    st.info("Please enter database URI to connect to your database.")
    st.stop()

# initialize model
llm = Ollama(model="codegemma:2b", temperature=0, verbose=True)

def configure_db(db_uri):
    if db_uri == LOCALDB:
        # Make the DB connection read-only to reduce risk of injection attacks
        # See: https://python.langchain.com/docs/security
        db_filepath = (Path(__file__).parent / "database/Chinook.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    return SQLDatabase.from_uri(database_uri=db_uri)


db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi! How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Hi! How can I help you?")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)