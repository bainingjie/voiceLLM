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



def speech_synthesis_to_audio_data_stream():
    """performs speech synthesis and gets the audio data from single request based stream."""
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription="252ced039853473b8acd8e525a7cf279", region="japaneast")
    # Creates a speech synthesizer with a null output stream.
    # This means the audio output data will not be written to any output channel.
    # You can just get the audio from the result.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # Receives a text from console input and synthesizes it to result.
    while True:
        print("Enter some text that you want to synthesize, Ctrl-Z to exit")
        try:
            text = input()
        except EOFError:
            break
        result = speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
            audio_data_stream = speechsdk.AudioDataStream(result)

            # You can save all the data in the audio data stream to a file
            file_name = "outputaudio.wav"
            audio_data_stream.save_to_wav_file(file_name)
            print("Audio data for text [{}] was saved to [{}]".format(text, file_name))

            # You can also read data from audio data stream and process it in memory
            # Reset the stream position to the beginning since saving to file puts the position to end.
            audio_data_stream.position = 0

            # Reads data from the stream
            audio_buffer = bytes(16000)
            total_size = 0
            filled_size = audio_data_stream.read_data(audio_buffer)
            while filled_size > 0:
                print("{} bytes received.".format(filled_size))
                total_size += filled_size
                filled_size = audio_data_stream.read_data(audio_buffer)
            print("Totally {} bytes received for text [{}].".format(total_size, text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))


speech_synthesis_to_audio_data_stream()