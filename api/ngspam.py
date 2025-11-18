from http.server import BaseHTTPRequestHandler
import json
import requests
import time
import uuid
import hashlib
from urllib.parse import urlencode

class NgspamAbiq:
    def __init__(self, username, message, max_attempts=10, delay=1):
        self.username = username
        self.message = message
        self.max_attempts = max_attempts
        self.delay = delay
        self.counter = 0
        self.results = {
            'successful_attempts': 0,
            'rate_limited_attempts': 0,
            'failed_attempts': 0
        }

    def generate_device_id(self):
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:42]

    def get_formatted_time(self):
        return time.strftime("%H:%M:%S")

    def send_single_message(self, attempt_number):
        try:
            formatted_time = self.get_formatted_time()
            device_id = self.generate_device_id()
            
            url = "https://ngl.link/api/submit"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
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
            
            print(f"[{formatted_time}] [Attempt {attempt_number}] Mengirim request...")
            
            response = requests.post(
                url, 
                data=post_data, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"[{formatted_time}] [Error] Rate limited - Status: {response.status_code}")
                self.results['rate_limited_attempts'] += 1
                return {'success': False, 'reason': 'rate_limited'}
            else:
                self.counter += 1
                self.results['successful_attempts'] += 1
                print(f"[{formatted_time}] [Success] Pesan terkirim: {self.counter}")
                return {'success': True, 'reason': 'success'}
                
        except Exception as e:
            formatted_time = self.get_formatted_time()
            print(f"[{formatted_time}] [Error] Request gagal: {str(e)}")
            self.results['failed_attempts'] += 1
            return {'success': False, 'reason': str(e)}

    def run_educational_test(self):
        print("=== NGSPAM ABIQ PYTHON API ===")
        print(f"Target: {self.username}")
        print(f"Pesan: {self.message}")
        print(f"Max Attempts: {self.max_attempts}")
        print(f"Delay: {self.delay} seconds")
        print("===============================")
        
        for attempt in range(1, self.max_attempts + 1):
            result = self.send_single_message(attempt)
            
            if result['reason'] == "rate_limited":
                print("[Info] Menunggu 25 detik karena rate limit...")
                time.sleep(25)
                continue
            
            if attempt < self.max_attempts:
                time.sleep(self.delay)
        
        success_rate = (self.results['successful_attempts'] / self.max_attempts * 100) if self.max_attempts > 0 else 0
        
        final_results = {
            'target': self.username,
            'message': self.message,
            'successful_attempts': self.results['successful_attempts'],
            'rate_limited_attempts': self.results['rate_limited_attempts'],
            'failed_attempts': self.results['failed_attempts'],
            'total_attempts': self.max_attempts,
            'success_rate': round(success_rate, 2),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'developer': 'Abiq Nurmagedov',
            'github': 'https://github.com/abiqq',
            'support': 'https://saweria.co/abiqq57'
        }
        
        print("=== HASIL SPAMING ===")
        print(json.dumps(final_results, indent=2))
        
        return final_results

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            username = body.get('username', '')
            message = body.get('message', '')
            max_attempts = body.get('max_attempts', 5)
            delay = body.get('delay', 2)
            
            # Validation
            if not username or not message:
                self.send_error_response(400, 'Username and message are required')
                return
            
            if max_attempts > 20:
                self.send_error_response(400, 'Max attempts cannot exceed 20')
                return
            
            # Run spam
            spam_bot = NgspamAbiq(username, message, max_attempts, delay)
            results = spam_bot.run_educational_test()
            
            self.send_success_response(results)
            
        except Exception as e:
            self.send_error_response(500, f'Internal server error: {str(e)}')
    
    def send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'success',
            'data': data
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'error',
            'error': message
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
