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
            data = request.get_json() or {}
        else:
            data = request.form

        # Spam honeypot check (silently drop bot submissions)
        if data.get('website'):
            return jsonify({
                "success": True,
                "message": "Thank you! Your message has been sent successfully."
            }), 200

        # Get and sanitize form fields
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip() or 'N/A'
        company = (data.get('company') or '').strip() or 'N/A'
        enquiry_raw = (data.get('enquiry_type') or '').strip()
        message = (data.get('message') or '').strip()

        # Map enquiry option values to readable labels
        enquiry_map = {
            'general': 'General Enquiry',
            'product': 'Product Enquiry',
            'partnership': 'Partnership',
            'other': 'Other'
        }
        enquiry_type = enquiry_map.get(enquiry_raw.lower(), enquiry_raw.title() or 'General Enquiry')

        # Validate required fields
        if not name or not email or not message:
            if not request.is_json:
                return render_template('contact.html', form_error="Missing required fields"), 400
            return jsonify({
                "success": False,
                "message": "Missing required fields"
            }), 400

        try:
            # Refresh Resend API key in case it was updated in environment
            resend.api_key = os.environ.get("RESEND_API_KEY")

            # ------------------------
            # Create and Send Email via Resend
            # ------------------------
            body = f"""New Contact Enquiry from Muthu Groups Website

Name: {name}
Email: {email}
Phone: {phone}
Company: {company}
Enquiry Type: {enquiry_type}

Message:
{message}
"""

            clean_name = name.replace('\r', '').replace('\n', ' ')
            to_email = os.environ.get("CONTACT_EMAIL") or os.environ.get("NOTIFICATION_EMAIL") or CONTACT_EMAIL
            from_email = os.environ.get("RESEND_FROM_EMAIL") or RESEND_FROM_EMAIL

            params = {
                "from": from_email,
                "to": [to_email],
                "reply_to": email,
                "subject": f"New Contact Enquiry from {clean_name} - {enquiry_type}",
                "text": body
            }

            resend.Emails.send(params)

            if not request.is_json:
                return render_template('contact.html', form_success=True)

            return jsonify({
                "success": True,
                "message": "Thank you! Your message has been sent successfully."
            })

        except Exception as e:
            traceback.print_exc()
            print(f"Error sending email: {str(e)}")

            if not request.is_json:
                return render_template('contact.html', form_error="Failed to send email. Please try again later."), 500

            return jsonify({
                "success": False,
                "message": "Failed to send email. Please try again later."
            }), 500

    return render_template('contact.html')


# ------------------------
# Error Handlers
# ------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500


# ------------------------
# Run App
# ------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
