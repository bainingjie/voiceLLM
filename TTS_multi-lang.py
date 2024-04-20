import os
import azure.cognitiveservices.speech as speechsdk

def speech_synthesis_with_auto_language_detection_to_speaker():
    """performs speech synthesis to the default speaker with auto language detection
       Note: this is a preview feature, which might be updated in future versions."""
    speech_config = speechsdk.SpeechConfig(subscription="252ced039853473b8acd8e525a7cf279", region="japaneast")

    # create the auto-detection language configuration without specific languages
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig()

    # Creates a speech synthesizer using the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)

    while True:
        # Receives a text from console input and synthesizes it to speaker.
        # For example, you can input "Bonjour le monde. Hello world.", then you will hear "Bonjour le monde."
        # spoken in a French voice and "Hello world." in an English voice.
        print("Enter some multi lingual text that you want to speak, Ctrl-Z to exit")
        try:
            text = input()
        except EOFError:
            break
        result = speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
speech_synthesis_with_auto_language_detection_to_speaker()