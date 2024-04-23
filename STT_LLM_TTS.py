import os
import copy
import threading
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.callbacks.base import BaseCallbackHandler
import sys
from prompt import *
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()
claude_api_key = os.getenv('ANTHROPIC_API_KEY')
AZURE_API_KEY = os.getenv('AZURE_API_KEY')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Constants
MODEL_NAME = "llama3-70b-8192"

# Ensure Azure Speech SDK is available
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("Failed to import Azure Speech SDK. Please install as per the documentation.")
    sys.exit(1)

def init_llm():
    """Initializes the language model and conversation chain."""
    memory = ConversationBufferMemory(return_messages=True)
    chat = ChatAnthropic(temperature=0, api_key=claude_api_key, model_name="claude-3-haiku-20240307",    
    streaming=True,callback_manager=AsyncCallbackManager([MyCustomCallbackHandler()]))
    # chat = ChatGroq(api_key=GROQ_API_KEY, model_name=MODEL_NAME, streaming=True,
    #                 callback_manager=AsyncCallbackManager([MyCustomCallbackHandler()]))
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    conversation = ConversationChain(llm=chat, prompt=prompt, memory=memory)
    return conversation

class MyCustomCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for processing new tokens."""
    def __init__(self):
        self.temp = ""

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        self.temp += token
        for split_word in ["、", "。", "?", "!"]:
            if split_word in self.temp:
                print(self.temp)
                temp2 = copy.deepcopy(self.temp)
                self.temp = ""
                speech_synthesis_with_auto_language_detection_to_speaker(temp2)

def speech_synthesis_init():
    """Initializes speech synthesis with auto language detection."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region="japaneast")
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig()
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)
    return speech_synthesizer

def speech_synthesis_with_auto_language_detection_to_speaker(text):
    """Performs speech synthesis with auto language detection."""
    global speech_synthesizer
    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
    elif result.reason == speechsdk.ResultReason.Canceled:
        print(f"Speech synthesis canceled: {result.cancellation_details.reason}")

def send_to_llm(text):
    """Sends text to the language model and synthesizes the response."""
    global conversation
    response = conversation.invoke(text)
    print("Chatbot:", response['response'])

def speech_recognize_continuous_async_from_microphone():
    """Performs continuous speech recognition with microphone input."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region="japaneast")
    speech_config.speech_recognition_language = "ja-JP"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    done = False

    def recognizing_cb(evt):
        global latest_user_utterance
        latest_user_utterance = evt.result.text
        print('RECOGNIZING:', evt)

    def recognized_cb(evt):
        global latest_user_utterance
        latest_user_utterance = evt.result.text
        print('RECOGNIZED:', evt)
        if latest_user_utterance:
            threading.Thread(target=send_to_llm, args=(latest_user_utterance,)).start()

    def stop_cb(evt):
        nonlocal done
        done = True
        print('CLOSING:', evt)

    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    speech_recognizer.start_continuous_recognition_async().get()
    print('Continuous Recognition started. Say something.')

    while not done:
        if input('Type "stop" to end: ').lower() == "stop":
            speech_recognizer.stop_continuous_recognition_async()
            break

    print("Recognition stopped.")

# Initialize global variables

latest_user_utterance = None
conversation = init_llm()
speech_synthesizer = speech_synthesis_init()

speech_synthesis_with_auto_language_detection_to_speaker(greeting_message)
speech_recognize_continuous_async_from_microphone()
