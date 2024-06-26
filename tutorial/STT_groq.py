import os
import azure.cognitiveservices.speech as speechsdk

from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

# Groq API key
groq_api_key = "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"

# Fixed model name and memory length
model_name = "llama3-70b-8192"
conversational_memory_length = 5



def send_to_groq(text):
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


    response = conversation.invoke(text)  # Updated method call based on deprecation warning
    print("Chatbot:", response['response'])
    
def speech_recognize_continuous_async_from_microphone():
    """performs continuous speech recognition asynchronously with input from microphone"""
    speech_config = speechsdk.SpeechConfig(subscription="252ced039853473b8acd8e525a7cf279", region="japaneast")
    # The default language is "en-us".
    
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["ja-JP", "en-US"])
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,auto_detect_source_language_config=auto_detect_source_language_config)
    done = False

    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZING: {}'.format())
        print("hahaha")
    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZED: {}'.format(evt))
        send_to_groq(evt.result.text)



    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition"""
        print('CLOSING on {}'.format(evt))
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



speech_recognize_continuous_async_from_microphone()


