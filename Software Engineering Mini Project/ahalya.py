import streamlit as st
import pandas as pd
st.title("Sub Page")
df=pd.read_csv("C:\\Users\\keert\\OneDrive\\Desktop\\templates\\Indian_cities.csv")
l1=["None","Temperature","Humidity","Wind Speed","Precipitation"]
city=st.selectbox("Select Location",[city for city in df])
year=st.selectbox("Select year",[year for year in range(2013,2023)])
p1=st.selectbox("Seelct Parameter1",l1)
p2=st.selectbox("Seelct Parameter2",l1)
p3=st.selectbox("Seelct Parameter3",l1)
p4=st.selectbox("Seelct Parameter4",l1)
submitted=st.button("Submit")

