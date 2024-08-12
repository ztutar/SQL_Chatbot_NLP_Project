import ollama
import streamlit

streamlit.title("SQL 4 Database Chatbot")

# initialize history
if "messages" not in streamlit.session_state:
    streamlit.session_state["messages"] = []
    
# initialize models
if "model" not in streamlit.session_state:
    streamlit.session_state["model"] = ""

models = [model["name"] for model in ollama.list()["models"] if model["name"] != "arr-phi:latest"]
streamlit.session_state["model"] = streamlit.selectbox("Choose a model", models)

def response_generator():
    stream = ollama.chat(
        model=streamlit.session_state["model"],
        messages=streamlit.session_state["messages"],
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]

# Display chat messages from history on app rerun
for message in streamlit.session_state["messages"]:
    with streamlit.chat_message(message["role"]):
        streamlit.markdown(message["content"])

if prompt := streamlit.chat_input("Hi! How can I help?"):
    # add latest message to history in format {role, content}
    streamlit.session_state["messages"].append({"role": "user", "content": prompt})

    with streamlit.chat_message("user"):
        streamlit.markdown(prompt)

    with streamlit.chat_message("assistant"):
        message = streamlit.write_stream(response_generator())
        streamlit.session_state["messages"].append({"role": "assistant", "content": message})
