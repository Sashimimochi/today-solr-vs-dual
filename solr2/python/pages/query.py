import streamlit as st
from request import BasicSearcher
import response
from config import *

if 'b_searcher' not in st.session_state:
    st.session_state.b_searcher = BasicSearcher()

def solr_params():
    vector_field = st.selectbox('vector field', ('q', 'fq', 'rqq'))
    q = st.text_input('q', value='*:*', help='メインクエリ')
    fq = st.text_input('fq', help='フィルタークエリ')
    rqq = st.text_input('rqq', help='リランキングクエリ')
    sort = st.text_input('sort', help='ソート')
    fl = st.text_input('fl', help='返却フィールド')
    start = st.number_input('start', min_value=0, value=0, step=1, help='開始位置')
    rows = st.number_input('rows', min_value=0, value=10, step=1, help='返却行数')
    raw = st.text_input('raw', help='生クエリ。変数と値は=でつないでください。また、複数の変数を渡すときは&でつないでください。')
    return {'q': q, 'fq': fq, 'rqq': rqq, 'sort': sort, 'fl': fl, 'start': start, 'rows': rows}, raw

def main():
    st.title('Detail Query Page')
    collection = st.selectbox('Select Collection', COLLECTION.keys())
    params, raw = solr_params()

    if st.button(label=':mag: Search'):
        if raw:
            try: 
                params.update({p.split('=')[0]: p.split('=')[1] for p in raw.split('&')})
            except IndexError:
                raise ValueError('rawでは、変数と値は=でつないでください。また、複数の変数を渡すときは&でつないでください。')
        resp = st.session_state.b_searcher.search(collection, params)
        response.make_response(collection, resp)

if __name__ == '__main__':
    main()