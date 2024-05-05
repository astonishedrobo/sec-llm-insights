## Demo

Find the demo of the app [here](https://youtu.be/q0o8jMft1E8).

## Insights

- **Revenue and Net Income:** Examining revenue and net income trends over time provides a high-level view of the company's financial trajectory and profitability. Sustained growth in both is a positive sign of financial health.

- **Effective Tax Rate:** Calculating the effective tax rate and comparing it to statutory rates and industry peers helps assess if the company's tax planning appears aggressive or conservative. An unusually low effective rate could be a red flag.

- **Deferred Tax Assets and Liabilities:** High or growing deferred tax assets may indicate the company is struggling and generating tax losses. Increasing deferred tax liabilities often mean the company is deferring taxes through methods like accelerated depreciation.

- **Foreign Income Percentage:** For multinational companies, analyzing the mix of domestic vs foreign income over time is insightful. A growing proportion of foreign income could signal strategic offshoring of profits to lower-tax jurisdictions.

Along with the above analysis **segment wise Revenue & Net Income** is also showed. It is useful becasue:
- **Identifying key revenue drivers:** By reporting revenue for each segment (e.g., advertising, payments), users can quickly identify which business units are generating the most sales. This helps in understanding the company's main revenue drivers and potential future growth areas.

- **Assessing segment profitability:** Providing net income data for each segment allows users to evaluate the profitability of different business units. In the example given, while the advertising segment is highly profitable, the payments segment is currently operating at a loss. This information can guide investment decisions and highlight areas for improvement.

- **Trend analysis:** Tracking segment-wise revenue and net income over time enables users to spot trends, such as which segments are growing, stagnating, or declining. This can provide insights into the company's overall strategic direction and potential risks or opportunities.

- **Peer comparison:** Presenting segment-wise financial data allows for better comparisons with industry peers that have similar business units. This can help benchmark the company's performance and identify competitive advantages or disadvantages in specific markets.

## Code: Setup & Run
To fix the dependencies run the following command:
```
pip install -r requirements.txt
```
The app also uses `Tailwind` for frontend. Make sure it's installed on your system following the guidelines mention on their [website](https://tailwindcss.com/docs/installation).

Put your API key in a `.env` file in the format: `ANTHROPIC_API_KEY=<KEY>` under the project root directory.

To get the app up and running, follow these steps:

1. Clone the repository to your local machine.
2. Open a terminal and navigate to the project directory.
3. Run the command `python3 app.py` to start the application.
4. Open your web browser and visit `localhost:5000`.
5. On the home page, you will find a form to enter the stock ticker and other details (as demonstrated in the demo).
6. Fill in the required information and click the "Generate Insights" button to fetch insights for the specified stock.

## Application Flow

The application works as follows:

1. When you enter the ticker on the website and click the "Generate Insights" button, the backend initiates the process by fetching the tax filings for the specified years using the `fetch_10k.py` script. 
2. Once the tax filings are successfully fetched, the `visualize.py` scripts acts upon them. The `visualize()` function proceeds to analyze the data using the `analyze()` function from the `analyzer.py` module. However, before running the analyzer, it utilizes the `parse_filing_text()` function to semantically parse the tax files. This parsed data serves as the context for the Language Model (LLM) used in the analysis and the models return a JSON output containing the main fileds as mentioned in insights section. The output is then saved to a path of format `insights/{ticker}/{filing_year}/analysis.json`.
3. After the analysis is complete, two key functions are invoked:
   - `create_bar_plot()`: This function generates high-level time series insights, providing a visual representation of the stock's performance over the specified period. It saves the plots under `visualizations/{ticker}/insights/` directory.
   - `create_segment_bar_plots()`: This function generates detailed insights for each year, offering a more granular view of the stock's financial metrics. Similarly, it saves the plots under `visualizations/{ticker}/detailed/` directory.

## Directory Structure
```
project-root/
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── output.css
├── app.py
├── fetch_10k.py
├── analyzer.py
├── visualize.py
├── .env 
├── data/
│   └── sec-edgar-filings/
│       └── <ticker>/
├── insights/
│   └── <ticker>/
│       └── <filing_year>/
│           └── analysis.json
└── visualizations/
    └── <ticker>/
        ├── insights/
        └── detailed/
```

## Tech Stack

- **Python**: The primary programming language used for the backend implementation.

- **Flask**: Chosen for its simplicity and ease of use for building small-to-medium web applications.

- **Matplotlib**: Selected for its extensive functionality for creating a variety of visualizations.

- **Anthropic API**: Utilized due to its powerful language model capabilities and the availability of free credits for testing purposes.

- **sec-edgar-downloader**: Chosen for its convenience and ease of use in retrieving financial filings from the SEC's EDGAR database.

- **sec-parser**: Employed for its ability to semantically parse the 10-K filings and extract relevant information for analysis.

- **HTML / CSS (Tailwind) / JavaScript**: Used to create the user interface, handle form submissions, and display the generated visualizations in the browser.

## Current Issues:
The app currenly uses **Anthropic API** for generating the insights. However, sometimes it doesn't retuns proper json format for `insights.json`.

This issue can be solved by trying to generate the insight again or using **OpenAI GPT API** which allows to get the output in proper json format.

## Future Plans:

- **Natural Language Processing (NLP) Enhancements:** The current text analysis relies on the Anthropic API's language model. While powerful, there is room for improvement in terms of accuracy and specificity. I plan to explore the use of Retrieval-Augmented Generation (RAG) models, which will help generate more accurate, context-aware insights by combining language models with external knowledge retrieval.