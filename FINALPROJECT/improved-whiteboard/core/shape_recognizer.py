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
        # Check line FIRST (most distinctive - low variance in one direction)
        
        # 1. Try Line (check first - very distinctive)
        line = self._detect_line(points)
        if line:
            return line
        
        # 2. Try Circle (second - needs consistent radius)
        circle = self._detect_circle(points)
        if circle:
            return circle
        
        # 3. Try Arrow (before polygons)
        arrow = self._detect_arrow(points)
        if arrow:
            return arrow
        
        # 4. Try Polygons last (Rectangle, Square, Triangle)
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
        - Check if start and end points are close (closed loop)
        - If standard deviation of distances is low, it's a circle
        """
        # Check if path is closed (start and end points close together)
        start_point = points[0]
        end_point = points[-1]
        closure_distance = np.linalg.norm(start_point - end_point)
        
        # If not closed, probably not a circle
        avg_point_distance = np.linalg.norm(points[1:] - points[:-1], axis=1).mean()
        if closure_distance > avg_point_distance * 5:  # Not closed
            return None
        
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
        
        Better approach:
        - Arrow = straight line + V-shape at one end
        - Check if points form mostly straight path with deviation at end
        """
        if len(points) < 20:  # Need enough points
            return None
        
        # First check if it's reasonably linear overall
        x = points[:, 0]
        y = points[:, 1]
        
        try:
            # Fit line to all points
            slope, intercept = np.polyfit(x, y, 1)
            predicted_y = slope * x + intercept
            overall_error = np.abs(y - predicted_y).mean()
            
            # If not reasonably linear, not an arrow
            if overall_error > 40:  # Too curved
                return None
            
            # Now check each end separately
            # Split into three sections: start 30%, middle 40%, end 30%
            third = len(points) // 3
            start_section = points[:third]
            end_section = points[-third:]
            
            # Check straightness of each end
            def check_straightness(section):
                if len(section) < 3:
                    return 999
                sx = section[:, 0]
                sy = section[:, 1]
                try:
                    s_slope, s_intercept = np.polyfit(sx, sy, 1)
                    s_predicted = s_slope * sx + s_intercept
                    return np.abs(sy - s_predicted).mean()
                except:
                    return 999
            
            start_error = check_straightness(start_section)
            end_error = check_straightness(end_section)
            
            # If one end is significantly less straight (has the arrow head)
            if start_error > end_error * 1.5 and start_error > 15:
                # Arrow head at start
                print(f"✅ Detected ARROW - head at START")
                return {
                    'type': 'arrow',
                    'tail': tuple(points[-1].astype(int)),
                    'head': tuple(points[0].astype(int)),
                    'points': points
                }
            elif end_error > start_error * 1.5 and end_error > 15:
                # Arrow head at end
                print(f"✅ Detected ARROW - head at END")
                return {
                    'type': 'arrow',
                    'tail': tuple(points[0].astype(int)),
                    'head': tuple(points[-1].astype(int)),
                    'points': points
                }
        except:
            pass
        
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
            # Draw arrow shaft (line)
            cv2.line(
                canvas,
                shape_info['tail'],
                shape_info['head'],
                color,
                thickness
            )
            
            # Draw arrow head (simple triangle)
            # Calculate arrow head points
            tail = np.array(shape_info['tail'])
            head = np.array(shape_info['head'])
            
            # Direction vector
            direction = head - tail
            length = np.linalg.norm(direction)
            if length > 0:
                direction = direction / length
                
                # Perpendicular vector
                perp = np.array([-direction[1], direction[0]])
                
                # Arrow head size (proportional to thickness)
                head_length = thickness * 3
                head_width = thickness * 2
                
                # Calculate arrow head points
                p1 = head - direction * head_length + perp * head_width
                p2 = head - direction * head_length - perp * head_width
                
                # Draw filled arrow head
                triangle = np.array([head, p1, p2], dtype=np.int32)
                cv2.fillPoly(canvas, [triangle], color)
    
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
