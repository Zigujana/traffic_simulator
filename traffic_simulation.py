from flask import Flask, render_template, jsonify, request
import numpy as np
import json
from dataclasses import dataclass, asdict
from typing import List, Dict
import random

app = Flask(__name__)

@dataclass
class Car:
    id: str
    x: float
    y: float
    speed: float
    lane: str
    direction: str
    color: str
    max_speed: float = 5.0
    width: float = 30
    height: float = 16
    stopped_at_light: bool = False
    
class TrafficSimulation:
    def __init__(self):
        self.cars = []
        self.canvas_width = 1000
        self.canvas_height = 600
        self.lane_width = 40
        self.params = {
            'num_cars': 20,
            'max_speed': 5.0,
            'acceleration': 0.2,
            'deceleration': 0.5,
            'min_gap': 30,
            'reaction_time': 0.5,
            'road_type': 'twoWay',
            'traffic_light_duration': 5000,
            'amber_duration': 2000
        }
        self.traffic_lights = {
            'horizontal': 'green',
            'vertical': 'red'
        }
        self.light_timer = 0
        self.light_phase = 'green'  # 'green', 'amber', 'red'
        self.stats = {
            'avg_speed': 0,
            'collisions': 0,
            'throughput': 0
        }
        self.collision_count = 0
        
    def initialize_cars(self):
        """Initialize cars based on road type and parameters"""
        self.cars = []
        self.collision_count = 0
        num_cars = self.params['num_cars']
        road_type = self.params['road_type']
        
        # Minimum spacing to prevent initial overlaps
        min_spacing = 80
        
        if road_type == 'twoWay':
            cars_per_lane = num_cars // 2
            
            # Lane 1: Left to right (top lane)
            for i in range(cars_per_lane):
                self.cars.append(Car(
                    id=f"car-1-{i}",
                    x=(i * min_spacing) % self.canvas_width,
                    y=self.canvas_height / 2 - self.lane_width - 10,
                    speed=random.uniform(1.5, 3),
                    lane='1',
                    direction='right',
                    color=f"hsl({random.randint(0, 360)}, 70%, 50%)",
                    max_speed=self.params['max_speed']
                ))
            
            # Lane 2: Right to left (bottom lane)
            for i in range(cars_per_lane):
                self.cars.append(Car(
                    id=f"car-2-{i}",
                    x=self.canvas_width - (i * min_spacing) % self.canvas_width,
                    y=self.canvas_height / 2 + 10,
                    speed=random.uniform(1.5, 3),
                    lane='2',
                    direction='left',
                    color=f"hsl({random.randint(0, 360)}, 70%, 50%)",
                    max_speed=self.params['max_speed']
                ))
        else:  # crossroad
            cars_per_lane = num_cars // 4
            
            # Horizontal left to right
            for i in range(cars_per_lane):
                self.cars.append(Car(
                    id=f"car-h1-{i}",
                    x=(i * min_spacing) % self.canvas_width,
                    y=self.canvas_height / 2 - self.lane_width - 10,
                    speed=random.uniform(1.5, 3),
                    lane='h1',
                    direction='right',
                    color=f"hsl({random.randint(0, 360)}, 70%, 50%)",
                    max_speed=self.params['max_speed']
                ))
            
            # Horizontal right to left
            for i in range(cars_per_lane):
                self.cars.append(Car(
                    id=f"car-h2-{i}",
                    x=self.canvas_width - (i * min_spacing) % self.canvas_width,
                    y=self.canvas_height / 2 + 10,
                    speed=random.uniform(1.5, 3),
                    lane='h2',
                    direction='left',
                    color=f"hsl({random.randint(0, 360)}, 70%, 50%)",
                    max_speed=self.params['max_speed']
                ))
            
            # Vertical top to bottom
            for i in range(cars_per_lane):
                self.cars.append(Car(
                    id=f"car-v1-{i}",
                    x=self.canvas_width / 2 - self.lane_width - 10,
                    y=(i * min_spacing) % self.canvas_height,
                    speed=random.uniform(1.5, 3),
                    lane='v1',
                    direction='down',
                    color=f"hsl({random.randint(0, 360)}, 70%, 50%)",
                    max_speed=self.params['max_speed']
                ))
            
            # Vertical bottom to top
            for i in range(cars_per_lane):
                self.cars.append(Car(
                    id=f"car-v2-{i}",
                    x=self.canvas_width / 2 + 10,
                    y=self.canvas_height - (i * min_spacing) % self.canvas_height,
                    speed=random.uniform(1.5, 3),
                    lane='v2',
                    direction='up',
                    color=f"hsl({random.randint(0, 360)}, 70%, 50%)",
                    max_speed=self.params['max_speed']
                ))
    
    
    def cars_colliding(self, car1: Car, car2: Car) -> bool:
        """Check if two cars are colliding"""
        # Don't check collision with self or cars in different lanes
        if car1.id == car2.id or car1.lane != car2.lane:
            return False
        
        # For horizontal movement
        if car1.direction in ['right', 'left']:
            # Calculate wrapped distance
            dx = abs(car1.x - car2.x)
            if dx > self.canvas_width / 2:
                dx = self.canvas_width - dx
            dy = abs(car1.y - car2.y)
            
            # Check if bounding boxes overlap
            return dx < car1.width and dy < car1.height
        else:  # Vertical movement
            dx = abs(car1.x - car2.x)
            # Calculate wrapped distance
            dy = abs(car1.y - car2.y)
            if dy > self.canvas_height / 2:
                dy = self.canvas_height - dy
            
            # Check if bounding boxes overlap (width/height swapped for vertical)
            return dx < car1.height and dy < car1.width
    
    def find_car_ahead(self, car: Car) -> tuple:
        """Find the car ahead in the same lane"""
        min_distance = float('inf')
        car_ahead = None
        
        for other_car in self.cars:
            if other_car.id == car.id or other_car.lane != car.lane:
                continue
            
            distance = 0
            if car.direction == 'right':
                distance = other_car.x - car.x
                if distance < 0:
                    distance += self.canvas_width
            elif car.direction == 'left':
                distance = car.x - other_car.x
                if distance < 0:
                    distance += self.canvas_width
            elif car.direction == 'down':
                distance = other_car.y - car.y
                if distance < 0:
                    distance += self.canvas_height
            else:  # up
                distance = car.y - other_car.y
                if distance < 0:
                    distance += self.canvas_height
            
            if 0 < distance < min_distance:
                min_distance = distance
                car_ahead = other_car
        
        return car_ahead, min_distance
    
    def check_traffic_light(self, car: Car) -> tuple:
        """
        Check if car should stop at traffic light (Zimbabwe traffic rules)
        - RED: Mandatory stop
        - AMBER: Stop if safe to do so, otherwise proceed with caution
        - GREEN: Proceed
        """
        if self.params['road_type'] != 'crossroad':
            return False, None
        
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Stop line is 80 pixels before intersection center
        stop_line_distance = 80
        # Detection starts 200 pixels before intersection
        detection_distance = 200
        # Point of no return (too close to safely stop)
        point_of_no_return = 30
        
        # Horizontal lanes (East-West traffic)
        if car.lane in ['h1', 'h2']:
            light_color = self.traffic_lights['horizontal']
            
            if car.direction == 'right':
                distance_to_intersection = center_x - car.x
                # Handle wrap-around
                if distance_to_intersection < -self.canvas_width / 2:
                    distance_to_intersection += self.canvas_width
                    
                if 0 < distance_to_intersection < detection_distance:
                    # Already past stop line - must continue
                    if distance_to_intersection < point_of_no_return:
                        return False, light_color
                    
                    # RED LIGHT: Mandatory stop
                    if light_color == 'red':
                        if distance_to_intersection > stop_line_distance:
                            return True, 'red'
                        else:
                            # In intersection, clear it
                            return False, 'red'
                    
                    # AMBER LIGHT: Zimbabwe rule - stop if you can safely do so
                    elif light_color == 'amber':
                        # Calculate if we can stop safely
                        stopping_distance = (car.speed ** 2) / (2 * self.params['deceleration'] * 10)
                        distance_to_stop_line = distance_to_intersection - stop_line_distance
                        
                        # Can stop safely before line
                        if stopping_distance < distance_to_stop_line * 0.8:
                            return True, 'amber'
                        # Too close or too fast - proceed through
                        else:
                            return False, 'amber'
                    
                    # GREEN: Proceed normally
                    else:
                        return False, 'green'
                        
            elif car.direction == 'left':
                distance_to_intersection = car.x - center_x
                if distance_to_intersection < -self.canvas_width / 2:
                    distance_to_intersection += self.canvas_width
                    
                if 0 < distance_to_intersection < detection_distance:
                    if distance_to_intersection < point_of_no_return:
                        return False, light_color
                    
                    if light_color == 'red':
                        if distance_to_intersection > stop_line_distance:
                            return True, 'red'
                        else:
                            return False, 'red'
                    elif light_color == 'amber':
                        stopping_distance = (car.speed ** 2) / (2 * self.params['deceleration'] * 10)
                        distance_to_stop_line = distance_to_intersection - stop_line_distance
                        if stopping_distance < distance_to_stop_line * 0.8:
                            return True, 'amber'
                        else:
                            return False, 'amber'
                    else:
                        return False, 'green'
        
        # Vertical lanes (North-South traffic)
        if car.lane in ['v1', 'v2']:
            light_color = self.traffic_lights['vertical']
            
            if car.direction == 'down':
                distance_to_intersection = center_y - car.y
                if distance_to_intersection < -self.canvas_height / 2:
                    distance_to_intersection += self.canvas_height
                    
                if 0 < distance_to_intersection < detection_distance:
                    if distance_to_intersection < point_of_no_return:
                        return False, light_color
                    
                    if light_color == 'red':
                        if distance_to_intersection > stop_line_distance:
                            return True, 'red'
                        else:
                            return False, 'red'
                    elif light_color == 'amber':
                        stopping_distance = (car.speed ** 2) / (2 * self.params['deceleration'] * 10)
                        distance_to_stop_line = distance_to_intersection - stop_line_distance
                        if stopping_distance < distance_to_stop_line * 0.8:
                            return True, 'amber'
                        else:
                            return False, 'amber'
                    else:
                        return False, 'green'
                        
            elif car.direction == 'up':
                distance_to_intersection = car.y - center_y
                if distance_to_intersection < -self.canvas_height / 2:
                    distance_to_intersection += self.canvas_height
                    
                if 0 < distance_to_intersection < detection_distance:
                    if distance_to_intersection < point_of_no_return:
                        return False, light_color
                    
                    if light_color == 'red':
                        if distance_to_intersection > stop_line_distance:
                            return True, 'red'
                        else:
                            return False, 'red'
                    elif light_color == 'amber':
                        stopping_distance = (car.speed ** 2) / (2 * self.params['deceleration'] * 10)
                        distance_to_stop_line = distance_to_intersection - stop_line_distance
                        if stopping_distance < distance_to_stop_line * 0.8:
                            return True, 'amber'
                        else:
                            return False, 'amber'
                    else:
                        return False, 'green'
        
        return False, None
    
    def update_car(self, car: Car, dt: float) -> Car:
        """Update car position with comprehensive safety checks and crush prediction"""
        car_ahead, distance = self.find_car_ahead(car)
        stop_at_light, light_color = self.check_traffic_light(car)
        
        # Calculate safe following distance based on speed (2-second rule + minimum gap)
        safe_distance = self.params['min_gap'] + (car.speed * self.params['reaction_time'] * 10)
        
        # Emergency distance (critical zone)
        emergency_distance = self.params['min_gap'] * 0.5
        
        new_speed = car.speed
        
        # PRIORITY 1: Emergency collision avoidance
        if car_ahead and distance < emergency_distance:
            # EMERGENCY BRAKE - potential crush detected
            new_speed = 0
            self.collision_count += 1
            
        # PRIORITY 2: Traffic light compliance (Zimbabwe style - strict adherence)
        elif stop_at_light:
            if light_color == 'red':
                # RED: Complete stop, no exceptions
                new_speed = max(0, car.speed - self.params['deceleration'] * 3 * dt)
            elif light_color == 'amber':
                # AMBER: Prepare to stop if safe distance allows
                # In Zimbabwe, amber means "stop if you can safely do so"
                if car.speed > 2.5:  # Going fast, might not stop safely
                    # Continue through but don't accelerate
                    new_speed = car.speed
                else:
                    # Slow down to stop
                    new_speed = max(0, car.speed - self.params['deceleration'] * 1.5 * dt)
                    
        # PRIORITY 3: Maintain safe following distance
        elif car_ahead:
            # Calculate relative speed (closing speed)
            closing_speed = car.speed - car_ahead.speed
            
            # Time to collision if speeds don't change
            if closing_speed > 0 and distance > 0:
                time_to_collision = distance / (closing_speed * 10)
            else:
                time_to_collision = float('inf')
            
            # CRITICAL ZONE: Too close, immediate braking
            if distance < safe_distance * 0.6:
                new_speed = max(0, car.speed - self.params['deceleration'] * 2.5 * dt)
                
            # WARNING ZONE: Approaching too fast
            elif time_to_collision < 3.0 and closing_speed > 0:
                # Predictive braking - adjust to match speed of car ahead
                new_speed = max(0, car.speed - self.params['deceleration'] * 1.5 * dt)
                
            # SAFE ZONE: Maintain safe distance
            elif distance < safe_distance:
                # Gentle deceleration to maintain safe gap
                target_speed = car_ahead.speed * 0.95  # Slightly slower than car ahead
                if car.speed > target_speed:
                    new_speed = max(target_speed, car.speed - self.params['deceleration'] * dt)
                else:
                    new_speed = min(car.max_speed, car.speed + self.params['acceleration'] * 0.5 * dt)
                    
            # COMFORT ZONE: Good distance, match speed
            elif distance < safe_distance * 1.5:
                # Adaptive cruise - match the car ahead
                target_speed = car_ahead.speed
                if car.speed > target_speed:
                    new_speed = max(target_speed, car.speed - self.params['acceleration'] * dt)
                elif car.speed < target_speed and car.speed < car.max_speed:
                    new_speed = min(car.max_speed, car.speed + self.params['acceleration'] * 0.5 * dt)
                    
            # FREE FLOW: Plenty of room
            else:
                if car.speed < car.max_speed:
                    new_speed = min(car.max_speed, car.speed + self.params['acceleration'] * dt)
                    
        # PRIORITY 4: Free flow (no obstacles)
        else:
            if car.speed < car.max_speed:
                new_speed = min(car.max_speed, car.speed + self.params['acceleration'] * dt)
        
        # Calculate new position
        new_x, new_y = car.x, car.y
        
        if car.direction == 'right':
            new_x = (car.x + new_speed * dt * 10) % self.canvas_width
        elif car.direction == 'left':
            new_x = (car.x - new_speed * dt * 10 + self.canvas_width) % self.canvas_width
        elif car.direction == 'down':
            new_y = (car.y + new_speed * dt * 10) % self.canvas_height
        else:  # up
            new_y = (car.y - new_speed * dt * 10 + self.canvas_height) % self.canvas_height
        
        # Create temporary car with new position to verify no collision
        temp_car = Car(
            id=car.id,
            x=new_x,
            y=new_y,
            speed=new_speed,
            lane=car.lane,
            direction=car.direction,
            color=car.color,
            max_speed=car.max_speed
        )
        
        # Final collision check - if position would cause overlap, don't move
        collision_detected = False
        for other_car in self.cars:
            if self.cars_colliding(temp_car, other_car):
                collision_detected = True
                break
        
        if collision_detected:
            # Don't move, stop completely
            new_speed = 0
            new_x = car.x
            new_y = car.y
        
        car.x = new_x
        car.y = new_y
        car.speed = new_speed
        car.stopped_at_light = stop_at_light
        
        return car
    
    def update(self, dt: float):
        """Update all cars in the simulation"""
        self.cars = [self.update_car(car, dt) for car in self.cars]
        
        # Update statistics
        if self.cars:
            self.stats['avg_speed'] = sum(car.speed for car in self.cars) / len(self.cars)
            self.stats['collisions'] = self.collision_count
        
    def update_traffic_lights(self, dt_ms: float):
        """Update traffic lights with Zimbabwe-style timing and safety phases"""
        if self.params['road_type'] != 'crossroad':
            return
        
        self.light_timer += dt_ms
        
        green_duration = self.params['traffic_light_duration']
        amber_duration = self.params['amber_duration']
        # All-red phase: Both directions red for safety clearance (Zimbabwe standard)
        all_red_duration = 1000  # 1 second all-red for intersection clearance
        
        # State machine for Zimbabwe-style traffic light sequence
        # Horizontal priority cycle: H-Green -> H-Amber -> All-Red -> V-Green -> V-Amber -> All-Red -> repeat
        
        if self.traffic_lights['horizontal'] == 'green' and self.traffic_lights['vertical'] == 'red':
            # Phase 1: Horizontal GREEN, Vertical RED
            if self.light_timer >= green_duration:
                self.traffic_lights['horizontal'] = 'amber'
                self.light_timer = 0
                
        elif self.traffic_lights['horizontal'] == 'amber' and self.traffic_lights['vertical'] == 'red':
            # Phase 2: Horizontal AMBER (warning), Vertical RED
            if self.light_timer >= amber_duration:
                self.traffic_lights['horizontal'] = 'red'
                self.traffic_lights['vertical'] = 'red'  # All-red phase
                self.light_phase = 'all_red_before_vertical'
                self.light_timer = 0
                
        elif self.light_phase == 'all_red_before_vertical':
            # Phase 3: ALL RED (safety clearance for intersection)
            if self.light_timer >= all_red_duration:
                self.traffic_lights['horizontal'] = 'red'
                self.traffic_lights['vertical'] = 'green'
                self.light_phase = 'green'
                self.light_timer = 0
                
        elif self.traffic_lights['vertical'] == 'green' and self.traffic_lights['horizontal'] == 'red':
            # Phase 4: Vertical GREEN, Horizontal RED
            if self.light_timer >= green_duration:
                self.traffic_lights['vertical'] = 'amber'
                self.light_timer = 0
                
        elif self.traffic_lights['vertical'] == 'amber' and self.traffic_lights['horizontal'] == 'red':
            # Phase 5: Vertical AMBER (warning), Horizontal RED
            if self.light_timer >= amber_duration:
                self.traffic_lights['horizontal'] = 'red'
                self.traffic_lights['vertical'] = 'red'  # All-red phase
                self.light_phase = 'all_red_before_horizontal'
                self.light_timer = 0
                
        elif self.light_phase == 'all_red_before_horizontal':
            # Phase 6: ALL RED (safety clearance for intersection)
            if self.light_timer >= all_red_duration:
                self.traffic_lights['horizontal'] = 'green'
                self.traffic_lights['vertical'] = 'red'
                self.light_phase = 'green'
                self.light_timer = 0
    
    def toggle_traffic_light(self):
        """Legacy method - kept for compatibility but not used"""
        pass
    
    def get_state(self) -> Dict:
        """Get current simulation state"""
        return {
            'cars': [asdict(car) for car in self.cars],
            'stats': self.stats,
            'traffic_lights': self.traffic_lights,
            'params': self.params
        }

# Global simulation instance
simulation = TrafficSimulation()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize simulation with parameters"""
    data = request.json
    if data:
        simulation.params.update(data)
    simulation.initialize_cars()
    return jsonify(simulation.get_state())

@app.route('/api/update', methods=['POST'])
def update():
    """Update simulation state"""
    data = request.json
    dt = data.get('dt', 0.016)  # Default to ~60fps
    dt_ms = data.get('dt_ms', 16)  # Milliseconds for traffic light timing
    
    simulation.update(dt)
    simulation.update_traffic_lights(dt_ms)
    
    return jsonify(simulation.get_state())

@app.route('/api/toggle_light', methods=['POST'])
def toggle_light():
    """Toggle traffic lights"""
    simulation.toggle_traffic_light()
    return jsonify(simulation.get_state())

@app.route('/api/update_params', methods=['POST'])
def update_params():
    """Update simulation parameters"""
    data = request.json
    simulation.params.update(data)
    return jsonify({'status': 'success', 'params': simulation.params})

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset simulation"""
    simulation.initialize_cars()
    simulation.stats = {'avg_speed': 0, 'collisions': 0, 'throughput': 0}
    simulation.collision_count = 0
    simulation.light_timer = 0
    simulation.traffic_lights = {'horizontal': 'green', 'vertical': 'red'}
    return jsonify(simulation.get_state())

if __name__ == '__main__':
    simulation.initialize_cars()
    app.run(debug=True, host='0.0.0.0', port=5000)
