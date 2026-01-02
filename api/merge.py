from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai
from PIL import Image
import io
import base64
import os

def setup_gemini(api_key):
    """Setup Gemini AI with API key"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')

def analyze_images_with_gemini(model, person_img, product_img):
    """Use Gemini to analyze both images"""
    prompt = """
    Analyze these two images:
    1. First image: A person
    2. Second image: A product
    
    Provide JSON format instructions for compositing:
    {
        "position_x": 0.5,
        "position_y": 0.5,
        "scale": 0.3,
        "opacity": 0.9,
        "description": "brief description"
    }
    """
    
    try:
        response = model.generate_content([prompt, person_img, product_img])
        return response.text
    except Exception as e:
        return None

def simple_merge(person_img, product_img, position=(0.5, 0.5), scale=0.3, opacity=0.9):
    """Merge product onto person image"""
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
    
    return result

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not data or 'person_image' not in data or 'product_image' not in data or 'api_key' not in data:
                response = {'error': 'Missing required data'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            api_key = data['api_key']
            
            # Decode base64 images
            person_data = base64.b64decode(data['person_image'].split(',')[1])
            product_data = base64.b64decode(data['product_image'].split(',')[1])
            
            person_img = Image.open(io.BytesIO(person_data))
            product_img = Image.open(io.BytesIO(product_data))
            
            # Setup Gemini
            model = setup_gemini(api_key)
            
            # Analyze with Gemini
            analysis = analyze_images_with_gemini(model, person_img, product_img)
            
            # Parse settings or use defaults
            position = (0.5, 0.5)
            scale = 0.3
            opacity = 0.9
            description = "Using default placement"
            
            if analysis:
                try:
                    import re
                    json_match = re.search(r'\{[^}]+\}', analysis)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        position = (parsed.get('position_x', 0.5), parsed.get('position_y', 0.5))
                        scale = parsed.get('scale', 0.3)
                        opacity = parsed.get('opacity', 0.9)
                        description = parsed.get('description', 'AI-suggested placement')
                except:
                    pass
            
            # Merge images
            result = simple_merge(person_img, product_img, position, scale, opacity)
            
            # Convert to base64
            buffered = io.BytesIO()
            result.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            response = {
                'success': True,
                'image': f'data:image/png;base64,{img_str}',
                'analysis': analysis or 'Used default settings',
                'settings': {
                    'position': position,
                    'scale': scale,
                    'opacity': opacity,
                    'description': description
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

