
import streamlit as st
import pandas as pd
import psycopg2
import time
import plotly.graph_objects as go
from datetime import datetime
from gtts import gTTS
from playsound import playsound

# Function to initialize the PostgreSQL connection
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

# Function to convert text to speech
def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("assistant_response.mp3")
    return "assistant_response.mp3"


# Function to execute a query and return results  
def run_query(query):
    with init_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        results= cur.fetchall()
        return results

# Function to get an answer from the database based on the question
def get_answer(question):
    query = f"SELECT answer FROM chatbot_data2 WHERE LOWER(question) like LOWER('%{question}%');"
    result = run_query(query)
    return result[0][0] if result else "I'm sorry, I don't have an answer for that."

# Function to get chart data based on the provided query
def get_chart_data(query, is_candlestick=False):
    result = run_query(query)

    if not result:
        return pd.DataFrame()

    # Get the number of columns based on the length of the first row
    num_columns = len(result[0])

    if is_candlestick:
        columns = ["lasttradetime", "open", "high", "low", "close"][:num_columns]
    else:
        columns = ["lasttradetime", "level1", "level3","level5","level7"][:num_columns]

    data = [tuple(row[:num_columns]) for row in result]
    df = pd.DataFrame(data, columns=columns)

    # Convert 'lasttradetime' column to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['lasttradetime']):
        df['lasttradetime'] = pd.to_datetime(df['lasttradetime'])

    return df


# Example usage in your Streamlit app
st.title("Simple chat")

# Initialize chat history with welcome message and set of questions
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to the chat."},
        {"role": "assistant", "content": "Feel free to ask me anything or choose from the following set of questions:"},
        {"role": "assistant", "content": "1. FUTIDX_BANKNIFTY_28DEC2023_XX_0"},        
        {"role": "assistant", "content": "2. BANKNIFTY28DEC2347900CE"},
        {"role": "assistant", "content": "3. USDINR15DEC23FUT"},
        {"role": "assistant", "content": "4. finniftyfut"},
        {"role": "assistant", "content": "5. finniftyce"},
        {"role": "assistant", "content": "6. finniftype"},
        {"role": "assistant", "content": "7. mcxfut"},
        
        {"role": "assistant", "content": "16. What is the latest news in finance?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hi, how can I help you?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Check if the user selected option 1
    if "1" in prompt:
        selected_question = "FUTIDX_BANKNIFTY_28DEC2023_XX_0"
    # Check if the user selected option 2
    elif "2" in prompt:
        selected_question = "BANKNIFTY28DEC2347900CE"

    elif "3" in prompt:
        selected_question = "USDINR15DEC23FUT"    
        
    elif "4" in prompt:
        selected_question = "finniftyfut"    

    elif "5" in prompt:
        selected_question = "finniftyce"    

    elif "6" in prompt:
        selected_question = "finniftype"    

    elif "7" in prompt:
        selected_question = "mcxfut"    
                    
    
    else:
        selected_question = prompt

    # Fetch response from the database
    answer = get_answer(selected_question.lower())  # Assuming the questions in the database are in lowercase

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""


        # Simulate stream of response with milliseconds delay
        for chunk in answer.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        # Convert text to speech and play the voice-over
        tts_filename = text_to_speech(full_response)
        audio_bytes = open(tts_filename, "rb").read()
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


    # Check if the user selected a question that requires a candlestick chart
    if "1" in prompt or "2" in prompt or "3" in prompt or "4" in prompt or "5" in prompt or "6" in prompt or "7" in prompt:
        candlestick_query = f"SELECT lasttradetime, open, high, low, close FROM table1_data1 WHERE instrumentidentifier='{selected_question}' ORDER BY lasttradetime LIMIT 100;"
        line_chart_query = f"SELECT lasttradetime, level1,level3,level5,level7 FROM table1 WHERE instrumentidentifier='{selected_question}' ORDER BY lasttradetime LIMIT 100;"

        candlestick_data = get_chart_data(candlestick_query, is_candlestick=True)
        line_chart_data = get_chart_data(line_chart_query, is_candlestick=False)
        # Display both candlestick and line charts
        fig = go.Figure()

        # Add candlestick trace
        fig.add_trace(go.Candlestick(x=candlestick_data['lasttradetime'],
                                    open=candlestick_data['open'],
                                    high=candlestick_data['high'],
                                    low=candlestick_data['low'],
                                    close=candlestick_data['close']))

            # Add line chart trace
        line_color = 'blue'  # Choose your desired color
        if 'level1' in line_chart_data.columns:
            fig.add_trace(go.Scatter(x=line_chart_data['lasttradetime'], y=line_chart_data['level1'], mode='lines', name='Line Chart 1',line_color=line_color))
        if 'level3' in line_chart_data.columns:
            fig.add_trace(go.Scatter(x=line_chart_data['lasttradetime'], y=line_chart_data['level3'], mode='lines', name='Line Chart 2',line_color=line_color))
        if 'level5' in line_chart_data.columns:
            fig.add_trace(go.Scatter(x=line_chart_data['lasttradetime'], y=line_chart_data['level5'], mode='lines', name='Line Chart 3',line_color=line_color))
        if 'level7' in line_chart_data.columns:
            fig.add_trace(go.Scatter(x=line_chart_data['lasttradetime'], y=line_chart_data['level7'], mode='lines', name='Line Chart 4',line_color=line_color))
        # Layout adjustments
        fig.update_layout(title="Candlestick and Line Chart Overlay",
                        xaxis_title="Last Trade Time",
                        yaxis_title="Price")

        st.plotly_chart(fig)
