import math
import streamlit as st
from config import *

def make_response(collection, resp):
    result_type = COLLECTION.get(collection).get('result_type')
    if result_type == "text":
        make_text_response(resp)
    elif result_type == "image":
        make_img_response(resp)
    else:
        raise ValueError(f"Unknown collection {collection}")

def make_text_response(resp):
    st.header('Result')
    res = {
        'QTime': f'{resp.qtime}ms',
        'numFound': resp.hits,
        'docs': resp.docs
    }
    return st.json(res)

def make_img_response(resp):
    st.header('Result')
    res = {
        "QTime": f'{resp.qtime}ms',
        "numFound": resp.hits
    }
    st.json(res)
    docs = resp.docs
    col_size = 2
    row_size = math.ceil(len(docs)/col_size)
    cols = [st.columns(col_size) for i in range(row_size)]
    
    for i, doc in enumerate(docs):
        row = i // col_size
        col = i % col_size
        with cols[row][col]:
            st.image(doc.get('filepath'), caption=f"No.{doc.get('id')}, Score:{doc.get('score')}", use_column_width=True)
