from flask import Flask, render_template, request, redirect, url_for, send_file
import cv2
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['image']
    filter_type = request.form.get('filter', 'original')
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        # Save original image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read image
        img = cv2.imread(filepath)
        
        # Apply filter
        processed_img = apply_filter(img, filter_type)
        
        # Save processed image
        processed_filename = f"processed_{filename}"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        cv2.imwrite(processed_path, processed_img)
        
        return render_template('result.html', 
                             original=filename, 
                             processed=processed_filename,
                             filter=filter_type)
    
    return redirect(url_for('index'))

def apply_filter(img, filter_type):
    """Apply selected filter to image"""
    h, w = img.shape[:2]
    
    if filter_type == 'original':
        return img
    
    elif filter_type == 'grayscale':
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    elif filter_type == 'negative':
        # Invert colors
        return 255 - img
    
    elif filter_type == 'blur':
        # Gaussian blur
        return cv2.GaussianBlur(img, (15, 15), 0)
    
    elif filter_type == 'sharpen':
        # Sharpen filter
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        return cv2.filter2D(img, -1, kernel)
    
    elif filter_type == 'edge':
        # Edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    elif filter_type == 'sepia':
        # Sepia tone (old photo effect)
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        sepia = cv2.transform(img, sepia_filter)
        return np.clip(sepia, 0, 255).astype(np.uint8)
    
    elif filter_type == 'cartoon':
        # Cartoon effect
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                      cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return cartoon
    
    elif filter_type == 'sketch':
        # Pencil sketch effect
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    elif filter_type == 'emboss':
        # Emboss effect
        kernel = np.array([[-2,-1,0],
                          [-1, 1,1],
                          [ 0, 1,2]])
        emboss = cv2.filter2D(img, -1, kernel)
        return emboss + 128
    
    elif filter_type == 'brightness':
        # Increase brightness
        return cv2.convertScaleAbs(img, alpha=1.0, beta=50)
    
    elif filter_type == 'contrast':
        # Increase contrast
        return cv2.convertScaleAbs(img, alpha=1.5, beta=0)
    
    elif filter_type == 'mirror':
        # Mirror/flip horizontally
        return cv2.flip(img, 1)
    
    elif filter_type == 'rotate':
        # Rotate 90 degrees
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    
    elif filter_type == 'pixelate':
        # Pixelate effect
        small = cv2.resize(img, (w//20, h//20), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    
    elif filter_type == 'vignette':
        # Vignette effect (dark corners)
        rows, cols = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols/2)
        kernel_y = cv2.getGaussianKernel(rows, rows/2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        vignette = np.copy(img)
        for i in range(3):
            vignette[:,:,i] = vignette[:,:,i] * mask
        return vignette.astype(np.uint8)
    
    elif filter_type == 'bw':
        # Black and white (threshold)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    
    elif filter_type == 'red':
        # Only red channel
        result = img.copy()
        result[:,:,0] = 0  # Remove blue
        result[:,:,1] = 0  # Remove green
        return result
    
    elif filter_type == 'green':
        # Only green channel
        result = img.copy()
        result[:,:,0] = 0  # Remove blue
        result[:,:,2] = 0  # Remove red
        return result
    
    elif filter_type == 'blue':
        # Only blue channel
        result = img.copy()
        result[:,:,1] = 0  # Remove green
        result[:,:,2] = 0  # Remove red
        return result
    
    return img

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, mimetype='image/jpeg')

@app.route('/processed/<filename>')
def processed_file(filename):
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    return send_file(filepath, mimetype='image/jpeg')

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)