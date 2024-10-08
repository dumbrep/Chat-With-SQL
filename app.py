import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_openai import ChatOpenAI
import os
from streamlit import session_state as ss
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Chat with SQL DB", page_icon="📚")
st.title("📚 Chat with SQL DB")

LOCALDB = 'UDE_LOCAL_DB'
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLLite 3 Database - Student.db", "Connect to your SQL Database"]

selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    ss.db_uri = MYSQL
    ss.mysql_host = st.sidebar.text_input("MySQL Host (e.g., localhost or IP)")
    ss.mysql_user = st.sidebar.text_input("MySQL User")
    ss.mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    ss.mysql_db = st.sidebar.text_input("MySQL Database")
else:
    ss.db_uri = LOCALDB

if not ss.db_uri:
    st.info("Please enter Database Information")

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o")

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        # Validate MySQL parameters
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.write("Please provide complete information")
            st.stop()

        # Debugging the connection string
        connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
        st.write(f"Attempting to connect using: {connection_string}")

        # Try connecting and catch any errors
        try:
            engine = create_engine(connection_string)
            connection = engine.connect()
            connection.close()  # Close the connection immediately if successful
            return SQLDatabase(engine)
        except Exception as e:
            st.error(f"Failed to connect to the MySQL database: {e}")
            st.stop()

if ss.db_uri == MYSQL:
    db = configure_db(db_uri=ss.db_uri, mysql_host=ss.mysql_host, mysql_user=ss.mysql_user,
                      mysql_password=ss.mysql_password, mysql_db=ss.mysql_db)
else:
    db = configure_db(ss.db_uri)

# Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in ss or st.sidebar.button("Clear message history"):
    ss["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in ss.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from database")

if user_query:
    ss.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        ss.messages.append({"role": "assistant", "content": response})
        st.write(response)
