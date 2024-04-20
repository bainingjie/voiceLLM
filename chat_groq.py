from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

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

# Initialize conversation with memory
conversation = ConversationChain(
    llm=groq_chat,
    memory=memory
)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break
    response = conversation.invoke(user_input)  # Updated method call based on deprecation warning
    print("Chatbot:", response['response'])
