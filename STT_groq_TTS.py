import os
import azure.cognitiveservices.speech as speechsdk

from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
# Groq API key
groq_api_key = "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"

# Fixed model name and memory length
model_name = "llama3-70b-8192"
conversational_memory_length = 5


#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
"""
Speech synthesis samples for the Microsoft Cognitive Services Speech SDK
"""

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


# Set up the subscription info for the Speech Service:
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "YourSubscriptionKey", "YourServiceRegion"



def speech_synthesis_with_auto_language_detection_to_speaker(text):
    """performs speech synthesis to the default speaker with auto language detection
       Note: this is a preview feature, which might be updated in future versions."""
    speech_config = speechsdk.SpeechConfig(subscription="252ced039853473b8acd8e525a7cf279", region="japaneast")

    # create the auto-detection language configuration without specific languages
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig()

    # Creates a speech synthesizer using the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)

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

def send_to_groq(text):
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


    response = conversation.invoke(text)  # Updated method call based on deprecation warning
    print("Chatbot:", response['response'])
    return response['response']
    
def speech_recognize_continuous_async_from_microphone():
    """performs continuous speech recognition asynchronously with input from microphone"""
    speech_config = speechsdk.SpeechConfig(subscription="252ced039853473b8acd8e525a7cf279", region="japaneast")
    # The default language is "en-us".
    
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["ja-JP", "en-US"])
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,auto_detect_source_language_config=auto_detect_source_language_config)
    done = False

    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZING: {}'.format(evt))
    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZED: {}'.format(evt))
        if len(evt.result.text)>0:
            resp=send_to_groq(evt.result.text)
            speech_synthesis_with_auto_language_detection_to_speaker(resp)



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


