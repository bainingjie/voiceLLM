import os
import azure.cognitiveservices.speech as speechsdk
import vad_collection as vad
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory,ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager
import threading,time
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os,copy

from prompt import * 


# .envファイルを読み込む
load_dotenv()

# 環境変数を取得する
claude_api_key = os.getenv('ANTHROPIC_API_KEY')
AZURE_API_KEY = os.getenv('AZURE_API_KEY')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Fixed model name and memory length
model_name = "llama3-70b-8192"
conversational_memory_length = 5

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-text-to-speech-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)

def init_llm():
    # Initialize memory
    memory = ConversationBufferMemory(return_messages=True)

    # Initialize Groq Langchain chat object with fixed model

    chat = ChatAnthropic(temperature=0, api_key=claude_api_key, model_name="claude-3-haiku-20240307",    
    streaming=True,callback_manager=AsyncCallbackManager([MyCustomCallbackHandler()]))
    # chat = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-70b-8192")

    prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_promt),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")])
    # Initialize conversation with memory
    conversation = ConversationChain(
        llm=chat,
        prompt=prompt,
        memory=memory
    )

    return conversation

class MyCustomCallbackHandler(BaseCallbackHandler):    
    def __init__(self):
        self.temp = ""

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        '''新しいtokenが来たらprintする'''
        self.temp = self.temp + token
        
        for split_word in ["、","。", "?", "!"]:
            if split_word in self.temp:
                print(self.temp)
                temp2=copy.deepcopy(self.temp)
                self.temp = ""
                speech_synthesis_with_auto_language_detection_to_speaker(temp2)
                


def speech_synthesis_init():
    """performs speech synthesis to the default speaker with auto language detection
       Note: this is a preview feature, which might be updated in future versions."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region="japaneast")
    # speech_config.speech_synthesis_voice_name ="en-US-AvaMultilingualNeural"
    # create the auto-detection language configuration without specific languages
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig()

    # Creates a speech synthesizer using the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)
    return speech_synthesizer

def speech_synthesis_with_auto_language_detection_to_speaker(text):
    print("start to synthesize")
    global speech_synthesizer
    # while True:
        # Receives a text from console input and synthesizes it to speaker.
        # For example, you can input "Bonjour le monde. Hello world.", then you will hear "Bonjour le monde."
        # spoken in a French voice and "Hello world." in an English voice.
        # print("Enter some multi lingual text that you want to speak, Ctrl-Z to exit")
    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized to speaker for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)


def send_to_llm(text):

    global conversation
    
    print("start to send text to LLM")
    response = conversation.invoke(text)  # Updated method call based on deprecation warning
    print("Chatbot:", response['response'])

    # thread=threading.Thread(target=speech_synthesis_with_auto_language_detection_to_speaker, args=(response['response'], ))
    # thread.start()
    # thread.join()


def speech_recognize_continuous_async_from_microphone():
    """performs continuous speech recognition asynchronously with input from microphone"""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region="japaneast")
    # The default language is "en-us".
    speech_config.speech_recognition_language="ja-JP"

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    # auto_detect_source_language_config = \
    #     speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["ja-JP", "en-US"])
    # speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,auto_detect_source_language_config=auto_detect_source_language_config)

    done = False

    print("trascriber initialized")
    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        global latest_user_utterance
        latest_user_utterance=evt.result.text
        # latest_user_utterance=send_to_groq(evt.result.text)
        print('RECOGNIZING: {}'.format(evt))


    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZED: {}'.format(evt))
        global latest_user_utterance,sentence_spoken_count,sentence_processed_count,is_vad_before
        latest_user_utterance=evt.result.text
        
        print(sentence_spoken_count,sentence_processed_count,is_vad_before)
        if len(latest_user_utterance)>0:
            sentence_spoken_count += 1
        
        if sentence_spoken_count>sentence_processed_count and latest_user_utterance:
            if len(latest_user_utterance)>1:
                is_vad_before = 0
                
                sentence_processed_count +=1
                print("thread llm from cb")
                print(latest_user_utterance)
                thread=threading.Thread(target=send_to_llm, args=(latest_user_utterance, ))
                thread.start()
                # thread.join()



    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition"""
        print('CLOSING on {}'.format(evt))
        print(evt)
        nonlocal done
        done = True


    # Connect callbacks to the events fired by the speech recognizer
    # 
    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Perform recognition. `start_continuous_recognition_async asynchronously initiates continuous recognition operation,
    # Other tasks can be performed on this thread while recognition starts...
    # wait on result_future.get() to know when initialization is done.
    # Call stop_continuous_recognition_async() to stop recognition.
    result_future = speech_recognizer.start_continuous_recognition_async()

    result_future.get()  # wait for voidfuture, so we know engine initialization is done.
    print('Continuous Recognition is now running, say something.')

    while not done:
        # No real sample parallel work to do on this thread, so just wait for user to type stop.
        # Can't exit function or speech_recognizer will go out of scope and be destroyed while running.
        print('type "stop" then enter when done')
        stop = input()
        if (stop.lower() == "stop"):
            print('Stopping async recognition.')
            speech_recognizer.stop_continuous_recognition_async()
            break

    print("recognition stopped, main thread can exit now.")

# マイク音声の終わりをより俊敏に検知するためのvad
def callback_vad(flag):
    # print("vad", flag)
    global latest_user_utterance,sentence_processed_count,sentence_spoken_count,is_vad_before
    if flag == True: #SPEAKING
        latest_user_utterance = None
        # print("is_sentenct_spelled turned FALSE ")
        # is_sentenct_spelled=False
    elif latest_user_utterance != None: #SPEAKING DONE
        if (sentence_spoken_count == sentence_processed_count) and (not is_vad_before) and len(latest_user_utterance)>1:
            # print("sent to groq")
            is_vad_before = 1
            print("thread llm from vad")
            print(sentence_spoken_count,sentence_processed_count)
            sentence_processed_count+=1
            print(latest_user_utterance)
            # print("is_sentenct_spelled turned TRUE ")
            thread=threading.Thread(target=send_to_llm, args=(latest_user_utterance, ))
            thread.start()
            # thread.join()

global latest_user_utterance
latest_user_utterance = None
global sentence_spoken_count
sentence_spoken_count=0
global sentence_processed_count
sentence_processed_count=0
global is_vad_before
is_vad_before = 0

global conversation
conversation = init_llm()
global speech_synthesizer
speech_synthesizer=speech_synthesis_init()

vad = vad.GOOGLE_WEBRTC()
speech_synthesis_with_auto_language_detection_to_speaker(greeting_message)



vad_thread = threading.Thread(target=vad.vad_loop, args=(callback_vad, ))
vad_thread.start()

speech_recognize_continuous_async_from_microphone()
# mic_thread = threading.Thread(target=speech_recognize_continuous_async_from_microphone)
# mic_thread.start()

# mic_thread.join()

vad_thread.join()
