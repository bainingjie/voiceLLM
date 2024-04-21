import os
import azure.cognitiveservices.speech as speechsdk
import vad_collection as vad
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory,ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import threading,time
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os


# .envファイルを読み込む
load_dotenv()

# 環境変数を取得する
claude_api_key = os.getenv('ANTHROPIC_API_KEY')
AZURE_API_KEY = os.getenv('AZURE_API_KEY')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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

def speech_synthesis_init():
    """performs speech synthesis to the default speaker with auto language detection
       Note: this is a preview feature, which might be updated in future versions."""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_API_KEY, region="japaneast")

    # create the auto-detection language configuration without specific languages
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig()

    # Creates a speech synthesizer using the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)
    return speech_synthesizer

def speech_synthesis_with_auto_language_detection_to_speaker(text):

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
def init_llm():
    # Initialize memory
    memory = ConversationBufferMemory(return_messages=True)

    # Initialize Groq Langchain chat object with fixed model

    chat = ChatAnthropic(temperature=0, api_key=claude_api_key, model_name="claude-3-haiku-20240307")
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

def send_to_llm(text):
    global is_sentenct_spelled
    global conversation
    is_sentenct_spelled=True

    response = conversation.invoke(text)  # Updated method call based on deprecation warning
    print("Chatbot:", response['response'])

    thread=threading.Thread(target=speech_synthesis_with_auto_language_detection_to_speaker, args=(response['response'], ))
    thread.start()
    thread.join()
    
def speech_recognize_continuous_async_from_microphone():
    """performs continuous speech recognition asynchronously with input from microphone"""
    speech_config = speechsdk.SpeechConfig(subscription="252ced039853473b8acd8e525a7cf279", region="japaneast")
    # The default language is "en-us".
    
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["ja-JP", "en-US"])
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,auto_detect_source_language_config=auto_detect_source_language_config)
    done = False
    global is_sentenct_spelled

    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        global latest_user_utterance
        latest_user_utterance=evt.result.text
        # latest_user_utterance=send_to_groq(evt.result.text)
        print('RECOGNIZING: {}'.format(evt))

    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        print('RECOGNIZED: {}'.format(evt))
        global latest_user_utterance,is_sentenct_spelled
        latest_user_utterance=evt.result.text
        if is_sentenct_spelled == False and latest_user_utterance:
            if len(latest_user_utterance)>1:
                thread=threading.Thread(target=send_to_llm, args=(latest_user_utterance, ))
                thread.start()
                thread.join()
        # latest_user_utterance=send_to_groq(evt.result.text)
            

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

# マイク音声の終わりをより俊敏に検知するためのvad
def callback_vad(flag):
    # print("vad", flag)
    global latest_user_utterance,is_sentenct_spelled
    if flag == True: #SPEAKING
        latest_user_utterance = None
        is_sentenct_spelled=False
    elif latest_user_utterance != None: #SPEAKING DONE
        if not is_sentenct_spelled and  len(latest_user_utterance)>1:
            print("sent to groq")
            print(latest_user_utterance)
            thread=threading.Thread(target=send_to_llm, args=(latest_user_utterance, ))
            thread.start()
            thread.join()

global latest_user_utterance
global is_sentenct_spelled
global conversation,speech_synthesizer
global system_promt


greeting_message=": リッツカールトン東京でございます。本日はお電話いただきまして誠にありがとうございます。本日はどのようなご用件でしょうか。"
system_promt='''

貴方はリッツカールトン東京の顧客サポート担当です。下記のscriptを参考にして、お客様の質問に答えてください。毎度の回答はなるべく45文字以内に抑えてください。

お客様: 今週金曜日に1泊で宿泊予約をしたいのですが、空室はありますか?

ホテルスタッフ: ありがとうございます。少々お待ちください。金曜日のご宿泊でございますね。お調べいたしますので、今しばらくお待ちくださいませ。
(少し待ってから)只今確認いたしましたところ、金曜日は空室がございます。ご予約を承らせていただきます。お客様のお名前と連絡先をお教えいただけますでしょうか。

お客様: 山田太郎です。電話番号は090-1234-5678です。

ホテルスタッフ: 山田太郎様、承知いたしました。ご連絡先は090-1234-5678ですね。ご宿泊は金曜日のお一泊で、4月19日でございます。お部屋のタイプやご要望はございますでしょうか。

お客様: 禁煙のツインルームでお願いします。あと、レイトチェックアウトは可能ですか?

ホテルスタッフ: 禁煙のツインルームですね。かしこまりました。レイトチェックアウトにつきましては、通常12時のところを14時まで無料で延長させていただきます。朝食のご希望はいかがいたしましょうか。

お客様: それは助かります。朝食はルームサービスでお願いできますか。

ホテルスタッフ: はい、朝食はルームサービスでも承っております。ご希望の時間帯がございましたら事前にお知らせくださいませ。山田様、ご予約内容を確認させていただきます。金曜日4月19日のお一泊、禁煙ツインルームにてレイトチェックアウト14時まで、朝食はルームサービスでのご用命ですね。

お客様: はい、その通りです。

ホテルスタッフ: ご予約ありがとうございます。当日はお気をつけてお越しくださいませ。ご宿泊を心よりお待ち申し上げております。リッツカールトン東京のでした。本日はお電話いただき誠にありがとうございました。

'''

latest_user_utterance = None
is_sentenct_spelled=False
vad = vad.GOOGLE_WEBRTC()
conversation = init_llm()
speech_synthesizer=speech_synthesis_init()
speech_synthesis_with_auto_language_detection_to_speaker(greeting_message)
mic_thread = threading.Thread(target=speech_recognize_continuous_async_from_microphone)
vad_thread = threading.Thread(target=vad.vad_loop, args=(callback_vad, ))
mic_thread.start()
vad_thread.start()


mic_thread.join()
vad_thread.join()
