from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

# Load the data
data_file = os.path.join(os.getcwd(), 'data.xlsx')
try:
    df = pd.read_excel(data_file, sheet_name='Sheet1')
except Exception as e:
    raise RuntimeError(f"Error loading data: {e}")

# Extract Company list
try:
    companies = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()
except KeyError:
    raise RuntimeError("Error: Required columns are missing in the data file.")

# Flask app
app = Flask(__name__)

# Handle HEAD requests globally
@app.before_request
def handle_head_request():
    if request.method == 'HEAD':
        return '', 200

@app.route('/')
def index():
    return render_template('search.html', companies=companies)

@app.route('/get_company_data', methods=['POST'])
def get_company_data():
    selected_company = request.json.get('company')
    if not selected_company:
        return jsonify({"error": "No company selected"}), 400

    # Validate selected company
    if selected_company not in df['기업명'].values:
        return jsonify({"error": "Company not found"}), 404

    # Find the starting index of the selected company
    try:
        company_start_index = df[df['기업명'] == selected_company].index[0]
    except IndexError:
        return jsonify({"error": "Company index not found"}), 404

    # Find the next "Company" index to limit the range
    next_company_index = df[(df.index > company_start_index) & (df['Unnamed: 0'] == 'Company')].index
    next_company_index = next_company_index[0] if not next_company_index.empty else len(df)

    # Filter rows for the selected company
    company_data = df.iloc[company_start_index + 1:next_company_index]
    company_data = company_data[company_data['Unnamed: 0'].isin(['Supplier', 'Buyer'])]

    data = company_data[['기업명', '국가', '품목', 'Last Shipment', 'Total # of Shipment']].dropna().to_dict(orient='records')
    return jsonify(data)

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Exception: {e}")
    return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
