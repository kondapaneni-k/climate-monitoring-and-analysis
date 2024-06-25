import streamlit as st
import pandas as pd
import replicate
import os
import folium
from streamlit_folium import st_folium
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_folium import folium_static
from statsmodels.tsa.seasonal import seasonal_decompose


st.set_page_config(page_title="User Climate Monitoring and Analysis", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")
# Read the CSV file
df_cities = pd.read_csv("Indian_cities.csv")


# Column 1: Non-clickable "Climate Pulse" title
st.markdown("<h1 style='color: #2196F3;'>Climate Pulse</h1>"
            "<h3 style='color: #333333'>Envisioning environment change - for a greener future</h3>", unsafe_allow_html=True)

def connect_to_mysql(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            return connection
    except Exception as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None


def get_years_by_location(connection, city):
    try:
        cursor = connection.cursor()
        query = f"SELECT DISTINCT YEAR(Date) AS Year FROM {city}"
        cursor.execute(query)
        years_data = cursor.fetchall()
        years_list = [year[0] for year in years_data]
        return years_list
    except Exception as e:
        st.error(f"Error fetching years: {e}")
        return []

def display_map():
    # Set the center coordinates for the map
    center = (20.5937, 78.9629)

    # Create a Folium map centered on India
    mymap = folium.Map( location=center,zoom_start=5,width="100%",height="100%",tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr='Esri.WorldImagery')


    # Add markers for each city in the DataFrame
    for index, row in df_cities.iterrows():
        location = (row['Latitude'], row['Longitude'])
        popup_text = f"{row['City']}<br>Latitude: {row['Latitude']}<br>Longitude: {row['Longitude']}"
        folium.Marker(location, popup=popup_text,
                    icon=folium.Icon(icon='globe',icon_color='blue')).add_to(mymap)

    # Display the map using Streamlit and Folium integration
    st_folium(mymap,width=1400,height=500)
    l1=['None','Temperature','Humidity','Wind Speed','Precipitation']
    with st.form("input_form"):   
        col_1, col_2 = st.columns([1,1])
        connection=connect_to_mysql('127.0.0.1','root','1114','Climate')
        if connection:

            # Query to retrieve all table names
            table_query = "SHOW TABLES"

            # Execute the queries
            cursor = connection.cursor()


            # Execute the table query
            cursor.execute(table_query)
            tables_data = cursor.fetchall()
            tables_list = [table[0] for table in tables_data]

            # Close the cursor and connection
            cursor.close()
            connection.close()

        with col_1:
            city=st.selectbox('Select a city',[city for city in tables_list])
        
            
        with col_2:
            connection = connect_to_mysql('127.0.0.1', 'root', '1114', 'Climate')
            if connection:
                years_list = get_years_by_location(connection, city)

                # Display select box for selecting a year
                year = st.selectbox('Select a year', years_list)
                
        
        st.write('Select parameters')
        col5,col6,col7,col8=st.columns([2.5,2.5,2.5,2.5])
        # Initialize empty select boxes
        selected_param1 = col5.selectbox("Parameter 1", l1)
        selected_param2 = col6.selectbox("Parameter 2", l1)
        selected_param3 = col7.selectbox("Parameter 3", l1)
        selected_param4 = col8.selectbox("Parameter 4", l1)

        submitted = st.form_submit_button("Set")
    if 'submitted_state' not in st.session_state:
        st.session_state.submitted_state=False
        
    if submitted or st.session_state.submitted_state:
        st.session_state.submitted_state=True
        connection=connect_to_mysql('127.0.0.1','root','1114','Climate')
        if connection:
            cursor=connection.cursor()
            if(selected_param1=='None' and selected_param2=='None' and selected_param3=='None'and selected_param4=='None'):
                query = f"SELECT * FROM {city} WHERE YEAR(Date) = {year}"
                cursor.execute(query)
                data=cursor.fetchall()
                df=pd.DataFrame(data,columns=cursor.column_names)
    
                # Close cursor and connection
                cursor.close()
                connection.close()

                # Convert 'Date' column to datetime format
                df['Date'] = pd.to_datetime(df['Date'])

                # Filter out the 'Date' column for plotting
                columns_to_plot = df.columns[df.columns != 'Date']

                    # Plotting using Plotly express within Streamlit
                fig = px.line(df, x='Date', y=columns_to_plot,
                            title=f'Line Graph of {city} for all parameters in {year}',
                            labels={'value': 'Value', 'variable': 'Column'},
                            hover_data={'value': ':.2f'})
                
                # Customize hover labels
                fig.update_traces(hovertemplate='%{x|%Y-%m-%d}<br>%{y:.2f}')
                fig.update_layout(width=1000, height=600)

                # Display Plotly figure in Streamlit
                st.plotly_chart(fig)
                
            elif (selected_param1 != 'None' or selected_param2 != 'None' or selected_param3 != 'None' or selected_param4 != 'None'):
                try:
                    query = f"SELECT Date, "
                    
                    selected_params = []
                    if selected_param1 != 'None':
                        query += f"`{selected_param1}`, "  # Use backticks for column names
                        selected_params.append(selected_param1)
                    if selected_param2 != 'None':
                        query += f"`{selected_param2}`, "  # Use backticks for column names
                        selected_params.append(selected_param2)
                    if selected_param3 != 'None':
                        query += f"`{selected_param3}`, "  # Use backticks for column names
                        selected_params.append(selected_param3)
                    if selected_param4 != 'None':
                        query += f"`{selected_param4}`, "  # Use backticks for column names
                        selected_params.append(selected_param4)
                    
                    query = query.rstrip(', ')  # Remove the trailing comma
                    query += f" FROM `{city}` WHERE YEAR(Date) = {year}"
                    
                    cursor.execute(query)
                    data = cursor.fetchall()
                    
                    # Create a DataFrame with selected columns and Date
                    columns = ['Date'] + selected_params
                    df = pd.DataFrame(data, columns=columns)


                    # Close cursor and connection
                    cursor.close()
                    connection.close()
                    
                    # Convert 'Date' column to datetime format
                    df['Date'] = pd.to_datetime(df['Date'])

                    # Filter out the 'Date' column for plotting
                    columns_to_plot = df.columns[df.columns != 'Date']
                    
                    column_titles=columns_to_plot.to_list()
                    
                    column_titles_str = ', '.join(column_titles)

                    opt=st.radio('Choose type of graph',['Line Graph','Bar Graph','Histogram'])
                    if opt=='Line Graph':
                        # Plotting using Plotly express within Streamlit
                        fig = px.line(df, x='Date', y=columns_to_plot,
                                    title=f'{opt} of {city} for parameters {column_titles_str} in {year}',
                                    labels={'value': 'Value', 'variable': 'Column'},
                                    hover_data={'value': ':.2f'})
                        
                        # Customize hover labels
                        fig.update_traces(hovertemplate='%{x|%Y-%m-%d}<br>%{y:.2f}')
                        fig.update_layout(width=1000, height=600)

                        # Display Plotly figure in Streamlit
                        st.plotly_chart(fig)
                    
                    elif opt=='Bar Graph':
                        for col in columns_to_plot:
                            fig = px.bar(df, x='Date', y=col, title=f'Bar Graph for {col} of {city} in {year}')
                            
                            # Customize hover labels
                            fig.update_traces(hovertemplate='%{x|%Y-%m-%d}<br>%{y:.2f}')
                            fig.update_layout(width=1000, height=600)

                            # Display Plotly figure in Streamlit
                            st.plotly_chart(fig)
                    else:
                        
                        fig = px.histogram(df, x='Date', y=columns_to_plot,
                                    title=f'{opt} of {city} for parameters {column_titles_str} in {year}',
                                    labels={'value': 'Value', 'variable': 'Column'},
                                    hover_data={'value': ':.2f'},
                                    histfunc='avg')
                        
                        # Customize hover labels
                        fig.update_traces(hovertemplate='%{x|%Y-%m-%d}<br>%{y:.2f}')
                        fig.update_layout(width=1000, height=600)

                        # Display Plotly figure in Streamlit
                        st.plotly_chart(fig)
                
                except Exception as e:
                    st.error(f"Error: Please make sure you have not selected duplicate parameters.")

                    
    
def get_data(location, parameter):
    connection = mysql.connector.connect(host='127.0.0.1', user='root', password='1114', database='Climate')
    if connection:
        query = f"SELECT `Date`, `{parameter}` FROM `{location}`"
        # Execute the queries
        cursor = connection.cursor()


        # Execute the table query
        cursor.execute(query)
        dataset_data = cursor.fetchall()
        # Get column names from the cursor description
        columns = [desc[0] for desc in cursor.description]
        
        df=pd.DataFrame(dataset_data,columns=columns)
        
        connection.close()
        return df

def pattern_detection():
    st.title('Seasonal Pattern Detection')

    connection = mysql.connector.connect(host='127.0.0.1', user='root', password='1114', database='Climate')
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables_data = cursor.fetchall()
    tables_list = [table[0] for table in tables_data]
    connection.close()

    # Select location (table name) from dropdown
    location = st.selectbox('Select Location', tables_list)

    # Select parameter (column) from dropdown
    if location:
        parameter = st.selectbox('Select Parameter', ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation'])

    if location and parameter:
        # Get data based on selection
        df = get_data(location, parameter)

        if df is not None:
            # Plot the original data
            st.subheader('Time Series Plot')
            df['Date'] = pd.to_datetime(df['Date'])  # Convert date column to datetime format
            df.set_index('Date', inplace=True)  # Set date column as index
            df.index.freq = 'D'  # Set the frequency (e.g., daily)

            fig, ax = plt.subplots(figsize=(8, 4))  # Adjust figure size here
            ax.plot(df.index, df[parameter])  # Plot the time series data
            ax.set_xlabel('Date')
            ax.set_ylabel('Value')
            ax.set_title('Time Series Data')
            st.pyplot(fig)  # Show the plot in Streamlit

            # Perform seasonal decomposition (using additive model)
            result = seasonal_decompose(df[parameter], model='additive')

            # Plot the decomposed components
            st.subheader('Seasonal Decomposition')
            fig, axs = plt.subplots(4, 1, figsize=(8, 6))

            axs[0].plot(result.trend)
            axs[0].set_title('Trend')

            axs[1].plot(result.seasonal)
            axs[1].set_title('Seasonality')

            axs[2].plot(result.resid)
            axs[2].set_title('Residual')

            axs[3].plot(result.observed)
            axs[3].set_title('Observed')

            plt.tight_layout()
            st.pyplot(fig)  # Show the plot in Streamlit


def chatbot():
    with st.sidebar:
        if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
        else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
            if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
                st.warning('Please enter your credentials!', icon='⚠️')
            else:
                st.success('Proceed to entering your prompt message!', icon='👉')
        os.environ['REPLICATE_API_TOKEN'] = replicate_api

        st.subheader('Models and parameters')
        selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
        if selected_model == 'Llama2-7B':
            llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
        elif selected_model == 'Llama2-13B':
            llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
        temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
        top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
        max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    # Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
    def generate_llama2_response(prompt_input):
        string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'. You give short and precise answers."
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                string_dialogue += "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
        output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                            input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                    "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
        return output

    # User-provided prompt
    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message) 
  
st.sidebar.header("Menu")

if "page" not in st.session_state:
    st.session_state.page = None

if st.sidebar.button("Home"):
    st.session_state.page = "home"

if st.sidebar.button("AI Assistent"):
    st.session_state.page = "aiass"

if st.sidebar.button("Pattern Detection"):
    st.session_state.page = "pattern"
    


for i in range(25):
    st.sidebar.markdown("   ")


if st.sidebar.button("Log Out", key="logout_button", help="Click here to log out"):
    st.write("You clicked Log Out")
    st.write("""
    <meta http-equiv="refresh" content="0; URL='http://127.0.0.1:5500/user-admin/user-admin.html'" />
    """, unsafe_allow_html=True)
    
if "page" in st.session_state:
    if st.session_state.page == "aiass":
        chatbot()
    elif st.session_state.page == "pattern":
        pattern_detection()
    elif st.session_state.page == "home":
        display_map()
    else:
        display_map()


    






        


    