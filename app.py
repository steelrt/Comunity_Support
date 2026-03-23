from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ⬇️ APNI GROQ KEY YAHAN HAI
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load intents for fallback
with open('models/intents.json', 'r') as f:
    intents = json.load(f)

# ==================== MAIN ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

# ==================== SERVICE PAGES ====================

@app.route('/services/government')
def government():
    return render_template('government.html')

@app.route('/services/digital-id')
def digital_id():
    return render_template('digital-id.html')

@app.route('/services/engagement')
def engagement():
    return render_template('engagement.html')

@app.route('/services/report')
def report():
    return render_template('report.html')

@app.route('/services/events')
def events():
    return render_template('events.html')

@app.route('/services/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/services/mahadbt')
def mahadbt():
    return render_template('mahadbt.html')

# ==================== DETAILED SERVICE PAGES ====================

@app.route('/services/<service_name>')
def service_detail(service_name):
    services = {
        'birth-certificate': {
            'title': 'Birth Certificate',
            'category': 'Government Services',
            'description': 'Apply for and obtain your birth certificate online.',
            'steps': ['Visit the official portal', 'Fill in required details', 'Upload supporting documents', 'Pay applicable fee', 'Track application status'],
            'documents_needed': ['ID Proof', 'Address Proof', 'Parent Details'],
            'processing_time': '7-10 days'
        },
        'driving-license': {
            'title': 'Driving License',
            'category': 'Government Services',
            'description': 'Apply for your driving license online.',
            'steps': ['Register on RTO portal', 'Book appointment', 'Take learning license test', 'Complete driving test', 'Receive DL certificate'],
            'documents_needed': ['Age Proof', 'Address Proof', 'Medical Certificate'],
            'processing_time': '15-30 days'
        },
        'aadhaar': {
            'title': 'Aadhaar Registration',
            'category': 'Digital Identity',
            'description': 'Register for Aadhaar - Your unique 12-digit identity.',
            'steps': ['Visit Aadhaar enrollment center', 'Provide biometric data', 'Verify OTP', 'Wait for Aadhaar letter'],
            'documents_needed': ['Proof of Residence', 'Proof of Identity'],
            'processing_time': '90 days'
        },
        'feedback': {
            'title': 'Feedback & Suggestions',
            'category': 'Citizen Engagement',
            'description': 'Share your valuable feedback and suggestions.',
            'steps': ['Select category', 'Write your feedback', 'Attach documents if needed', 'Submit and track status'],
            'documents_needed': [],
            'processing_time': '5-7 days'
        }
    }
    service = services.get(service_name)
    if service:
        return jsonify(service)
    return jsonify({'error': 'Service not found'}), 404

# ==================== CHATBOT API (GROQ AI) ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant for Community Platform — an Indian government services portal.
Help users with:
- Aadhaar card services
- PAN card apply and update
- Ration card application
- MahaDBT scholarship form filling (mahadbt.maharashtra.gov.in)
- Driving Licence application
- Voter ID registration
- Passport application
- RTI filing
- Emergency helpline numbers (112, 100, 102, 101)
- Income certificate, Caste certificate
- PMAY housing scheme
- Cyber crime reporting (1930)

Always give step by step guidance.
Respond in the same language as the user (Hindi or English).
If user asks in Hindi/Hinglish, reply in Hindi/Hinglish.
Be friendly, concise and helpful.
Keep responses under 300 words."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=600,
            temperature=0.7
        )

        response_text = completion.choices[0].message.content
        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        # Fallback to intents if Groq fails
        fallback = find_intent_response(user_message if 'user_message' in locals() else "help")
        return jsonify({
            'response': fallback,
            'timestamp': datetime.now().isoformat()
        })

def find_intent_response(user_message):
    user_message = user_message.lower().strip()
    for intent in intents.get('intents', []):
        for pattern in intent.get('patterns', []):
            if pattern.lower() in user_message or user_message in pattern.lower():
                import random
                responses = intent.get('responses', [])
                return random.choice(responses) if responses else "I'm not sure about that."
    keyword_map = {
        'mahadbt': 'mahadbt_scholarship', 'scholarship': 'mahadbt_scholarship',
        'aadhaar': 'aadhaar', 'aadhar': 'aadhaar', 'pan': 'pan_card',
        'ration': 'ration_card', 'driving': 'driving_licence', 'voter': 'voter_id',
        'passport': 'passport', 'income': 'income_certificate', 'caste': 'caste_certificate',
        'emergency': 'emergency', 'fraud': 'cyber_crime', 'cyber': 'cyber_crime',
    }
    for keyword, tag in keyword_map.items():
        if keyword in user_message:
            for intent in intents.get('intents', []):
                if intent['tag'] == tag:
                    import random
                    return random.choice(intent['responses'])
    for intent in intents.get('intents', []):
        if intent['tag'] == 'fallback':
            import random
            return random.choice(intent['responses'])
    return "Sorry, I didn't understand. Please ask about Aadhaar, PAN card, MahaDBT scholarship or other services!"

# ==================== API ENDPOINTS ====================

@app.route('/api/services')
def get_all_services():
    return jsonify({
        'services': [
            {'id': 1, 'name': 'Online Government Services', 'link': '/services/government'},
            {'id': 2, 'name': 'Digital Identity & Security', 'link': '/services/digital-id'},
            {'id': 3, 'name': 'Citizen Engagement Initiatives', 'link': '/services/engagement'},
            {'id': 4, 'name': 'Report an Issue', 'link': '/services/report'},
            {'id': 5, 'name': 'Events & Meetups', 'link': '/services/events'},
            {'id': 6, 'name': 'Emergency Help', 'link': '/services/emergency'},
            {'id': 7, 'name': 'MahaDBT Scholarship', 'link': '/services/mahadbt'},
        ]
    })

@app.route('/api/announcements')
def get_announcements():
    return jsonify({
        'announcements': [
            {'title': 'New Service Added', 'date': '2024-03-23', 'description': 'Check our new digital services'},
            {'title': 'Maintenance Notice', 'date': '2024-03-22', 'description': 'Portal will be down for maintenance'},
        ]
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)