import os
import requests
import json
from dotenv import load_dotenv
import sec_parser as sp
from sec_parser.processing_steps import TopSectionManagerFor10Q, IndividualSemanticElementExtractor, TopSectionTitleCheck

def analyze(filing_text, api_url="https://api.anthropic.com/v1/complete"):
    """
    Analyze the given filing text using the Anthropic API.

    Args:
        - filing_text (str): The semantically parsed text of the filing to analyze.
        - api_url (str): The URL of the Anthropic API.

    Returns:
        - dict: The analysis results in JSON format.
    """

    prompt = """From the "Management's Discussion and Analysis of Financial Condition and Results of Operations" and "Financial Statements and Supplementary Data" sections, extract the following information: Revenue (product wise if applicable), Net Income (product wise if applicable), Effective Tax Rate, Deferred Tax Assets, Deferred Tax Liabilities, Foreign Income Percentage, and any other relevant financial information

    answer in proper json format. Make sure the format is right that is it doesn't face the JSONDecodeError: Expecting ',' delimiter issue. Note: Only return the json, no additional text.
    Example Json (sub-fields may not match completely and change but the units should be same (billions), convert if you need to)
    {"Revenue": {"Compute & Networking": "$26.938 billion",
    "Graphics": "$11.718 billion"},
    "Net Income": {"Compute & Networking": "$7.634 billion",
    "Graphics": "$2.462 billion"},
    "Effective Tax Rate": "9.9%",
    "Deferred Tax Assets": "$5.05 billion",
    "Deferred Tax Liabilities": "$339 million",
    "Foreign Income Percentage": "85%"
    }

    Note: main fields ("Revenue", "Net Income", "Effective Tax Rate", "Deferred Tax Assets", "Deferred Tax Liabilities", "Foreign Income Percentage") should be present in the json. However, sub-fields may vary for example for Revenue the source of revenue may be different for different companies or different for same company in different years. You should mention the source of revenue in the sub-fields.
    Also mention profit or loss with positive or negative sign in front of the number.
    Make sure the json format is parseable and correct and doesn't face issues like "Expecting property name enclosed in double quotes", "Expecting ',' delimiter", etc.
    """

    max_tokens = 102398
    token_limit = max_tokens - len(prompt) - 100
    truncated_filing_text = filing_text[:token_limit]

    input_text = truncated_filing_text + "\n\n" + prompt

    # Load environment variables from .env file
    dotenv_path = os.path.join(os.getcwd(), '.env')
    load_dotenv(dotenv_path)
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        return None

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "prompt": f"\n\nHuman: {input_text}\n\nAssistant:",
        "stop_sequences": ["\n\nHuman"],
        "model": "claude-v1",
        "max_tokens_to_sample": 1000
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        insights = response.json()["completion"]
        print(insights)
        try:
            return json.loads(insights)
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
  
def without_10q_related_steps():
    all_steps = sp.Edgar10QParser().get_default_steps()
    
    # Change 1: Remove the TopSectionManagerFor10Q
    steps_without_top_section_manager = [step for step in all_steps if not isinstance(step, TopSectionManagerFor10Q)]
    
    # Change 2: Replace the IndividualSemanticElementExtractor with a new one that has the top section checks removed
    def get_checks_without_top_section_title_check():
        all_checks = sp.Edgar10QParser().get_default_single_element_checks()
        return [check for check in all_checks if not isinstance(check, TopSectionTitleCheck)]
    return [
        IndividualSemanticElementExtractor(get_checks=get_checks_without_top_section_title_check) 
        if isinstance(step, IndividualSemanticElementExtractor) 
        else step
        for step in steps_without_top_section_manager
    ]

def parse_filing_text(filing_html_path):
    with open(filing_html_path, 'r') as file:
        html = file.read()
    parser = sp.Edgar10QParser(get_steps=without_10q_related_steps)
    elements: list = parser.parse(html)
    tree: sp.SemanticTree = sp.TreeBuilder().build(elements)

    filing_text = [node.text for node in tree.nodes if node.text]
    return ' '.join(filing_text)
    