from flask import Flask, render_template, request, jsonify
import pandas as pd

# Load the data
data_file = 'data.xlsx'  # Ensure this file is included in your repository
df = pd.read_excel(data_file, sheet_name='Sheet1')

# Filter only the rows with Company
companies = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('search.html', companies=companies)

@app.route('/get_company_data', methods=['POST'])
def get_company_data():
    # Get the selected company
    selected_company = request.json.get('company')
    if not selected_company:
        return jsonify({"error": "No company selected"}), 400

    # Find rows associated with the selected company
    company_index = df[df['기업명'] == selected_company].index
    if company_index.empty:
        return jsonify({"error": "Company not found"}), 404

    # Get rows under the selected company
    company_data = df.iloc[company_index[0] + 1:]
    company_data = company_data[company_data['Unnamed: 0'].isin(['Supplier', 'Buyer'])]

    # Convert to a list of dictionaries for JSON response
    data = company_data[['기업명', '국가', '품목', 'Last Shipment', 'Total # of Shipment']].dropna().to_dict(orient='records')
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
