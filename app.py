from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os

app = Flask(__name__, static_url_path='', static_folder='frontend')

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/generate-insight', methods=['POST'])
def generate_insight():
    data = request.get_json()
    company = data['company']
    email = data['email']
    ticker = data['ticker']
    from_year = int(data['fromYear'])
    to_year = int(data['toYear'])

    # Fetch the 10-K filings
    try:
        command = f'python fetch_10k.py --company="{company}" --email="{email}" --ticker="{ticker}" --start_year={from_year} --end_year={to_year}'
        subprocess.run(command, check=True, shell=True)
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error fetching 10-K filings: ' + str(e)}), 500

    # Perform text analysis and visualization
    try:
        command = f'python visualize.py --ticker="{ticker}" --start_year={from_year} --end_year={to_year}'
        print(command)
        subprocess.run(command, check=True, shell=True)
        
    except Exception as e:
        return jsonify({'error': 'Error generating insight: ' + str(e)}), 500

    # Return the path to the generated visualization
    return jsonify({'success': 'Visualization generated successfully'}), 200

@app.route('/visualizations/<path:path>')
def serve_visualizations(path):
    return send_from_directory('visualizations', path)

@app.route('/get-plots', methods=['GET'])
def get_plots():
    ticker = request.args.get('ticker')
    visualization_path = f'visualizations/{ticker}/insights'
    
    if not os.path.exists(visualization_path):
        return jsonify([]), 404
    
    plot_files = []
    for file_name in os.listdir(visualization_path):
        if file_name.endswith('.png'):
            plot_files.append({
                'title': file_name[:-4],  # Remove the '.png' extension
                'path': f'visualizations/{ticker}/insights/{file_name}'  # Update the path to include the ticker and file name
            })
    
    return jsonify(plot_files)

@app.route('/get-detailed-plots', methods=['GET'])
def get_detailed_plots():
    ticker = request.args.get('ticker')
    visualization_path = f'visualizations/{ticker}/detailed'
    
    if not os.path.exists(visualization_path):
        return jsonify([]), 404
    
    plot_files = []
    for file_name in sorted(os.listdir(visualization_path)):
        if file_name.endswith('.png'):
            plot_files.append({
                'title': file_name[:-4],  # Remove the '.png' extension
                'path': f'visualizations/{ticker}/detailed/{file_name}'
            })
    print(jsonify(plot_files))
    return jsonify(plot_files)

if __name__ == '__main__':
    app.run(port=5000)