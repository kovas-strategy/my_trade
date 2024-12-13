from flask import Flask, render_template, request, jsonify
import pandas as pd

# Load the data
data_file = 'data.xlsx'
df = pd.read_excel(data_file, sheet_name='Sheet1')

# Extract Company list
companies = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()

# Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def index():
    if request.method == 'HEAD':
        return '', 200  # Return an empty response with status 200 for HEAD requests
    return render_template('index.html', companies=companies)

@app.route('/get_company_data', methods=['POST'])
def get_company_data():
    selected_company = request.json.get('company')
    if not selected_company:
        return jsonify({"error": "No company selected"}), 400

    company_start_index = df[df['기업명'] == selected_company].index[0]
    next_company_index = df[(df.index > company_start_index) & (df['Unnamed: 0'] == 'Company')].index
    next_company_index = next_company_index[0] if not next_company_index.empty else len(df)

    company_data = df.iloc[company_start_index + 1:next_company_index]
    company_data = company_data[company_data['Unnamed: 0'].isin(['Supplier', 'Buyer'])]

    data = company_data[['기업명', '국가', '품목', 'Last Shipment', 'Total # of Shipment']].dropna().to_dict(orient='records')
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
