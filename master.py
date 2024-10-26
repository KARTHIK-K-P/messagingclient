import streamlit as st
import pandas as pd
from twilio.rest import Client

# Load the court scenarios CSV file
df_scenarios = pd.read_csv('court_scenarios.csv')

# Twilio Configuration
TWILIO_ACCOUNT_SID = st.secrets["twilio"]["account_sid"]  # Fetch from secrets
TWILIO_AUTH_TOKEN = st.secrets["twilio"]["auth_token"]    # Fetch from secrets
TWILIO_WHATSAPP_NUMBER = st.secrets["twilio"]["whatsapp_number"]  # Fetch from secrets

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to search for relevant documents based on keywords
def get_document_suggestions(case_description):
    suggested_documents = []
    for _, row in df_scenarios.iterrows():
        # Check if the case description contains keywords from the "description" field
        if any(keyword.lower() in case_description.lower() for keyword in row['description'].split()):
            # Collect document suggestions from multiple columns
            documents = [row[col] for col in df_scenarios.columns if col.startswith('document_suggestions__') and pd.notnull(row[col])]
            suggested_documents.extend(documents)  # Add all document suggestions
    return list(set(suggested_documents))  # Return unique suggestions

# Streamlit UI
st.title("Court Case Document Suggestion Tool")

# Input case description
case_description = st.text_area("Enter a description of your court case:")

# Get document suggestions based on the case description
suggestions = []
if case_description:
    suggestions = get_document_suggestions(case_description)

# Display suggested documents when the button is clicked
if st.button("Get Document Suggestions"):
    if case_description:
        if suggestions:
            st.write("### Suggested Documents")
            for doc in suggestions:
                st.write("- " + doc)  # Display each document suggestion
        else:
            st.write("No document suggestions found. Try rephrasing your case description.")
    else:
        st.write("Please enter a case description to get suggestions.")

# Client's WhatsApp number input
client_whatsapp_number = st.text_input("Enter client's WhatsApp number (e.g., +1234567890):")

# Client's name input
client_name = st.text_input("Enter client's name:")

# Button to send WhatsApp message
if st.button("Send Document Collection Message"):
    if client_whatsapp_number and suggestions and client_name:
        # Create a formatted message
        message_body = (
            f"Hello there {client_name}!\n\n"
            f"Please bring the following documents while meeting your lawyer:\n"
            f"{', '.join(suggestions)}\n\n"
            "Please make sure to bring these documents safely.\n\n"
            "Thank you!"
        )
        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:{client_whatsapp_number}'
            )
            st.success(f"Message sent to {client_whatsapp_number}: {message_body}")
        except Exception as e:
            st.error(f"Failed to send message: {str(e)}")
    else:
        st.warning("Please enter a valid WhatsApp number, ensure there are suggested documents, and provide the client's name.")
