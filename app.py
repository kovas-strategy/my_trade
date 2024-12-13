from flask import Flask, render_template, request, jsonify
import pandas as pd

# Load the data
data_file = 'data.xlsx'
df = pd.read_excel(data_file, sheet_name='Sheet1')

# Flask app
app = Flask(__name__)

@app.before_request
def handle_head_request():
    if request.method == 'HEAD':
        return '', 200

@app.route('/')
def index():
    # Extract Company list dynamically and sort alphabetically
    companies = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()
    companies = sorted(companies)  # Sort the company list alphabetically
    return render_template('search.html', companies=companies)

@app.route('/get_company_data', methods=['POST'])
def get_company_data():
    try:
        selected_company = request.json.get('company')
        print(f"Received request for company: {selected_company}")  # Debugging log
        if not selected_company:
            return jsonify({"error": "No company selected"}), 400

        # Find the starting index of the selected company
        company_rows = df[df['Unnamed: 0'] == 'Company']
        company_start_index = company_rows[company_rows['기업명'] == selected_company].index[0]

        # Find the next "Company" index to limit the range
        next_company = company_rows[company_rows.index > company_start_index]
        next_company_index = next_company.index[0] if not next_company.empty else len(df)

        # Filter rows for the selected company
        company_data = df.iloc[company_start_index + 1:next_company_index]
        company_data = company_data[company_data['Unnamed: 0'].isin(['Supplier', 'Buyer'])]

        # Get the list of all companies
        company_list = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()

        # Add hyperlinks if the company exists in the company list
        result = []
        for _, row in company_data.iterrows():
            company_name = row['기업명']
            hyperlink = f"/company?company={company_name}" if company_name in company_list else None
            result.append({
                "기업명": company_name,
                "국가": row['국가'],
                "품목": row['품목'],
                "Last Shipment": row['Last Shipment'],
                "Total # of Shipment": row['Total # of Shipment'],
                "hyperlink": hyperlink
            })

        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")  # Debugging log
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/company', methods=['GET'])
def company_redirect():
    # Get the company name from query parameters
    selected_company = request.args.get('company')
    if not selected_company:
        return render_template('error.html', error="No company selected.")

    # Use the same logic as /get_company_data
    company_rows = df[df['Unnamed: 0'] == 'Company']
    company_start_index = company_rows[company_rows['기업명'] == selected_company].index[0]
    next_company = company_rows[company_rows.index > company_start_index]
    next_company_index = next_company.index[0] if not next_company.empty else len(df)

    company_data = df.iloc[company_start_index + 1:next_company_index]
    company_data = company_data[company_data['Unnamed: 0'].isin(['Supplier', 'Buyer'])]

    company_list = df[df['Unnamed: 0'] == 'Company']['기업명'].dropna().tolist()

    result = []
    for _, row in company_data.iterrows():
        company_name = row['기업명']
        hyperlink = f"/company?company={company_name}" if company_name in company_list else None
        result.append({
            "기업명": company_name,
            "국가": row['국가'],
            "품목": row['품목'],
            "Last Shipment": row['Last Shipment'],
            "Total # of Shipment": row['Total # of Shipment'],
            "hyperlink": hyperlink
        })

    return render_template('results.html', selected_company=selected_company, data=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
