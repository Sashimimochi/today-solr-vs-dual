import streamlit as st
from vectorizer.clip_vectorizer import Vectorizer as cv
from vectorizer.w2v_vectorizer import Vectorizer as wv
from vectorizer.mobnet_vectorizer import Vectorizer as mv

class Vectorizer:
    def __init__(self) -> None:
        if 'clip' not in st.session_state:
            st.session_state.clip = cv()
        self.clip = st.session_state.clip
        if 'w2v' not in st.session_state:
            st.session_state.w2v = wv()
        self.w2v = st.session_state.w2v
        if 'mobnet' not in st.session_state:
            st.session_state.mobnet = mv()
        self.mobnet = st.session_state.mobnet

    def get_text_vector(self, model, text):
        if model == 'w2v':
            return self.w2v.text_vectorize(text).tolist()
        else:
            return self.clip.text_vectorize(text).tolist()[0]

    def get_img_vector(self, model, img):
        if model == 'mobnet':
            return self.mobnet.img_vectorize(img).tolist()[0]
        else:
            return self.clip.img_vectorize(img).tolist()[0]
