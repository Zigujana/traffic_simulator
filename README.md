# Traffic Flow Simulation - Python-based Computational Model

A comprehensive web-based traffic flow simulation built with Python (Flask backend) and JavaScript (frontend visualization). Features Zimbabwe-style traffic light systems, advanced collision detection, predictive safety measures, and real-time parameter adjustment for sensitivity analysis.

## Features

### 🚗 Road Configurations
- **Two-Way Road**: Opposing traffic lanes with strict lane discipline
- **Crossroad**: 4-way intersection with Zimbabwe-standard traffic light control

### 🎯 Advanced Safety Systems
- **Collision Detection**: Real-time bounding box collision detection
- **Crush Prediction**: Cars calculate time-to-collision and brake preemptively
- **Safe Following Distance**: Automatic 2-second rule + minimum gap maintenance
- **Emergency Braking**: Multi-level braking system based on threat level
- **Adaptive Cruise Control**: Cars match speed of vehicle ahead when in comfort zone

### 🚦 Zimbabwe-Style Traffic Light System
- **RED**: Mandatory stop - no exceptions
- **AMBER**: Stop if safe to do so (calculates stopping distance vs distance to line)
- **GREEN**: Proceed normally
- **All-Red Phase**: Both directions red for 1 second during transition (intersection clearance)
- **Proper Sequencing**: Green → Amber → Red → All-Red → Other direction Green

### 📊 Adjustable Parameters
1. **Number of Cars** (5-50): Control traffic density
2. **Max Speed** (1-10): Set speed limit
3. **Acceleration** (0.1-1.0): How quickly cars speed up
4. **Deceleration** (0.1-2.0): Braking strength
5. **Minimum Gap** (10-100px): Base safe following distance
6. **Reaction Time** (0.1-2.0s): Driver response time for 2-second rule
7. **Green Light Duration** (2-10s): How long green phase lasts
8. **Amber Duration** (1-5s): Warning time before red

### 🎨 Visual Features
- **Safety Zones**: Green highlighted zones showing safe following distance
- **Brake Lights**: Red lights activate when car is stopped or slowing
- **Headlights**: Brightness varies with speed
- **3-Light Signals**: Realistic traffic lights with red, amber, and green
- **Stop Lines**: White lines marking stopping positions
- **Light Glow**: Active lights glow, inactive lights are dimmed

### 📈 Real-time Statistics
- Average speed of all vehicles
- Active car count
- Collision count (attempted overlaps prevented)
- Simulation status

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python traffic_simulation.py
   ```

3. **Access the Simulation**
   - Open your web browser
   - Navigate to: `http://localhost:5000`
   - The simulation interface will load automatically

## Usage Guide

### Starting the Simulation
1. Click **"Start Simulation"** to begin
2. Cars will start moving according to the current parameters
3. Traffic lights (in crossroad mode) will automatically cycle

### Adjusting Parameters
- Use the sliders in the left panel to modify parameters
- Changes take effect immediately
- Observe how traffic flow responds to each change

### Performing Sensitivity Analysis
1. **Baseline**: Start with default parameters and observe traffic flow
2. **Single Variable**: Change one parameter (e.g., increase Max Speed)
3. **Observe**: Watch how average speed and traffic patterns change
4. **Document**: Note the relationship between parameter and outcome
5. **Reset**: Return to baseline and test another parameter

### Road Type Switching
- Select **"Two-Way Road"** for simple opposing traffic
- Select **"Crossroad"** to add intersection with traffic lights
- The simulation will automatically reinitialize

### Reset Function
- Click **"Reset"** to reinitialize cars with current parameters
- Useful for comparing different configurations

## Computational Model

### Advanced Safety & Distance Management

The simulation implements a comprehensive multi-layered safety system:

#### 1. Safe Following Distance Calculation
```python
safe_distance = min_gap + (current_speed × reaction_time × 10)
```
This implements the **2-second rule**: maintain enough distance to react and stop safely.

#### 2. Collision Prediction & Prevention
Cars calculate:
- **Distance to vehicle ahead**: Using wrapped distance for continuous road
- **Closing speed**: Relative velocity between cars
- **Time to collision**: `distance / closing_speed`
- **Stopping distance**: `speed² / (2 × deceleration)`

#### 3. Multi-Zone Safety System

**Emergency Zone** (distance < 50% of safe distance):
- Immediate stop - potential crush detected
- Maximum braking force applied
- Collision counter incremented

**Critical Zone** (distance < 60% of safe distance):
- Heavy braking (2.5× normal deceleration)
- Prevents dangerous situations

**Warning Zone** (time to collision < 3 seconds):
- Predictive braking (1.5× normal deceleration)
- Adjusts speed to match vehicle ahead

**Safe Zone** (distance < safe distance):
- Gentle deceleration to maintain gap
- Target speed = 95% of vehicle ahead

**Comfort Zone** (distance < 1.5× safe distance):
- Adaptive cruise control
- Match speed of vehicle ahead

**Free Flow** (distance > 1.5× safe distance):
- Accelerate to max speed
- No constraints

### Zimbabwe-Style Traffic Light System

#### Traffic Light Phases
```
Horizontal: GREEN (5s) → AMBER (2s) → RED → ALL-RED (1s)
                                              ↓
Vertical:   RED → ALL-RED (1s) → GREEN (5s) → AMBER (2s) → RED
                  ↑_______________________________________________|
```

#### Light Rules Implementation

**RED Light**:
- Mandatory stop, no exceptions
- 3× deceleration force
- Stop before white stop line (80px before intersection)

**AMBER Light** (Zimbabwe Standard):
- Calculate: `stopping_distance = speed² / (2 × deceleration)`
- If `stopping_distance < 80% of distance_to_stop_line`: **STOP**
- Otherwise: **PROCEED** (too close to stop safely)
- Implements real-world "stop if you can safely do so" rule

**GREEN Light**:
- Proceed normally
- Maintain safe distance from vehicles ahead

**ALL-RED Phase** (Safety Clearance):
- Both directions RED for 1 second
- Allows intersection to clear
- Prevents side-impact collisions
- Standard practice in Zimbabwe traffic management

### Intelligent Driver Model (IDM)

The simulation uses a modified IDM with priority-based decision making:

**Priority 1**: Emergency collision avoidance (overrides all)  
**Priority 2**: Traffic light compliance (Zimbabwe rules)  
**Priority 3**: Maintain safe following distance  
**Priority 4**: Free flow acceleration  

Key equations:
- **Desired speed**: `v* = min(v_max, v_ahead × 0.95)` when following
- **Desired gap**: `s* = s_min + vT + v·Δv/(2√(a·b))`
- **Acceleration**: `a = a_max · (1 - (v/v*)⁴ - (s*/s)²)`

Where:
- `v`: Current speed
- `v_max`: Maximum allowed speed  
- `a_max`: Maximum acceleration
- `b`: Comfortable braking deceleration
- `s`: Current gap
- `s_min`: Minimum gap
- `T`: Desired time headway (reaction time)
- `Δv`: Speed difference to vehicle ahead

## Example Sensitivity Analysis

### Experiment 1: Impact of Reaction Time on Safety
**Objective**: Understand how driver reaction time affects collision prevention

1. **Baseline**: reaction_time = 0.5s
   - Observe: Moderate safe distances, occasional emergency braking
   
2. **Quick Reflexes**: reaction_time = 0.1s
   - Observe: Shorter following distances, less braking, higher throughput
   - Risk: Less margin for error
   
3. **Slow Reflexes**: reaction_time = 2.0s
   - Observe: Large gaps, smoother flow, more stable speeds
   - Benefit: Better safety margins, fewer near-misses

**Analysis**: Higher reaction times create traffic waves but improve safety

### Experiment 2: Traffic Density vs Collision Rate
**Objective**: Find optimal traffic density

1. **Light Traffic**: num_cars = 10
   - Result: Free flow, minimal braking, zero collisions
   - Average speed approaches max_speed
   
2. **Moderate Traffic**: num_cars = 25
   - Result: Some adaptive cruise control, occasional braking
   - Speed ~70% of max_speed
   
3. **Heavy Traffic**: num_cars = 50
   - Result: Stop-and-go waves, frequent braking, increased collision attempts
   - Speed ~40% of max_speed

**Analysis**: Collision risk increases exponentially with density

### Experiment 3: Minimum Gap Effect
**Objective**: Determine safe following distance requirements

1. **Tight Following**: min_gap = 10px
   - Observe: Cars very close, frequent emergency braking
   - High collision count, unstable flow
   
2. **Moderate Gap**: min_gap = 30px (default)
   - Observe: Balanced flow, occasional braking
   - Low collision count, stable speeds
   
3. **Large Gap**: min_gap = 100px
   - Observe: Very safe, smooth flow
   - Zero collisions, but lower road capacity

**Analysis**: Minimum gap of 30-50px optimal for safety vs capacity

### Experiment 4: Traffic Light Timing (Zimbabwe Standard)
**Objective**: Optimize intersection throughput while maintaining safety

1. **Short Cycle**: green = 2s, amber = 1s
   - Result: Frequent stops, low throughput
   - Many cars caught by red light
   
2. **Standard Cycle**: green = 5s, amber = 2s (Zimbabwe standard)
   - Result: Good throughput, safe amber clearance
   - Most cars can clear on amber if close
   
3. **Long Cycle**: green = 10s, amber = 5s
   - Result: High throughput one direction, long waits other direction
   - Risk of red-light running if amber too long

**Analysis**: 5-second green with 2-second amber optimal

### Experiment 5: Deceleration Capacity
**Objective**: Test braking system effectiveness

1. **Weak Brakes**: deceleration = 0.2
   - Observe: Long stopping distances, many collisions
   - Cars can't stop for red lights in time
   
2. **Normal Brakes**: deceleration = 0.5
   - Observe: Safe stops, good control
   - Proper response to traffic lights
   
3. **Performance Brakes**: deceleration = 2.0
   - Observe: Very short stops, jerky motion
   - Can stop from any speed quickly

**Analysis**: Deceleration of 0.5-1.0 balances safety and comfort

### Experiment 6: Speed Limit Impact
**Objective**: Analyze relationship between speed and safety

1. **Low Speed**: max_speed = 2
   - Result: Very safe, zero collisions
   - Low throughput, long travel times
   
2. **Medium Speed**: max_speed = 5
   - Result: Good balance, occasional emergency braking
   - Acceptable collision prevention
   
3. **High Speed**: max_speed = 10
   - Result: Higher throughput but more dangerous
   - Increased collision attempts, longer stopping distances

**Analysis**: Lower speeds safer but reduce capacity; optimal ~5-6 units

## Technical Architecture

```
traffic_simulation.py (Flask Backend)
├── TrafficSimulation class
│   ├── Car management
│   ├── IDM physics calculations
│   ├── Traffic light control
│   └── Statistics computation
└── REST API endpoints
    ├── /api/initialize
    ├── /api/update
    ├── /api/toggle_light
    ├── /api/update_params
    └── /api/reset

templates/index.html (Frontend)
├── Canvas rendering
├── Real-time visualization
├── Parameter controls
└── Statistics display
```

## API Endpoints

- **POST /api/initialize**: Initialize simulation with parameters
- **POST /api/update**: Update simulation state (called each frame)
- **POST /api/toggle_light**: Toggle traffic lights
- **POST /api/update_params**: Update simulation parameters
- **POST /api/reset**: Reset simulation

## Customization

### Modify Default Parameters
Edit the `params` dictionary in `traffic_simulation.py`:
```python
self.params = {
    'num_cars': 20,
    'max_speed': 5.0,
    # ... modify as needed
}
```

### Change Canvas Size
In `traffic_simulation.py`:
```python
self.canvas_width = 1000  # Change width
self.canvas_height = 600  # Change height
```

And in `templates/index.html`:
```html
<canvas id="simulationCanvas" width="1000" height="600"></canvas>
```

## Troubleshooting

### Port Already in Use
If port 5000 is busy, change it in `traffic_simulation.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Cars Not Moving
- Ensure simulation is started (click Start button)
- Check browser console for JavaScript errors
- Verify Flask server is running

### Performance Issues
- Reduce number of cars
- Decrease canvas size
- Close other browser tabs

## Research Applications

This simulation can be used to study:
- Traffic flow theory
- Congestion formation and propagation
- Impact of driver behavior on traffic
- Traffic light optimization
- Road capacity analysis
- Autonomous vehicle integration scenarios

## License

Free to use for educational and research purposes.

## Author

Created as a computational traffic flow model for simulation and analysis.
