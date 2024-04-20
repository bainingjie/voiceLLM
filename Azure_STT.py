import os
import azure.cognitiveservices.speech as speechsdk

def recognize_from_microphone_continuously():
    # Fetch the Azure Speech service subscription info from environment variables
    speech_key = os.environ.get("SPEECH_KEY", "252ced039853473b8acd8e525a7cf279")
    speech_region = os.environ.get("SPEECH_REGION", "japaneast")

    # Initialize speech config
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = "ja-JP"

    # Setup the audio configuration to use the default microphone
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    # Create a speech recognizer with the given settings
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def recognized_cb(event):
        print("Recognized: {}".format(event.result.text))

    def canceled_cb(event):
        print("Speech Recognition canceled: {}".format(event.reason))
        if event.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(event.error_details))

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.canceled.connect(canceled_cb)

    # Start continuous speech recognition
    print("Speak into your microphone.")
    speech_recognizer.start_continuous_recognition()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Recognition stopped.")
        speech_recognizer.stop_continuous_recognition()

recognize_from_microphone_continuously()
