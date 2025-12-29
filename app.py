from flask import Flask, request, send_file, jsonify
from rembg import remove
from PIL import Image, ImageFilter, ImageDraw
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
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        input_image = Image.open(file.stream)

        output_image = remove(input_image)

        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-background', methods=['POST'])
def add_background():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        img = Image.open(file.stream).convert('RGBA')

        width, height = img.size
        padding = 40
        shadow_offset = 10

        canvas_width = width + (padding * 2)
        canvas_height = height + (padding * 2)
        background = Image.new('RGB', (canvas_width, canvas_height), '#F5F5F5')

        shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))

        shadow_x = padding + shadow_offset
        shadow_y = padding + shadow_offset

        background.paste(shadow, (shadow_x, shadow_y), shadow)
        background.paste(img, (padding, padding), img)

        img_io = io.BytesIO()
        background.save(img_io, 'PNG', quality=95)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process-complete', methods=['POST'])
def process_complete():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        input_image = Image.open(file.stream)

        no_bg_image = remove(input_image)

        img = no_bg_image.convert('RGBA')
        width, height = img.size
        padding = 40
        shadow_offset = 10

        canvas_width = width + (padding * 2)
        canvas_height = height + (padding * 2)
        background = Image.new('RGB', (canvas_width, canvas_height), '#F5F5F5')

        shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))

        shadow_x = padding + shadow_offset
        shadow_y = padding + shadow_offset

        background.paste(shadow, (shadow_x, shadow_y), shadow)
        background.paste(img, (padding, padding), img)

        img_io = io.BytesIO()
        background.save(img_io, 'PNG', quality=95)
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render utilise en général le port 10000 en interne.
    port_str = os.environ.get('PORT', '10000')
    try:
        port = int(port_str)
    except ValueError:
        port = 10000

    print(f"[APP] Starting Flask on 0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port)

