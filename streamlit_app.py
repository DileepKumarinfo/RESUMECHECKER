import streamlit as st
import PyPDF2 as pdf
import google.generativeai as genai
import json
import re 

import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    #generate a response from the Gemini model using the provided prompt
    response = model.generate_content(prompt)
    # return a text response from the model's response
    return response.text

def clean_json_response(response):
    # search for json like structure in the response using regex
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    # if JSonon structure is found, extract it
    if json_match:
        # extract the matched json string
        json_str = json_match.group(0)
        # clean up the json string by removing unwanted characters
        json_str = json_str.replace('\n', ' ').replace('\r', ' ').strip()
        # return the cleaned json string
        return json_str
    else:
        # if no json structure is found, return None
        return None

def input_pdf_text(uploaded_file):
    # create a PDF reader object using the uploaded file
    pdf_reader = pdf.PdfReader(uploaded_file)
    # initialize an empty string to hold the extracted text
    text = ""
    # iterate through each page in the PDF and extract text
    for page in range(len(pdf_reader.pages)):
        # get the current page
        page = pdf_reader.pages[page]
        # extract text from the current page and append it to the text string
        text += page.extract_text()
    return text

#Define the Prompt Templare for the ATS anlysis
input_prompt = """
You are an expert ATS (Application Tracking System) with deep knowledge in tech fields including software engineering, data science, data analytics, and big data engineering.

Your task is to evaluate the resume against the given job description and provide a detailed analysis. Consider the competitive job market and provide actionable improvement suggestions.

IMPORTANT: You must respond with ONLY a JSON object in the following exact format, with no additional text:
{{
    "JD Match": "X%",
    "MissingKeywords": ["keyword1", "keyword2", "keyword3"],
    "Profile Summary": "Your detailed analysis and improvement suggestions here"
}}

resume: {text}
description: {jd}
"""


st.set_page_config(page_title="Smart ATS - Resume Analyzer", page_icon="📝", layout="wide")
st.title("Smart ATS - Resume Analyzer")
st.write("Upload your resume and job description to see how well you match the job requirements.")

jd = st.text_area("Paste the Job Description")

uploaded_file = st.file_uploader("Choose a resume file", type="pdf", help="Upload your resume in PDF format.")

submit = st.button("Submit")

#check if the submit button is clicked
if submit:
    # verify if the job description is provided and a file is uploaded
    if jd and uploaded_file:
        # extract text from the uploaded PDF file
        text = input_pdf_text(uploaded_file)
        # Format the prompt with resume text and job description
        prompt = input_prompt.format(text=text, jd=jd)
        # get the response from the Gemini model
        response = get_gemini_response(prompt)
        # clean and extract json from the response
        json_str = clean_json_response(response)

        if json_str:
            try:
                #parse the json string into a python dictionary
                result = json.loads(json_str)
                # display the results in a structured format
                st.subheader("ATS Analysis Result")
                st.write(f"JD Match: {result['JD Match']}")
                # display missing keywords 
                st.write("Missing Keywords:")
                for keyword in result['MissingKeywords']:
                    st.write(f"- {keyword}")
                # display the profile summary
                st.write("Profile Summary:")
                st.write(result['Profile Summary'])
            except json.JSONDecodeError:
                st.error("Error parsing JSON response from the model.")
        else:
            st.error("No valid JSON response found from the model.")
    else:
        st.error("Please provide both a job description and upload a resume file.")
