"""
Shape Recognition Module
AI-powered shape detection with improved algorithms
Detects: Circle, Line, Rectangle, Triangle, Square, Arrow
"""

import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple
import config

class ShapeRecognizer:
    def __init__(self):
        """Initialize shape recognizer"""
        pass
    
    def recognize_shape(self, points: np.ndarray) -> Optional[Dict]:
        """
        Recognize shape from points
        
        Args:
            points: numpy array of (x, y) coordinates
            
        Returns:
            Dictionary with shape info or None if not recognized
        """
        if len(points) < config.MIN_POINTS_FOR_SHAPE:
            print("⚠️ Not enough points for shape recognition")
            return None
        
        # Try to recognize different shapes in order of specificity
        
        # 1. Try Circle (most distinctive)
        circle = self._detect_circle(points)
        if circle:
            return circle
        
        # 2. Try Line (second most distinctive)
        line = self._detect_line(points)
        if line:
            return line
        
        # 3. Try Arrow (before polygons)
        arrow = self._detect_arrow(points)
        if arrow:
            return arrow
        
        # 4. Try Polygons (Rectangle, Square, Triangle)
        polygon = self._detect_polygon(points)
        if polygon:
            return polygon
        
        print("❓ Could not recognize shape")
        return None
    
    def _detect_circle(self, points: np.ndarray) -> Optional[Dict]:
        """
        Detect if points form a circle
        
        Algorithm:
        - Calculate center point (mean of all points)
        - Calculate distance of each point from center
        - If standard deviation of distances is low, it's a circle
        """
        # Calculate center
        center = points.mean(axis=0).astype(int)
        center_x, center_y = center[0], center[1]
        
        # Calculate distances from center
        distances = np.linalg.norm(points - center, axis=1)
        avg_distance = distances.mean()
        std_distance = distances.std()
        
        # Check if it's circular (low variance in distances)
        if std_distance < avg_distance * config.CIRCLE_STD_THRESHOLD:
            print(f"✅ Detected CIRCLE - center: ({center_x}, {center_y}), radius: {int(avg_distance)}")
            return {
                'type': 'circle',
                'center': (center_x, center_y),
                'radius': int(avg_distance)
            }
        
        return None
    
    def _detect_line(self, points: np.ndarray) -> Optional[Dict]:
        """
        Detect if points form a straight line
        
        Algorithm:
        - Fit a line using linear regression
        - Calculate error (distance from fitted line)
        - If error is low, it's a line
        """
        if len(points) < 2:
            return None
        
        x = points[:, 0]
        y = points[:, 1]
        
        try:
            # Fit line using least squares
            slope, intercept = np.polyfit(x, y, 1)
            
            # Calculate predicted y values
            predicted_y = slope * x + intercept
            
            # Calculate mean error
            error = np.abs(y - predicted_y).mean()
            
            # Check if it's a straight line
            if error < config.LINE_ERROR_THRESHOLD:
                start_point = tuple(points[0].astype(int))
                end_point = tuple(points[-1].astype(int))
                
                print(f"✅ Detected LINE - from {start_point} to {end_point}")
                return {
                    'type': 'line',
                    'start': start_point,
                    'end': end_point
                }
        except:
            pass
        
        return None
    
    def _detect_polygon(self, points: np.ndarray) -> Optional[Dict]:
        """
        Detect polygons (triangle, rectangle, square)
        
        Algorithm:
        - Create convex hull
        - Approximate polygon
        - Count vertices
        """
        # Get convex hull
        hull = cv2.convexHull(points)
        
        # Approximate polygon
        epsilon = config.POLYGON_EPSILON * cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, epsilon, True)
        
        num_vertices = len(approx)
        
        # Triangle (3 vertices)
        if num_vertices == 3:
            print("✅ Detected TRIANGLE")
            return {
                'type': 'triangle',
                'points': approx.reshape(-1, 2).astype(int)
            }
        
        # Rectangle or Square (4 vertices)
        elif num_vertices == 4:
            # Check if it's a square (all sides approximately equal)
            points_2d = approx.reshape(-1, 2)
            
            # Calculate side lengths
            sides = []
            for i in range(4):
                p1 = points_2d[i]
                p2 = points_2d[(i + 1) % 4]
                length = np.linalg.norm(p1 - p2)
                sides.append(length)
            
            sides = np.array(sides)
            mean_side = sides.mean()
            std_side = sides.std()
            
            # If all sides are similar, it's a square
            if std_side < mean_side * config.SQUARE_SIDE_VARIANCE:
                print("✅ Detected SQUARE")
                return {
                    'type': 'square',
                    'points': approx.reshape(-1, 2).astype(int)
                }
            else:
                print("✅ Detected RECTANGLE")
                return {
                    'type': 'rectangle',
                    'points': approx.reshape(-1, 2).astype(int)
                }
        
        return None
    
    def _detect_arrow(self, points: np.ndarray) -> Optional[Dict]:
        """
        Detect arrow shape
        
        Simplified detection:
        - Check if roughly linear with deviation at one end
        - More complex arrow detection can be added later
        """
        # For now, return None (arrow detection is complex)
        # Can be implemented as: line + triangle at end
        return None
    
    def draw_perfect_shape(self, canvas: np.ndarray, shape_info: Dict, color: Tuple[int, int, int], thickness: int):
        """
        Draw the recognized shape perfectly on canvas
        
        Args:
            canvas: Image to draw on
            shape_info: Shape information from recognize_shape()
            color: BGR color
            thickness: Line thickness
        """
        shape_type = shape_info['type']
        
        if shape_type == 'circle':
            cv2.circle(
                canvas,
                shape_info['center'],
                shape_info['radius'],
                color,
                thickness
            )
        
        elif shape_type == 'line':
            cv2.line(
                canvas,
                shape_info['start'],
                shape_info['end'],
                color,
                thickness
            )
        
        elif shape_type in ['rectangle', 'square', 'triangle']:
            pts = shape_info['points'].reshape((-1, 1, 2))
            cv2.polylines(
                canvas,
                [pts],
                isClosed=True,
                color=color,
                thickness=thickness
            )
        
        elif shape_type == 'arrow':
            # Arrow drawing logic (to be implemented)
            pass
    
    def get_shape_bounding_box(self, points: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Get bounding box of shape (for clearing region)
        
        Returns:
            (x_min, y_min, x_max, y_max)
        """
        x_min = int(points[:, 0].min()) - 30
        y_min = int(points[:, 1].min()) - 30
        x_max = int(points[:, 0].max()) + 30
        y_max = int(points[:, 1].max()) + 30
        
        return (x_min, y_min, x_max, y_max)