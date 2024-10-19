from pydantic import BaseModel
from ..helpers import get_settings

import re
import os
import shutil
import requests
import google.generativeai as genai

settings = get_settings()


class CollegeCredentials(BaseModel):
    username: str
    password: str


class TranscriptController:
    def __init__(self, credentials: CollegeCredentials) -> None:
        """
        Initialize with user credentials, set up session, and headers.
        """
        self.username = credentials.username
        self.password = credentials.password
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
        }
        self.pdf_directory = "pdf"
        self.ensure_pdf_directory()

    def ensure_pdf_directory(self):
        """Ensure the directory for storing PDF transcripts exists."""
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)

    def login(self) -> bool:
        """
        Log in to the college website.
        Returns True if successful, False otherwise.
        """
        login_url = settings.COLLEGE_SCRAPING_SITE
        login_data = {"username": self.username, "password": self.password}
        login_response = self.session.post(
            login_url, json=login_data, headers=self.headers
        )

        if login_response.status_code == 200:
            print("Login successful!")
            return True
        else:
            print(f"Login failed. Status code: {login_response.status_code}")
            return False

    def download_transcript(self) -> str:
        """
        Download the transcript PDF file.
        Returns the path to the downloaded file or an empty string if failed.
        """
        download_url = settings.TRANSCRIPT_DOWNLOAD_LINK + self.username + ".pdf"
        print(f"Attempting to download transcript from: {download_url}")

        download_response = self.session.get(download_url, allow_redirects=True)
        if download_response.status_code == 200:
            filename = f"transcript-{self.username}.pdf"
            temp_path = filename
            with open(temp_path, "wb") as f:
                f.write(download_response.content)
            print(f"Transcript downloaded successfully as {filename}")
            return temp_path
        else:
            print(
                f"Failed to download transcript. Status code: {download_response.status_code}"
            )
            return ""

    def process_transcript_with_gemini(self, transcript_path: str) -> str:
        """
        Pass the downloaded transcript to the Gemini model and extract information.
        Returns the extracted data as a string.
        """
        # Step 1: Configure the Gemini API
        key = settings.GEMINI_API_KEY
        genai.configure(api_key=key)

        # Step 2: Initialize the Gemini model
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Step 3: Upload the PDF file to Gemini
        file_ref = genai.upload_file(transcript_path)

        # Step 4: Prepare the prompt for extracting student information
        prompt = settings.EXTRACT_STUDENT_INFORMATION_PROMPT

        # Step 5: Generate content using the model
        response = model.generate_content(
            [file_ref, prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0,  # Setting temperature to 0 for deterministic output
            ),
        )

        # Step 6: Return the extracted text from the PDF
        return response.text

    def process(self) -> str:
        """
        Orchestrate the full flow: login, download the transcript, process it with Gemini.
        Returns the extracted information as a string or an error message.
        """
        if self.login():
            temp_path = self.download_transcript()
            if temp_path:
                final_path = os.path.join(
                    self.pdf_directory, os.path.basename(temp_path)
                )
                shutil.move(temp_path, final_path)
                # Now that we have the transcript, pass it to the Gemini model for processing
                extracted_information = self.process_transcript_with_gemini(final_path)
                # Step 1: Add newlines after commas and curly braces
                # Step 1: Remove all newlines
                formatted_text = re.sub(r"\n+", " ", extracted_information)

                # Step 2: Remove multiple spaces
                formatted_text = re.sub(r"\s+", " ", formatted_text)

                # Step 3: Optionally remove spaces around curly braces and colons for compactness
                formatted_text = re.sub(r"\s*{\s*", "{", formatted_text)
                formatted_text = re.sub(r"\s*}\s*", "}", formatted_text)
                formatted_text = re.sub(r"\s*:\s*", ": ", formatted_text)
                formatted_text = re.sub(r"\s*,\s*", ", ", formatted_text)

                return formatted_text
            else:
                raise RuntimeError("Failed to download the transcript.")
        else:
            raise RuntimeError(
                "Login failed. Cannot proceed with downloading the transcript."
            )
