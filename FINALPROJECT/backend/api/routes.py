"""
API Routes
REST endpoints for whiteboard control
"""

from flask import Blueprint, jsonify, request
import config

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# This will be set by the main app
whiteboard_state = None

def init_routes(state):
    """Initialize routes with whiteboard state"""
    global whiteboard_state
    whiteboard_state = state

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get current whiteboard status"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    return jsonify({
        'mode': whiteboard_state['gesture_recognizer'].get_mode_display_text(),
        'color': whiteboard_state['gesture_recognizer'].get_current_color_name(),
        'brush_size': whiteboard_state['brush_thickness'],
        'can_undo': whiteboard_state['canvas'].can_undo(),
        'can_redo': whiteboard_state['canvas'].can_redo(),
        'hand_detected': whiteboard_state.get('hand_detected', False)
    })

@api_bp.route('/clear', methods=['POST'])
def clear_canvas():
    """Clear the canvas"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        whiteboard_state['canvas'].clear()
        return jsonify({'success': True, 'message': 'Canvas cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/undo', methods=['POST'])
def undo():
    """Undo last stroke"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        success = whiteboard_state['canvas'].undo()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/redo', methods=['POST'])
def redo():
    """Redo last undone stroke"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        success = whiteboard_state['canvas'].redo()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/perfect-shape', methods=['POST'])
def perfect_shape():
    """Apply shape recognition to last stroke"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        success = whiteboard_state['canvas'].apply_shape_recognition()
        return jsonify({
            'success': success,
            'message': 'Shape converted' if success else 'Could not recognize shape'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/change-color', methods=['POST'])
def change_color():
    """Change drawing color"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        data = request.get_json()
        color_name = data.get('color')
        
        if color_name not in config.COLOR_ORDER:
            return jsonify({'error': f'Invalid color. Choose from: {config.COLOR_ORDER}'}), 400
        
        whiteboard_state['gesture_recognizer'].set_color_by_name(color_name)
        return jsonify({
            'success': True,
            'color': color_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/brush-size', methods=['POST'])
def change_brush_size():
    """Change brush size"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        data = request.get_json()
        size = data.get('size')
        
        if size is None:
            return jsonify({'error': 'Size parameter required'}), 400
        
        # Validate size
        size = int(size)
        if size < config.BRUSH_THICKNESS_MIN or size > config.BRUSH_THICKNESS_MAX:
            return jsonify({
                'error': f'Size must be between {config.BRUSH_THICKNESS_MIN} and {config.BRUSH_THICKNESS_MAX}'
            }), 400
        
        whiteboard_state['brush_thickness'] = size
        return jsonify({
            'success': True,
            'size': size
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/save', methods=['POST'])
def save_canvas():
    """Save canvas as PNG"""
    if whiteboard_state is None:
        return jsonify({'error': 'Whiteboard not initialized'}), 500
    
    try:
        file_handler = whiteboard_state['file_handler']
        export_path = file_handler.get_export_path()
        
        success = whiteboard_state['canvas'].save_as_png(export_path)
        
        if success:
            return jsonify({
                'success': True,
                'filename': export_path.split('/')[-1],
                'path': export_path
            })
        else:
            return jsonify({'error': 'Failed to save canvas'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/colors', methods=['GET'])
def get_colors():
    """Get available colors"""
    return jsonify({
        'colors': config.COLOR_ORDER,
        'current': whiteboard_state['gesture_recognizer'].get_current_color_name() if whiteboard_state else None
    })

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get whiteboard configuration"""
    return jsonify({
        'camera_width': config.CAMERA_WIDTH,
        'camera_height': config.CAMERA_HEIGHT,
        'brush_min': config.BRUSH_THICKNESS_MIN,
        'brush_max': config.BRUSH_THICKNESS_MAX,
        'brush_default': config.BRUSH_THICKNESS_DEFAULT,
        'colors': config.COLOR_ORDER,
        'max_history': config.MAX_HISTORY_SIZE
    })
