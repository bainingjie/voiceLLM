import pyaudio as pa
import webrtcvad 

# https://pypi.org/project/webrtcvad-wheels/
# sample_rateは 8000, 16000, 32000 or 48000 Hzのいずれか
RATE=16000
# duration timeは10, 20, 30 msのいずれか
FRAME_DURATION=10

# BUFFER_SIZE=int(RATE/FRAME_DURATION/100) # RATE/BUFFER_SIZE/100
BUFFER_SIZE=160
# COLLECTION_LENGTH=100
# SWITCH_LENGTH=70

COLLECTION_LENGTH=100
SWITCH_LENGTH=60

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

        self.vad_collection=[0 for _ in range(COLLECTION_LENGTH)]
        print("-SWITCH_LENGTH-1",-SWITCH_LENGTH-1)

    def vad_loop(self, callback):
        self.before_result = False
        while self.thread_alive:
            ## ストリームからデータを取得
            audio_data = self.stream.read(BUFFER_SIZE, exception_on_overflow = False)
            vad_result = self.vad.is_speech(audio_data, RATE)
            self.vad_collection = self.vad_collection[1:] + [vad_result]
            switch_sum= 0
            for each in self.vad_collection[(-SWITCH_LENGTH):]:
                if  each :
                    flag += 1
                else:
                    flag = 0
                if flag == 3:
                    switch_sum += 1
            # print(self.vad_collection,switch_sum,self.vad_collection[(-SWITCH_LENGTH-1)])
            if switch_sum < 1 and self.vad_collection[(-SWITCH_LENGTH-1)] :
                # print(self.vad_collection,switch_sum,self.vad_collection[(-SWITCH_LENGTH-1)])
                if callback != None:
                    # print("call back called")
                    callback(vad_result)
            elif not self.vad_collection[-4] and self.vad_collection[-3] and self.vad_collection[-2] and self.vad_collection[-1]:
                if callback != None:
                    print("cleared called to")
                    callback(vad_result)


    def shutdown(self):
        self.thread_alive = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()