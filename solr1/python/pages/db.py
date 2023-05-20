import streamlit as st
from mysql import MySQLClient
from config import *

def main():
    st.title('Check Data in Database')
    client = MySQLClient()

    rows = st.number_input('select rows', min_value=1, value=5, step=1)
    if st.button(label=':dvd: Select from Database'):
        st.header('Result')
        st.write(client.select(rows))

    st.write('You can select tables from below')
    st.write(TABLES)

    query = st.text_area('input query here', placeholder='select * from lcc limit 1')
    if st.button(':dvd: Select by query'):
        st.header('Result')
        st.write(client.select_with_query(query))

if __name__ == '__main__':
    main()