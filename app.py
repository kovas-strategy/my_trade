from flask import Flask, render_template, request, jsonify
import pandas as pd

# Load the data
data_file = 'data.xlsx'  # Ensure this file is included in your GitHub repository
df = pd.read_excel(data_file, sheet_name='Sheet1')
df = df.dropna(subset=['기업명'])  # Drop rows where '기업명' is NaN

# Flask app
app = Flask(__name__)

@app.route('/')
def index():
    # Pass the list of company names to the front end
    company_names = df['기업명'].dropna().unique().tolist()
    return render_template('search.html', companies=company_names)

@app.route('/get_company_info', methods=['POST'])
def get_company_info():
    # Get the selected company from the request
    selected_company = request.json.get('company')
    if not selected_company:
        return jsonify({"error": "No company selected"}), 400

    # Filter the dataframe for the selected company
    company_info = df[df['기업명'] == selected_company]
    if company_info.empty:
        return jsonify({"error": "Company not found"}), 404

    # Convert company info to a dictionary
    company_data = company_info.to_dict(orient='records')[0]
    return jsonify(company_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Allow external access
