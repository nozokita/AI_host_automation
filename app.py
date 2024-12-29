import streamlit as st
import requests
import json

class VoiceVoxTTS:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port
        try:
            self.speakers = self.get_speakers()
        except requests.exceptions.ConnectionError:
            self.speakers = None
            st.error("VOICEVOXを起動してください")
    
    def get_speakers(self):
        response = requests.get(f"http://{self.host}:{self.port}/speakers")
        response.raise_for_status()
        return response.json()
    
    def create_audio_query(self, text, speaker_id):
        params = {"text": text, "speaker": speaker_id}
        response = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def synthesis(self, audio_query, speaker_id):
        params = {"speaker": speaker_id}
        response = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(audio_query)
        )
        response.raise_for_status()
        return response.content

def main():
    st.title("イベント司会アプリ")
    
    if 'tts_engine' not in st.session_state:
        st.session_state.tts_engine = VoiceVoxTTS()

    if not st.session_state.tts_engine.speakers:
        return

    # 話者選択
    speaker_options = {}
    for speaker in st.session_state.tts_engine.speakers:
        for style in speaker["styles"]:
            name = f"{speaker['name']} ({style['name']})"
            speaker_options[name] = style["id"]

    selected_speaker = st.selectbox("話者を選択", options=list(speaker_options.keys()))

    # 話速のみ設定
    speed = st.slider("話速", 0.8, 1.2, 1.0, 0.1)

    # テキスト入力
    text = st.text_area("テキストを入力", height=200)

    # 音声合成実行
    if st.button("音声合成"):
        if not text:
            st.warning("テキストを入力してください")
            return

        try:
            with st.spinner("音声を生成中..."):
                audio_query = st.session_state.tts_engine.create_audio_query(
                    text,
                    speaker_options[selected_speaker]
                )

                if speed != 1.0:
                    audio_query["speedScale"] = speed
                
                audio_data = st.session_state.tts_engine.synthesis(
                    audio_query,
                    speaker_options[selected_speaker]
                )
                
                st.audio(audio_data, format='audio/wav')

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
# streamlit run app.py

"""
それでは、定刻となりましたので。
ただいまから「技術開発成果報告会」を開催いたします。

本日は、お忙しいなか、ご参加いただき。
誠にありがとうございます。

私は、本日の司会を務めさせていただきます。
最後まで、どうぞよろしくお願いいたします。
"""