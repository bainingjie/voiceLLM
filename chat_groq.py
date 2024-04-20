from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
# Groq API key
groq_api_key = "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"

# Fixed model name and memory length
model_name = "llama3-70b-8192"
conversational_memory_length = 5

# Initialize memory
memory = ConversationBufferWindowMemory(k=conversational_memory_length)

# Initialize Groq Langchain chat object with fixed model
groq_chat = ChatGroq(
    groq_api_key=groq_api_key, 
    model_name=model_name
)

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template='''
    貴方は愉快な会話できる友達です。毎度の回答はなるべく45文字以内に抑えてください。返答は、質問と同じ言語を使ってください。
    Current conversation:
    {history}
    Human: {input}
    AI Assistant:"""
    '''
)
# Initialize conversation with memory
conversation = ConversationChain(
    llm=groq_chat,
    prompt=prompt,
    memory=memory
)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break
    response = conversation.invoke(user_input)  # Updated method call based on deprecation warning
    print("Chatbot:", response['response'])
