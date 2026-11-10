import os
import traceback
import resend
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
resend.api_key = os.environ.get("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "info@muthugroups.com")


# ------------------------
# Health Check Route
# ------------------------
@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


# ------------------------
# Main Routes
# ------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/companies')
def companies():
    return render_template('companies.html')


# ------------------------
# Contact Route
# ------------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        # Handle JSON or form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Get form fields
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', 'N/A')
        company = data.get('company', 'N/A')
        enquiry_type = data.get('enquiry_type', 'General Enquiry')
        message = data.get('message')

        # Validate required fields
        if not name or not email or not message:
            return jsonify({
                "success": False,
                "message": "Missing required fields"
            }), 400

        try:

            # ------------------------
            # Create and Send Email via Resend
            # ------------------------
            body = f"""
New Contact Enquiry from Muthu Groups Website

Name: {name}
Email: {email}
Phone: {phone}
Company: {company}
Enquiry Type: {enquiry_type}

Message:
{message}
"""

            params = {
                "from": RESEND_FROM_EMAIL,
                "to": [CONTACT_EMAIL],
                "subject": f"New Contact Enquiry from {name} - {enquiry_type}",
                "text": body
            }

            resend.Emails.send(params)

            return jsonify({
                "success": True,
                "message": "Thank you! Your message has been sent successfully."
            })

        except Exception as e:

            traceback.print_exc()

            print(f"Error sending email: {str(e)}")

            return jsonify({
                "success": False,
                "message": "Failed to send email. Please try again later."
            }), 500

    return render_template('contact.html')


# ------------------------
# Run App
# ------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
