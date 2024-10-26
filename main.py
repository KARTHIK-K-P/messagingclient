import streamlit as st
import pandas as pd

# Load the CSV file
df_scenarios = pd.read_csv('court_scenarios.csv')

# Function to search for relevant documents based on keywords
def get_document_suggestions(case_description):
    suggested_documents = []
    for _, row in df_scenarios.iterrows():
        # Collect document suggestions from multiple columns
        documents = [row[col] for col in df_scenarios.columns if col.startswith('document_suggestions__') and pd.notnull(row[col])]
        
        # Check if the case description contains keywords from the "description" field
        if any(keyword.lower() in case_description.lower() for keyword in row['description'].split()):
            suggested_documents.extend(documents)
    
    return list(set(suggested_documents))  # Return unique suggestions

# Streamlit UI
st.title("Court Case Document Suggestion Tool")

# Input case description
case_description = st.text_area("Enter a description of your court case:")

# Get document suggestions based on the case description
suggestions = []
if case_description:
    suggestions = get_document_suggestions(case_description)

# Display suggested documents
if st.button("Get Document Suggestions"):
    if case_description:
        if suggestions:
            st.write("### Suggested Documents")
            st.write(suggestions)
        else:
            st.write("No document suggestions found. Try rephrasing your case description.")
    else:
        st.write("Please enter a case description to get suggestions.")

# File upload section
st.write("### Upload Suggested Documents")
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

# Calculate and display document strength based on uploaded files
if uploaded_files and suggestions:
    uploaded_file_names = [uploaded_file.name.split('.')[0] for uploaded_file in uploaded_files]  # Only file names without extension
    matched_docs = set(uploaded_file_names).intersection(set(suggestions))
    strength_percentage = (len(matched_docs) / len(suggestions)) * 100  # Calculate strength as percentage

    # Display uploaded files and document strength
    st.write("Uploaded files:")
    for uploaded_file in uploaded_files:
        st.write(uploaded_file.name)

    st.write(f"The submitted documents are {strength_percentage:.2f}% strong in supporting your case.")
elif uploaded_files:
    st.write("No document suggestions available for this case. Strength calculation cannot be performed.")
