from http.server import BaseHTTPRequestHandler
import json
import requests
import time
import uuid
import hashlib
from urllib.parse import urlencode
import os

class NgspamAbiq:
    def __init__(self, username, message, max_attempts=10, delay=1):
        self.username = username
        self.message = message
        self.max_attempts = max_attempts
        self.delay = delay
        self.counter = 0
        self.results = {
            'successful': 0,
            'failed': 0,
            'rate_limited': 0
        }

    def generate_device_id(self):
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:42]

    def send_single_message(self, attempt_number):
        try:
            device_id = self.generate_device_id()
            
            url = "https://ngl.link/api/submit"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"https://ngl.link/{self.username}",
                "Origin": "https://ngl.link"
            }
            
            post_data = urlencode({
                'username': self.username,
                'question': self.message,
                'deviceId': device_id,
                'gameSlug': '',
                'referrer': ''
            })
            
            response = requests.post(
                url, 
                data=post_data, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                self.results['successful'] += 1
                return {'success': True, 'status': response.status_code}
            else:
                self.results['failed'] += 1
                return {'success': False, 'status': response.status_code}
                
        except Exception as e:
            self.results['failed'] += 1
            return {'success': False, 'error': str(e)}

    def run_spam(self):
        print(f"Starting spam for {self.username}")
        
        for attempt in range(1, self.max_attempts + 1):
            result = self.send_single_message(attempt)
            
            # Add delay between requests
            if attempt < self.max_attempts:
                time.sleep(self.delay)
        
        success_rate = (self.results['successful'] / self.max_attempts * 100) if self.max_attempts > 0 else 0
        
        return {
            'target': self.username,
            'message': self.message,
            'results': {
                'successful': self.results['successful'],
                'failed': self.results['failed'],
                'total_attempts': self.max_attempts,
                'success_rate': round(success_rate, 2)
            },
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'developer': 'Abiq Nurmagedov',
            'github': 'https://github.com/abiqq',
            'support': 'https://saweria.co/abiqq57'
        }

def handler(request):
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    # Handle GET request (show API info)
    if request.method == 'GET':
        response_data = {
            'message': 'NGL Spam API by Abiq Nurmagedov',
            'version': '1.0',
            'endpoints': {
                'POST /': 'Send spam messages',
                'parameters': {
                    'username': 'Target username',
                    'message': 'Message to send',
                    'max_attempts': 'Number of attempts (default: 5)',
                    'delay': 'Delay between requests in seconds (default: 1)'
                }
            },
            'developer': 'Abiq Nurmagedov',
            'github': 'https://github.com/abiqq',
            'support': 'https://saweria.co/abiqq57'
        }
        return (json.dumps(response_data), 200, headers)

    # Handle POST request
    if request.method == 'POST':
        try:
            # Parse JSON body
            body = request.json()
            
            if not body:
                return (json.dumps({'error': 'No JSON body provided'}), 400, headers)
            
            username = body.get('username', '')
            message = body.get('message', '')
            max_attempts = body.get('max_attempts', 5)
            delay = body.get('delay', 1)

            # Validation
            if not username or not message:
                return (json.dumps({'error': 'Username and message are required'}), 400, headers)
            
            if max_attempts > 20:
                return (json.dumps({'error': 'Max attempts cannot exceed 20'}), 400, headers)

            # Run spam
            spam_bot = NgspamAbiq(username, message, max_attempts, delay)
            results = spam_bot.run_spam()
            
            response_data = {
                'status': 'success',
                'data': results
            }
            
            return (json.dumps(response_data), 200, headers)
            
        except Exception as e:
            error_data = {
                'status': 'error',
                'error': f'Internal server error: {str(e)}'
            }
            return (json.dumps(error_data), 500, headers)

    # Method not allowed
    return (json.dumps({'error': 'Method not allowed'}), 405, headers)
