from flask import Flask, render_template, request, jsonify
import pandas as pd

# Load the data
data_file = 'data.xlsx'  # Replace with the path to your Excel file
df = pd.read_excel(data_file, sheet_name='Sheet1')

# Extract Company list
companies = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    # Pass Company list to the front end
    return render_template('search.html', companies=companies)

@app.route('/get_company_data', methods=['POST'])
def get_company_data():
    # Get the selected company from the request
    selected_company = request.json.get('company')
    if not selected_company:
        return jsonify({"error": "No company selected"}), 400

    # Find the starting index of the selected company
    company_start_index = df[df['기업명'] == selected_company].index[0]

    # Find the next "Company" index to limit the range
    next_company_index = df[(df.index > company_start_index) & (df['Unnamed: 0'] == 'Company')].index
    next_company_index = next_company_index[0] if not next_company_index.empty else len(df)

    # Filter rows for the selected company
    # Only include rows from the current Company to the next Company, excluding the Company row itself
    company_data = df.iloc[company_start_index + 1:next_company_index]
    company_data = company_data[company_data['Unnamed: 0'].isin(['Supplier', 'Buyer'])]

    # Convert to a list of dictionaries for JSON response
    data = company_data[['기업명', '국가', '품목', 'Last Shipment', 'Total # of Shipment']].dropna().to_dict(orient='records')
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
