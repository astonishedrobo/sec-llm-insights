from analyzer import analyze, parse_filing_text
import os
import re
import argparse
import json
import matplotlib.pyplot as plt
import shutil
import numpy as np


def get_year(folder_name):
    """
    Extract the year from the folder name.

    Args:
        - folder_name: The name of the folder containing the filing

    Returns:
        - The year as a string
    """
    # Use regular expression to extract the year part from the folder name
    match = re.search(r'-(\d{2})-', folder_name)
    if match:
        year = int(match.group(1))
        if year > 80:
            year += 1900
        else:
            year += 2000
    else:
        return None

    return str(year)

def extract_total_values(json_data):
    """
    Extract the total values for Revenue, Net Income, and other insights from the JSON data.

    Args:
        - json_data: The JSON data containing the insights
        - Example: {
            "Revenue": {
                "Segment 1": "$10 billion",
                "Segment 2": "$20 billion",
                ...
            }
            "Net Income": {
                "Segment 1": "$5 billion",
                "Segment 2": "$10 billion",
                ...
            }
            "Effective Tax Rate": "5%",
            "Deferred Tax Assets": "$1 billion",
            "Deferred Tax Liabilities": "$100 million",
            "Foreign Income Percentage": "80%"
        }

    Returns:
        - A dictionary containing the total values for Revenue, Net Income, and other insights in billions
        - Example: {
            "Revenue": 30,
            "Net Income": 15,
            "Effective Tax Rate": 5,
            "Deferred Tax Assets": 1,
            "Deferred Tax Liabilities": 0.1,
            "Foreign Income Percentage": 80
        }

    """
    main_keys = list(json_data.keys())
    total_values = {}

    for key in main_keys:
        if isinstance(json_data[key], dict):
            total_value = 0
            for sub_key, sub_value in json_data[key].items():
                if isinstance(sub_value, str):
                    # Extract the sign (+ or -) from the string
                    sign = 1
                    if sub_value.startswith('-'):
                        sign = -1
                        sub_value = sub_value[1:]
                    elif sub_value.startswith('+'):
                        sub_value = sub_value[1:]

                    # Replace anything non-number (except the decimal point) in the string with an empty string
                    value_str = re.sub(r'[^0-9.]', '', sub_value)
                    if value_str:
                        value = float(value_str)
                        # Convert value to billion if it contains "million" or "thousand"
                        if "million" in sub_value or "M" in sub_value:
                            value /= 1000
                        elif "thousand" in sub_value:
                            value /= 1000000
                        total_value += sign * value
            total_values[key] = total_value
        elif isinstance(json_data[key], str):
            # Extract the sign (+ or -) from the string
            sign = 1
            if json_data[key].startswith('-'):
                sign = -1
                json_data[key] = json_data[key][1:]
            elif json_data[key].startswith('+'):
                json_data[key] = json_data[key][1:]

            # Replace anything non-number (except the decimal point) in the string with an empty string
            value_str = re.sub(r'[^0-9.]', '', json_data[key])
            if value_str:
                value = float(value_str)
                # Convert value to billion if it contains "million" or "thousand"
                if "million" in json_data[key] or "M" in json_data[key]:
                    value /= 1000
                elif "thousand" in json_data[key]:
                    value /= 1000000
                total_values[key] = sign * value

    print(total_values)
    return total_values

def drop_none_values(data):
    """
    Drops keys with None values from a dictionary.

    Args:
        - data: A dictionary containing the data

    Returns:
        - A dictionary with keys that have non-None values
    """
    cleaned_data = {k: v for k, v in data.items() if v is not None}
    return cleaned_data

def create_bar_plot(ticker, insights):
    """
    Create bar plots for the total values of Revenue, Net Income, and other insights over the years.

    Args:
        - ticker: The company's stock ticker symbol
        - insights: A dictionary containing the insights for each year

    Returns:
        - None
        - Saves the bar plots in the "visualizations/{ticker}/insights" directory
    """
    # Delete the existing insights directory if it exists
    if os.path.exists(f'visualizations/{ticker}/insights'):
        shutil.rmtree(f'visualizations/{ticker}/insights')
    insights = drop_none_values(insights)
    years = sorted(list(insights.keys()))
    total_values_list = [extract_total_values(insights[year]) for year in years]
    keys = list(total_values_list[0].keys())

    for key in keys:
        values = [total_values[key] if key in total_values else 0 for total_values in total_values_list]

        plt.figure(figsize=(8, 6))
        plt.yscale('symlog') # Use logarithmic scale for the y-axis
        plt.bar(range(len(years)), values, color=[('r' if v < 0 else 'b') for v in values])
        plt.xlabel('Year')
        plt.ylabel(key)
        plt.title(f'{key} over the Years')
        plt.xticks(range(len(years)), years)

        # Save the plot in the visualizations/{ticker} directory
        os.makedirs(f'visualizations/{ticker}/insights', exist_ok=True)
        plt.savefig(f'visualizations/{ticker}/insights/{key}.png')
        plt.close()

def extract_values_for_segments_charts(json_data):
    """
    Extract the values for Revenue and Net Income segments for creating bar plots.

    Args:
        - json_data: The JSON data containing the insights
        - Example:
            {
                "Revenue": {
                    "Segment 1": "$10 billion",
                    "Segment 2": "$20 billion",
                    ...
                },
                "Net Income": {
                    "Segment 1": "$5 billion",
                    "Segment 2": "$10 billion",
                    ...
                }
            }
    
    Returns:
        - A dictionary containing the values for Revenue and Net Income segments in billions
        - Example: {
            "Revenue": {
                "Segment 1": 10,
                "Segment 2": 20,
                ...
            },
            "Net Income": {
                "Segment 1": 5,
                "Segment 2": 10,
                ...
        }
    """
    values = {}

    for key, value in json_data.items():
        if isinstance(value, dict):
            sub_values = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    # Extract the sign (+ or -) from the string
                    sign = 1
                    if sub_value.startswith('-'):
                        sign = -1
                        sub_value = sub_value[1:]
                    elif sub_value.startswith('+'):
                        sub_value = sub_value[1:]

                    # Replace anything non-number (except the decimal point) in the string with an empty string
                    value_str = re.sub(r'[^0-9.]', '', sub_value)
                    if value_str:
                        sub_values[sub_key] = sign * float(value_str)
            values[key] = sub_values

    return values

def create_segment_bar_plots(ticker, insights):
    """
    Create bar plots for Revenue and Net Income segments for each year.

    Args:
        - ticker: The company's stock ticker symbol
        - insights: A dictionary containing the insights for each year

    Returns:
    - None
    - Saves the bar plots in the "visualizations/{ticker}/detailed" directory
    """
    # Delete the existing detailed directory if it exists
    if os.path.exists(f'visualizations/{ticker}/detailed'):
        shutil.rmtree(f'visualizations/{ticker}/detailed')

    for year, data in insights.items():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(f'Revenue and Net Income Segments for {year}')

        # Revenue bar plot
        revenue_data = extract_values_for_segments_charts(data).get('Revenue', {})
        revenue_labels = list(revenue_data.keys())
        revenue_values = list(revenue_data.values())

        num_segments = len(revenue_values)
        revenue_colors = ['#%02x%02x%02x' % (r, g, b) for r, g, b in zip(
            np.round(np.linspace(0, 102, num_segments)).astype(int),
            np.round(np.linspace(115, 204, num_segments)).astype(int),
            np.round(np.linspace(230, 255, num_segments)).astype(int))]

        ax1.bar(revenue_labels, revenue_values, color=revenue_colors)
        ax1.set_xlabel('Revenue Segment')
        ax1.set_ylabel('Value (in billions)')
        ax1.set_title('Revenue Segments')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_yscale('symlog')# Use logarithmic scale for the y-axis

        # Net Income bar plot
        net_income_data = extract_values_for_segments_charts(data).get('Net Income', {})
        net_income_labels = list(net_income_data.keys())
        net_income_values = list(net_income_data.values())

        num_segments = len(net_income_values)
        profit_colors = ['#%02x%02x%02x' % (r, g, b) for r, g, b in zip(
            np.round(np.linspace(179, 0, num_segments)).astype(int),
            np.round(np.linspace(217, 115, num_segments)).astype(int),
            np.round(np.linspace(255, 230, num_segments)).astype(int))]
        loss_colors = ['#%02x%02x%02x' % (r, g, b) for r, g, b in zip(
            np.round(np.linspace(255, 230, num_segments)).astype(int),
            np.round(np.linspace(179, 0, num_segments)).astype(int),
            np.round(np.linspace(179, 0, num_segments)).astype(int))]

        net_income_colors = []
        for value in net_income_values:
            if value < 0:
                index = int(abs(value) / abs(min(net_income_values)) * (num_segments - 1))
                net_income_colors.append(loss_colors[index])
            else:
                index = int(value / max(net_income_values) * (num_segments - 1))
                net_income_colors.append(profit_colors[index])

        ax2.bar(net_income_labels, net_income_values, color=net_income_colors)
        ax2.set_xlabel('Net Income Segment')
        ax2.set_ylabel('Value (in billions)')
        ax2.set_title('Net Income Segments')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_yscale('symlog')# Use logarithmic scale for the y-axis

        plt.tight_layout()
        plt.subplots_adjust(top=0.88)

        # Save the plot in the visualizations/{ticker}/detailed directory
        os.makedirs(f'visualizations/{ticker}/detailed', exist_ok=True)
        plt.savefig(f'visualizations/{ticker}/detailed/{year}_segments.png')
        plt.close(fig)

def visualize(args):
    ticker = args.ticker
    start_year, end_year = int(args.start_year), int(args.end_year)
    data_path = f'data/sec-edgar-filings/{ticker}/10-K'
    insights = {}
    for year in os.listdir(data_path):
        filing_path = os.path.join(data_path, year, 'primary-document.html')
        filing_year = get_year(year)
        if not(int(filing_year) <= end_year and int(filing_year) >= start_year):
            continue
        filing_text = parse_filing_text(filing_path)
        # Check if analysis already exists
        if os.path.exists(f'insights/{ticker}/{filing_year}/analysis.json'):
            with open(f'insights/{ticker}/{filing_year}/analysis.json', 'r') as f:
                insights[filing_year] = json.load(f)
                if insights[filing_year] == None:
                    print(f"Error in {filing_year} analysis. Re-analyzing...")
                    insights[filing_year] = analyze(filing_text)  
        else:
            print(f"Analyzing {filing_year}...")
            insights[filing_year] = analyze(filing_text)
            print(insights[filing_year])

        # Save the analysis in insights/{ticker}/year/analysis.json
        insights_dir = f'insights/{ticker}/{filing_year}'
        print(insights_dir)
        os.makedirs(insights_dir, exist_ok=True)
        with open(os.path.join(insights_dir, 'analysis.json'), 'w') as f:
            json.dump(insights[filing_year], f, indent=4)

    # Generate visualizations based on the insights
    create_bar_plot(ticker, insights)
    create_segment_bar_plots(ticker, insights)


def main():
    parser = argparse.ArgumentParser(description="Generate insights from 10-K filings")
    parser.add_argument('--ticker', type=str, help="The company's stock ticker symbol")
    parser.add_argument('--start_year', type=int, help="The start year for analysis")
    parser.add_argument('--end_year', type=int, help="The end year for analysis")
    args = parser.parse_args()

    visualize(args)

if __name__ == '__main__':
    main()