import pyaudio as pa
import webrtcvad 

# https://pypi.org/project/webrtcvad-wheels/
# sample_rateは 8000, 16000, 32000 or 48000 Hzのいずれか
RATE=16000
# duration timeは10, 20, 30 msのいずれか
BUFFER_SIZE=320 # RATE/BUFFER_SIZE/100

class GOOGLE_WEBRTC():

    def __init__(self):

        ## ストリーム準備
        self.audio = pa.PyAudio()
        self.stream = self.audio.open( 
            rate=RATE,
            channels=1,
            format=pa.paInt16,
            input=True,
            frames_per_buffer=BUFFER_SIZE
        )

        if self.stream == None:
            raise EnvironmentError("audio streamが開けませんでした")

        # 無音区間検出
        
        self.vad = webrtcvad.Vad(2)#1~3まで指定できます。値が大きいほど敏感に認識するのでノイズが混ざる可能性があります。環境音が周りから入る環境なら2などに設定しても良いかも知れません。
        self.thread_alive = True

    def vad_loop(self, callback):
        self.before_result = False
        while self.thread_alive:
            ## ストリームからデータを取得
            audio_data = self.stream.read(BUFFER_SIZE, exception_on_overflow = False)
            vad_result = self.vad.is_speech(audio_data, RATE)
            if vad_result != self.before_result:
                if callback != None:
                    callback(vad_result)
                self.before_result = vad_result

    def shutdown(self):
        self.thread_alive = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()