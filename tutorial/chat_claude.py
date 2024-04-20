from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
conversational_memory_length = 5

# Initialize memory
memory = ConversationBufferWindowMemory(k=conversational_memory_length)

# Initialize Groq Langchain chat object with fixed model


chat = ChatAnthropic(temperature=0, api_key="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", model_name="claude-3-opus-20240229")

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
