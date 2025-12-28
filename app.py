from flask import Flask, request, send_file, jsonify
from rembg import remove
from PIL import Image, ImageFilter, ImageDraw, ImageOps
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "API is running",
        "endpoints": {
            "/remove-bg": "POST - Remove background from image",
            "/add-background": "POST - Add grey background with shadow",
            "/process-complete": "POST - Remove bg + add background in one call"
        }
    })

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    """Retire le fond d'une image"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        input_image = Image.open(file.stream)
        
        # Retirer le fond
        output_image = remove(input_image)
        
        # Convertir en bytes
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-background', methods=['POST'])
def add_background():
    """Ajoute un fond gris clair avec ombre portée"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        img = Image.open(file.stream).convert('RGBA')
        
        # Dimensions
        width, height = img.size
        padding = 40
        shadow_offset = 10
        
        # Créer le canvas avec fond gris clair
        canvas_width = width + (padding * 2)
        canvas_height = height + (padding * 2)
        background = Image.new('RGB', (canvas_width, canvas_height), '#F5F5F5')
        
        # Créer l'ombre
        shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Dessiner l'ombre (rectangle noir semi-transparent)
        shadow_draw.rectangle(
            [(0, 0), (width, height)], 
            fill=(0, 0, 0, 80)  # Noir à 80/255 d'opacité
        )
        
        # Flouter l'ombre pour effet réaliste
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Positionner l'ombre (légèrement décalée)
        shadow_x = padding + shadow_offset
        shadow_y = padding + shadow_offset
        
        # Composer l'image finale
        background.paste(shadow, (shadow_x, shadow_y), shadow)
        background.paste(img, (padding, padding), img)
        
        # Convertir en bytes
        img_io = io.BytesIO()
        background.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process-complete', methods=['POST'])
def process_complete():
    """Traitement complet : retire le fond + ajoute fond gris avec ombre"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        input_image = Image.open(file.stream)
        
        # Étape 1 : Retirer le fond
        no_bg_image = remove(input_image)
        
        # Étape 2 : Ajouter fond gris avec ombre
        img = no_bg_image.convert('RGBA')
        width, height = img.size
        padding = 40
        shadow_offset = 10
        
        canvas_width = width + (padding * 2)
        canvas_height = height + (padding * 2)
        background = Image.new('RGB', (canvas_width, canvas_height), '#F5F5F5')
        
        # Créer l'ombre
        shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Composer
        shadow_x = padding + shadow_offset
        shadow_y = padding + shadow_offset
        background.paste(shadow, (shadow_x, shadow_y), shadow)
        background.paste(img, (padding, padding), img)
        
        # Convertir en bytes
        img_io = io.BytesIO()
        background.save(img_io, 'PNG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
