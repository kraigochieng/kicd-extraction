# KICD Curriculum Data Extraction Pipeline

This project is an automated pipeline designed to scrape curriculum documents from the Kenya Institute of Curriculum Development (KICD) website, process them, and extract structured data using a Large Language Model (LLM). The final output is a set of clean, organized Excel files, making the curriculum data easily accessible for analysis and use.

## Workflow

The project operates in a sequential, three-stage pipeline. The output of each stage serves as the input for the next.

1. Scraping: A Scrapy spider navigates the KICD website and downloads the curriculum PDFs. These raw files are saved in the downloads directory.
2. Conversion: The md_creator.py script processes the downloaded PDFs, converting them into text-friendly Markdown (.md) files. This step makes the content easily readable for the language model. The results are stored in the markdown_files directory.
3. Extraction: The core script, llm_extraction.py, reads the Markdown files. It sends the content to an LLM via LangChain, which intelligently extracts predefined fields (like strand, theme, activity, etc.). This structured data is then saved as Excel (.xlsx) files in the excel_outputs directory.

### Workflow Diagram

```
graph TD
A[KICD Website] -->|1. Scrapy Spider| B(PDFs in `downloads/`);
B -->|2. md_creator.py| C(Markdown files in `markdown_files/`);
C -->|3. llm_extraction.py| D{LLM via LangChain};
D --> E[Structured Data (Pydantic Objects)];
E -->|Pandas| F(Excel files in `excel_outputs/`);
```

## Project Structure

The project is organized into several key directories and files:

```
.
├── downloads/ # Stores raw PDF files scraped from the KICD website.
├── markdown_files/ # Contains the Markdown versions of the PDFs.
├── excel_outputs/ # Final destination for the structured Excel data.
├── kicd_extraction/ # The Scrapy spider project directory.
├── md_creator.py # Script responsible for converting PDFs to Markdown.
├── llm_extraction.py # Main script that uses the LLM to extract data.
├── requirements.txt # A list of all Python dependencies for the project.
├── settings.py # For project configuration, including API keys.
└── README.md # This file.
```

## Setup and Installation

Follow these steps to get the project running on your local machine.

1. Prerequisites
   Python 3.8+

An API key from an LLM provider (e.g., Grok, OpenAI).

2. Clone the Repository

```bash

git clone <your-repository-url>

cd kicd_extraction
```

3. Create a Virtual Environment(or any other way you know)
   It's highly recommended to use a virtual environment to manage project dependencies.

```bash

python -m venv kicd_env
source kicd_env/bin/activate # On Windows, use `kicd_env\Scripts\activate` 4. Install Dependencies
```

4. Install all the required Python libraries from the requirements.txt file.

```bash

pip install -r requirements.txt
```

5. Configure Environment Variables. The project requires an API key to communicate with the language model. We use a .env file to manage these secrets securely. The settings.py file is built with Pydantic and will automatically read the variables from this file.

Step 1: Create the .env file

An example template (.env.example) is provided in the repository. Make a copy of this file and name it .env.

On macOS or Linux:

```bash

cp .env.example .env
```

On Windows:

```bash

copy .env.example .env
```

Step 2: Add Your API Key

Open the newly created .env file and add your API key from your LLM provider.

```Ini, TOML

# .env

# Replace YOUR_API_KEY_HERE with your actual API key

OPENAI_API_KEY="sk-YOUR_API_KEY_HERE"

# If using Grok or another provider, use the appropriate variable name

# GROK_API_KEY="gsk-YOUR_GROK_API_KEY_HERE"
```

The application will now be able to load your API key without you having to hardcode it into the script. Remember to never commit your .env file to version control.

## How to Run the Pipeline

Execute the scripts in the following order to run the full data extraction pipeline.

### Step 1: Run the Scrapy Spider

Navigate to the Scrapy project directory and run the spider to download the PDFs.

```bash

cd kicd_extraction
scrapy crawl curriculum
cd ..
```

This will populate the downloads directory with PDF files.

### Step 2: Convert PDFs to Markdown

Run the conversion script to process the downloaded PDFs.

```bash

python md_creator.py
```

This will read from the downloads directory and create corresponding files in the markdown_files directory.

### Step 3: Run the LLM Extraction

Finally, run the main extraction script. This will process the Markdown files and generate the final Excel outputs.

```bash

python llm_extraction.py
```

Check the excel_outputs directory for the resulting .xlsx files. The script uses a ThreadPoolExecutor to process multiple files in parallel for efficiency.
