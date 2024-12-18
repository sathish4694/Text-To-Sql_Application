import re
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import bigquery

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate SQL queries using Gemini
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt[0], question])
    return response.text.strip()

# Function to run the BigQuery query and retrieve results
def run_bigquery_query(query):
    client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))
    try:
        query_job = client.query(query)
        results = query_job.result()  # Wait for the job to complete
        return [dict(row) for row in results]
    except Exception as e:
        raise Exception(f"Error running query on BigQuery: {e}")

# Updated Prompt tailored for the customer data (customer_data table)
prompt = [
    f"""
    You are an expert in converting English questions to SQL queries and retrieving results directly from BigQuery.
    The table is located in Google BigQuery with the following information:
    - Project: {os.getenv("GCP_PROJECT_ID")}
    - Dataset: {os.getenv("GCP_DATASET_ID")}
    - Table: {os.getenv("GCP_TABLE_ID")}

    The table has the following columns: Income, Limit, Rating, Cards, Age, Education, Gender, Student, Married, Ethnicity, Balance.

    Your task is to generate an SQL query based on the user's natural language question. 
    The question should be transformed into a SQL query that retrieves the results from BigQuery. 
    Examples of questions and SQL queries:

    Example 1: "What is the average income of customers?"
    SQL query: 
    SELECT AVG(Income) FROM {os.getenv("GCP_PROJECT_ID")}.{os.getenv("GCP_DATASET_ID")}.{os.getenv("GCP_TABLE_ID")};

    Example 2: "How many customers have a rating above 700?"
    SQL query: 
    SELECT COUNT(*) FROM {os.getenv("GCP_PROJECT_ID")}.{os.getenv("GCP_DATASET_ID")}.{os.getenv("GCP_TABLE_ID")} WHERE Rating > 700;

    Example 3: "What is the average balance of customers who are married?"
    SQL query: 
    SELECT AVG(Balance) FROM {os.getenv("GCP_PROJECT_ID")}.{os.getenv("GCP_DATASET_ID")}.{os.getenv("GCP_TABLE_ID")} WHERE Married = 'Yes';

    Your response should only include the results from executing the SQL query, not the SQL query itself.
    """
]

# Streamlit App
st.set_page_config(page_title="Text-to-SQL Application")

# Adding logo at the top
logo_path = "https://images.miraclesoft.com/miracle-logo-dark.svg"  # Replace this with the correct path to your logo
st.image(logo_path, width=200)

st.header("Retrieve Data from BigQuery using Natural Language")

# Styling using custom CSS
st.markdown("""
    <style>
        .main {
            font-family: 'Arial', sans-serif;
        }
        .header {
            color: #4CAF50;
        }
        .input-box {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 14px;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

# User input
question = st.text_input("Enter your query in English:", key="input", placeholder="e.g. What is the average income of customers?", help="Type your query in natural language.")

submit = st.button("Submit", key="submit", help="Click to generate the query")

def sanitize_query(sql_query):
    """
    Function to sanitize SQL query, focusing on ensuring proper formatting for numbers and avoiding invalid literals.
    """
    # Ensure proper formatting of floating point numbers (no spaces, no commas, etc.)
    sql_query = re.sub(r'(\d+)\.(\d+)', r'\1.\2', sql_query)  # Fix potential issues with dot and number formatting
    sql_query = re.sub(r'(\d+)\s*([><=!]=?)\s*(\d+\.\d+)', r'\1\2\3', sql_query)  # Ensure spaces are not present between operators and numbers
    
    # Additional check for numbers like '42' that might appear in the wrong places
    sql_query = re.sub(r'^\d+$', '', sql_query)  # Remove standalone numbers at the start of the query

    # Check for common query structures and add missing SELECT statement if necessary
    if not sql_query.lower().startswith("select"):
        sql_query = f"SELECT {sql_query}"

    return sql_query.strip()

if submit:
    try:
        # Step 1: Generate SQL query from the question using Gemini
        sql_query = get_gemini_response(question, prompt)
        
        # # Step 2: Log the generated query for debugging purposes
        # st.write("Generated SQL Query: ", sql_query)  # Log the generated query
        
        # Step 3: Sanitize and clean up the query
        sql_query = sanitize_query(sql_query)

        # Log sanitized query before execution for debugging
        st.write("Output: ", sql_query)  # Log sanitized query

        # Step 4: Execute the query on BigQuery and retrieve the results
        results = run_bigquery_query(sql_query)

        # # Step 5: Display results as one unified response
        # st.subheader("Query Results:")
        # if results:
        #     # Combine all results into one string and display
        #     combined_results = "\n".join([str(row) for row in results])
        #     st.write(combined_results)
        # else:
        #     st.write("No results found.")

    except Exception as e:
        # Handle errors more gracefully with detailed messages
        st.error(f"An error occurred while processing the request: {str(e)}")
        st.write("Please ensure the query is valid and try again.")

# Footer section with "Developed By" message
st.markdown("""
    <div class="footer">
        <p>Developed by Sathish Mattapalli >
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    import os
    import subprocess

    # Get the port from the environment variable, default to 8080
    port = int(os.environ.get("PORT", 8080))

    # Ensure compatibility with deployment environments
    script_path = os.path.abspath(__file__)
    subprocess.run(["streamlit", "run", script_path, "--server.port", str(port)])
