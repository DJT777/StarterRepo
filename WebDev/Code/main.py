
import sys

from flask import Flask, request, jsonify, render_template, send_from_directory
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import openai
from flask_cors import CORS
from nemoguardrails import LLMRails, RailsConfig
import os
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQA

#Get our API Key
openai.api_key = os.environ["OPENAI_API_KEY"]

#Load our app
app = Flask(__name__)

#allow for cross-site scripting
CORS(app, resources={r"/chat": {"origins": "*"}})

#define our embedding model
embedding = OpenAIEmbeddings()

#We can load the persisted database from disk, and use it as normal.
#vectordb = Chroma(persist_directory="db", embedding_function=embedding)


#GUARDRAILS CONTENT
yaml_content = """
models:
- type: main
  engine: openai
  model: text-davinci-003
  
- type: embeddings
  engine: openai
  model: text-embedding-ada-002
"""

#GUARDRAILS CONTENT
colang_content = """
define user express greeting
    "hello"
    "hi"
    "what's up?"

define flow greeting
    user express greeting
    bot express greeting
    bot ask how are you

# define limits
define user ask politics
    "what are your political beliefs?"
    "thoughts on the president?"
    "left wing"
    "right wing"

define bot answer politics
    "I'm here to help you with questions about USI, I don't like to talk of politics."

define flow politics
    user ask politics
    bot answer politics
    bot offer help

define flow
    user ...
    $answer = execute get_response(user_input=$last_user_message)
    bot $answer
"""

# initialize rails config
config = RailsConfig.from_content(
  	yaml_content=yaml_content,
    colang_content=colang_content
)
appRails = LLMRails(config)

#these are language chains with guardrails used to define the prompting structure.
llm = ChatOpenAI(temperature=0,model_name="gpt-4")
'''#qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectordb.as_retriever())

#qa_chain_retrival = RetrievalQA.from_chain_type(
    llm=appRails.llm, retriever=vectordb.as_retriever()
)
qa_chain_retrival_no_rails = RetrievalQA.from_chain_type(
    llm=llm, retriever=vectordb.as_retriever()
)'''


#function used to get responses using guardrails
def qa_chain_answer(query):
    ###history = ""
    ###input_dict = {"question": query, "chat_history": history}
    history = [
        {"role": "user", "content": query}
    ]
    result = appRails.generate(messages=history)
    print(result)
    response = result['content']
    return response

#our raw response functions without any rails or data augmentation
def get_response(user_input):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    response = completion['choices'][0]['message']['content']
    print(response)
    return response

appRails.register_action(get_response)
#appRails.register_action(qa_chain, name="qa_chain")
#appRails.register_action(qa_chain_answer, name="qa_chain_answer")



#gets the icon for display
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'static/Icons/favicon.ico')

#serves the main page
@app.route('/')
def index():
    return render_template('ChatBot.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    #Raw GPT with no Rails, no Data Augmentation

    #completion = qa_chain({"question": user_input, "chat_history": ""})
    #print(completion)

    #QA Retrieval Chain With No Rails
    #retrieval = qa_chain_retrival_no_rails({"query": user_input})
    #response = retrieval['result']

    #Talking to GPT with rails in place
    #response = completion['answer']
    #completion = appRails.generate(messages=[{
    #    "role": "user",
    #    "content": user_input
    #}])
    #print(completion)

    user_input = request.json.get('input')
    print("USER INPUT: " + user_input)
    response = get_response(user_input)

    print("RESPONSE: " + response)
    return jsonify({"response": response})



#run our application
if __name__ == '__main__':
    app.run(debug=True)
