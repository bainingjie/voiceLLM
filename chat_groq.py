from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chat = ChatGroq(temperature=0, groq_api_key="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", model_name="llama3-70b-8192")
prompt = ChatPromptTemplate.from_messages([("human", "Write a haiku about {topic}")])
chain = prompt | chat
for chunk in chain.stream({"topic": "The Moon"}):
    print(chunk.content, end="", flush=True)