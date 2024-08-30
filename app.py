import gradio as gr
from transformers import pipeline
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import sqlite3
import requests

# Global variable to store the database connection object
db = None

# Function to connect to the database
def connectDatabase(url):
    response = requests.get(url)
    sql_script = response.text

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    engine = create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False})
    db = SQLDatabase(engine)


# Function to run a query on the database
def runQuery(query):
    if db:
        return db.run(query)
    else:
        return "Please connect to the database first."


# Function to get the database schema
def getDatabaseSchema():
    if db:
        return db.get_table_info()
    else:
        return "Please connect to the database first."


def getQueryFromLLM(model_pipeline, question, max_iteration=10):
    template = """Below is the schema of an SQLite database. Read the schema carefully, noting the table and column names. 
    Please answer the user's question by providing only the SQL query.

    {schema}

    Please provide the SQL query and nothing else.

    Example:
    Question: How many albums are in the database?
    SQL query: SELECT COUNT(*) FROM album;
    Question: How many customers are from Brazil?
    SQL query: SELECT COUNT(*) FROM customer WHERE country='Brazil';

    Your turn:
    Question: {question}
    SQL query:"""
    
    prompt = template.format(schema=getDatabaseSchema(), question=question)
    
    response = None
    for _ in range(max_iteration):
        try:
            response = model_pipeline(prompt)
            query = response[0]['generated_text']
            result = runQuery(query)
            if result:
                return query
        except Exception as error:
            print(f"Error encountered: {error}")
            prompt = f"""Previous query attempt failed with error: {error}.
                        Please try generating a different SQL query for the question: {question}.
                        Here is the database schema for reference: {getDatabaseSchema()}
                        SQL query:"""
    
    return None


def getResponseForQueryResult(model_pipeline, question, query, result):
    template = """Below is the schema of an SQLite database. Read the schema carefully, noting the table and column names. 
    Write a response in natural language based on the conversation and result.

    {schema}

    Examples:
    Question: How many albums are in the database?
    SQL query: SELECT COUNT(*) FROM album;
    Result: [(34,)]
    Response: There are 34 albums in the database.

    Question: How many users are in the database?
    SQL query: SELECT COUNT(*) FROM customer;
    Result: [(59,)]
    Response: There are 59 users in the database.

    Question: How many users from India are in the database?
    SQL query: SELECT COUNT(*) FROM customer WHERE country='India';
    Result: [(4,)]
    Response: There are 4 users from India in the database.

    Your turn to write a response in natural language:
    Question: {question}
    SQL query: {query}
    Result: {result}
    Response:"""
    
    prompt = template.format(schema=getDatabaseSchema(), question=question, query=query, result=result)
    response = model_pipeline(prompt)
    return response[0]['generated_text']


def clear_history():
    return [], "", "", ""


def chat_with_sql(question, database, model_name, chat_history):
    if not database:
        return chat_history, "", "Please connect to a database first."

    chat_history.append(("user", question))

    try:
        print("Connecting to the database...")
        connectDatabase(url=database)
        print("Database connected.")

        print(f"Loading model: {model_name}...")
        model_pipeline = pipeline("text-generation", model=model_name)
        print("Model loaded.")

        print(f"Generating query from LLM for question: {question}")
        query = getQueryFromLLM(model_pipeline, question)
        print(f"Generated query: {query}")

        print("Running query on the database...")
        result = runQuery(query)
        print(f"Query result: {result}")

        print("Generating response based on query result...")
        response = getResponseForQueryResult(model_pipeline, question, query, result)
        print(f"Response: {response}")

        chat_history.append(("assistant", response))

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        chat_history.append(("assistant", error_message))

    return chat_history, "", ""


# Initialize Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# Chat with SQL DB 🤖")

    with gr.Row():
        database = gr.Textbox(label="Database", placeholder="ex: https://raw.githubusercontent.com/....sql")
        model = gr.Dropdown(choices=["meta-llama/Meta-Llama-3.1-70B"], label="Model", value="meta-llama/Meta-Llama-3.1-70B")

    chat_history = []

    question = gr.Textbox(label="Chat with an SQL database", placeholder="Enter your question here...")

    with gr.Row():
        connect_btn = gr.Button("Connect")
        clear_btn = gr.Button("Clear message history")

    chat_output = gr.Chatbot(height=400)

    def submit_callback(question, database, model_name):
        return chat_with_sql(question, database, model_name, chat_history)

    question.submit(submit_callback, inputs=[question, database, model], outputs=[chat_output, question, database])
    connect_btn.click(submit_callback, inputs=[question, database, model], outputs=[chat_output, question, database])
    clear_btn.click(clear_history, inputs=None, outputs=[chat_output, question, database, model])


if __name__ == "__main__":
    demo.launch()
