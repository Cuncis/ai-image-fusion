from http.server import BaseHTTPRequestHandler
import json
import base64
import io
import re

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        # Simple test endpoint
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'ok',
            'message': 'API is working!',
            'info': 'Send POST request to /api with JSON data'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                response = {'error': 'Invalid JSON'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Check required fields
            if not data or 'person_image' not in data or 'product_image' not in data or 'api_key' not in data:
                response = {'error': 'Missing required fields: person_image, product_image, api_key'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Import PIL here (lazy import)
            try:
                from PIL import Image
            except ImportError:
                response = {'error': 'PIL not available'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Import Gemini here (lazy import)
            try:
                import google.generativeai as genai
            except ImportError:
                response = {'error': 'google-generativeai not available'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            api_key = data['api_key']
            
            # Decode base64 images
            try:
                person_data = base64.b64decode(data['person_image'].split(',')[1])
                product_data = base64.b64decode(data['product_image'].split(',')[1])
                
                person_img = Image.open(io.BytesIO(person_data))
                product_img = Image.open(io.BytesIO(product_data))
            except Exception as e:
                response = {'error': f'Failed to decode images: {str(e)}'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Setup Gemini
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception as e:
                response = {'error': f'Gemini setup failed: {str(e)}'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Analyze with Gemini (optional - use defaults if fails)
            position = (0.5, 0.5)
            scale = 0.3
            opacity = 0.9
            description = "Using default placement"
            analysis = "Used default settings"
            
            try:
                prompt = """Analyze these two images. Provide JSON: {"position_x": 0.5, "position_y": 0.5, "scale": 0.3, "opacity": 0.9, "description": "brief description"}"""
                response_ai = model.generate_content([prompt, person_img, product_img])
                analysis = response_ai.text
                
                # Try to parse JSON from response
                json_match = re.search(r'\{[^}]+\}', analysis)
                if json_match:
                    parsed = json.loads(json_match.group())
                    position = (parsed.get('position_x', 0.5), parsed.get('position_y', 0.5))
                    scale = parsed.get('scale', 0.3)
                    opacity = parsed.get('opacity', 0.9)
                    description = parsed.get('description', 'AI-suggested placement')
            except:
                pass  # Use defaults
            
            # Merge images
            try:
                person = person_img.convert('RGBA')
                product = product_img.convert('RGBA')
                
                person_width = person.size[0]
                new_product_width = int(person_width * scale)
                aspect_ratio = product.size[1] / product.size[0]
                new_product_height = int(new_product_width * aspect_ratio)
                
                product_resized = product.resize((new_product_width, new_product_height), Image.Resampling.LANCZOS)
                
                if opacity < 1.0:
                    alpha = product_resized.split()[3]
                    alpha = alpha.point(lambda p: int(p * opacity))
                    product_resized.putalpha(alpha)
                
                x = int(position[0] * person.size[0] - new_product_width / 2)
                y = int(position[1] * person.size[1] - new_product_height / 2)
                
                result = person.copy()
                result.paste(product_resized, (x, y), product_resized)
                
                # Convert to base64
                buffered = io.BytesIO()
                result.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                response = {
                    'success': True,
                    'image': f'data:image/png;base64,{img_str}',
                    'analysis': analysis,
                    'settings': {
                        'position': position,
                        'scale': scale,
                        'opacity': opacity,
                        'description': description
                    }
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                response = {'error': f'Image processing failed: {str(e)}'}
                self.wfile.write(json.dumps(response).encode())
                return
            
        except Exception as e:
            response = {'error': f'Server error: {str(e)}'}
            self.wfile.write(json.dumps(response).encode())
