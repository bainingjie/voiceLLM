from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
conversational_memory_length = 5

# Initialize memory
memory = ConversationBufferWindowMemory(k=conversational_memory_length)
from dotenv import load_dotenv
import os
claude_api_key = os.getenv('ANTHROPIC_API_KEY')
# Initialize Groq Langchain chat object with fixed model


chat = ChatAnthropic(temperature=0, api_key=claude_api_key, model_name="claude-3-opus-20240229")

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
    llm=chat,
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
