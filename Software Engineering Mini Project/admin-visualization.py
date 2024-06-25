import streamlit as st
import pandas as pd
import folium
import replicate
import os
from streamlit_folium import st_folium
from streamlit.components.v1 import html as components_html
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_folium import folium_static

st.set_page_config(page_title="Admin Climate Monitoring and Analysis", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")
# Read the CSV file
df_cities = pd.read_csv("Indian_cities.csv")

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
        with col_1:
            city=st.selectbox('Select a city',[city for city in df_cities['City']])
        with col_2:
            year=st.selectbox('Select an year',[year for year in range(2017,2024)])
            
        st.write('Select parameters')
        col5,col6,col7,col8=st.columns([2.5,2.5,2.5,2.5])
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
                                    hover_data={'value': ':.2f'},)
                        
                        # Customize hover labels
                        fig.update_traces(hovertemplate='%{x|%Y-%m-%d}<br>%{y:.2f}')
                        fig.update_layout(width=1000, height=600)

                        # Display Plotly figure in Streamlit
                        st.plotly_chart(fig)
                
                except Exception as e:
                    st.error(f"Error: Please make sure you have not selected duplicate parameters.")
    
def add_data(city, temperature, humidity, precipitation, wind_speed, date):
    try:
        connection = connect_to_mysql('127.0.0.1', 'root', '1114', 'Climate')
        cursor = connection.cursor()
        # Insert data into database
        query = f"INSERT INTO `{city}` (Temperature, Humidity, Precipitation, `Wind Speed`, `Date`) " \
                f"VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (temperature, humidity, precipitation, wind_speed, date))
        connection.commit()
        return True, "Data added successfully"
    except Exception as e:
        return False, f"Error adding data: {e}"
    
def add_data_page():
    st.title("Add Data")

    connection = connect_to_mysql('127.0.0.1', 'root', '1114', 'Climate')
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

        # Dropdown for selecting city
        city = st.selectbox('Select a city', tables_list)  # Add more cities here

        # Text input for date
        date = st.date_input("Enter Date")

        # Number inputs for other data
        temperature = st.number_input("Enter Temperature", step=0.1)
        humidity = st.number_input("Enter Humidity", step=0.1)
        wind_speed = st.number_input("Enter Wind Speed", step=0.1)
        precipitation = st.number_input("Enter Precipitation", step=0.1)

        # Button to submit data
        if st.button("Submit"):
            if date:
                success, message = add_data(city, temperature, humidity, precipitation, wind_speed, date)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please enter date")
                
def delete_data(connection, city,date):
    try:
        cursor = connection.cursor()
        # Delete data from the specified table based on the condition
        delete_query = f"DELETE FROM `{city}` WHERE `Date` = '{date}'"
        cursor.execute(delete_query)
        connection.commit()
        cursor.close()
        connection.close()
        return True, "Data deleted successfully"
    except Exception as e:
        return False, f"Error deleting data: {e}"
                   
def delete():
    st.title("Delete a record")
    
    connection = connect_to_mysql('127.0.0.1', 'root', '1114', 'Climate')
    
    if connection:
        table_query = "SHOW TABLES"

        # Execute the queries
        cursor = connection.cursor()

        # Execute the table query
        cursor.execute(table_query)
        tables_data = cursor.fetchall()
        tables_list = [table[0] for table in tables_data]

        # Dropdown for selecting city
        city = st.selectbox('Select a city', tables_list)
        
        date = st.date_input("Enter Date")
        
        if st.button("Submit"):
            if date:
                success, message = delete_data(connection, city, date)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please enter date")

def update_record(connection, city, date, temperature, humidity, precipitation, wind_speed):
    try:
        cursor = connection.cursor()
        # Update data in the specified table based on the condition
        update_query = f"UPDATE `{city}` "
        update_query += f"SET Temperature = '{temperature}', "
        update_query += f"Humidity = '{humidity}', "
        update_query += f"Precipitation = '{precipitation}', "
        update_query += f"`Wind Speed` = '{wind_speed}' "
        update_query += f"WHERE `Date` = '{date}'"
        
        
        cursor.execute(update_query)
        connection.commit()
        cursor.close()
        connection.close()
        return True, "Data updated successfully"
    
    except Exception as e:
        return False, f"Error updating data: {e}"
        
def modify():
    st.title("Update a record")
    connection = connect_to_mysql('127.0.0.1', 'root', '1114', 'Climate')
    if connection:
        # Query to retrieve all table names
        table_query = "SHOW TABLES"

        # Execute the queries
        cursor = connection.cursor()

        # Execute the table query
        cursor.execute(table_query)
        tables_data = cursor.fetchall()
        tables_list = [table[0] for table in tables_data]

        # Dropdown for selecting city
        city = st.selectbox('Select a city', tables_list)  # Add more cities here

        # Text input for date
        date = st.date_input("Enter Date")

        # Number inputs for other data
        temperature = st.number_input("Enter Temperature", step=0.1)
        humidity = st.number_input("Enter Humidity", step=0.1)
        wind_speed = st.number_input("Enter Wind Speed", step=0.1)
        precipitation = st.number_input("Enter Precipitation", step=0.1)

        # Button to submit data
        if st.button("Submit"):
            if date:
                #update_data = {'Temperature': temperature, 'Humidity': humidity, 'Precipitation': precipitation, 'Wind Speed': wind_speed}
                success, message = update_record(connection, city, date, temperature,humidity, precipitation,wind_speed)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please enter date")

def view_dataset(connection,city):
    try:
        dataset_query=f'SELECT * FROM {city}'
        cursor = connection.cursor()
        cursor.execute(dataset_query)
        dataset_data = cursor.fetchall()
        
        # Get column names from the cursor description
        columns = [desc[0] for desc in cursor.description]
        
        df=pd.DataFrame(dataset_data,columns=columns)
        
        
        st.dataframe(df,use_container_width=True)
        
    except Exception as e:
        print(f'Error fetching data: {e}')        
                  
def view():
    st.title('View Dataset')
    
    connection = connect_to_mysql('127.0.0.1', 'root', '1114', 'Climate')
    if connection:
        # Query to retrieve all table names
        table_query = "SHOW TABLES"

        # Execute the queries
        cursor = connection.cursor()

        # Execute the table query
        cursor.execute(table_query)
        tables_data = cursor.fetchall()
        tables_list = [table[0] for table in tables_data]

        # Dropdown for selecting city
        city = st.selectbox('Select a city', tables_list)
        
        if st.button("submit"):
            view_dataset(connection, city)          
          
def admin_acess():
    opt=st.radio("Select an option",['Add a record','Delete a record','Update a record','View Dataset'])
    if opt=='Add a record':
        add_data_page()
    elif opt=='Delete a record':
        delete()
    elif opt=='Update a record':
        modify()
    else:
        view()

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
  

st.markdown("<h1 style='color: #2196F3;'>Climate Pulse</h1>"
            "<h3 style='color: #333333;'>Envisioning environment change - for a greener future</h3>", unsafe_allow_html=True)
            

st.sidebar.header("Menu")

if "page" not in st.session_state:
    st.session_state.page = None


if st.sidebar.button("Home"):
    st.session_state.page = "home"
    
if st.sidebar.button("Add Data"):
    st.session_state.page = "add"

if st.sidebar.button("AI Assistent"):
    st.session_state.page = "aiass"



# Spacer between navigation and logout button
for i in range(25):
    st.sidebar.markdown("      ")


if st.sidebar.button("Log Out", key="logout_button", help="Click here to log out"):
    # Add your log out logic here
    st.write("You clicked Log Out")
    # Redirect to another HTML page using JavaScript
    st.write("""
    <meta http-equiv="refresh" content="0; URL='http://127.0.0.1:5500/user-admin/user-admin.html'" />
    """, unsafe_allow_html=True)
    

if "page" in st.session_state:
    if st.session_state.page == "home":
        display_map()
    elif st.session_state.page == "aiass":
        chatbot()
    elif st.session_state.page == "add":
        admin_acess()
    else:
        display_map()







    