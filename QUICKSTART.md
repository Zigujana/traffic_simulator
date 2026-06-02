# QUICK START GUIDE

## Complete File List
Your traffic simulation package includes:

1. **traffic_simulation.py** - Main Python Flask application
2. **templates/index.html** - Web interface
3. **requirements.txt** - Python dependencies
4. **README.md** - Full documentation
5. **run.sh** - Linux/Mac startup script
6. **run.bat** - Windows startup script

## Fastest Way to Run (3 Steps):

### On Windows:
1. Extract all files to a folder
2. Double-click `run.bat`
3. Open browser to http://localhost:5000

### On Linux/Mac:
1. Extract all files to a folder
2. Open terminal in that folder and run: `./run.sh`
3. Open browser to http://localhost:5000

## Manual Method:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python traffic_simulation.py

# 3. Open your browser to:
http://localhost:5000
```

## Folder Structure Should Look Like:
```
your-folder/
├── traffic_simulation.py
├── templates/
│   └── index.html
├── requirements.txt
├── README.md
├── run.sh
└── run.bat
```

## Troubleshooting:

**Problem:** Port 5000 already in use
**Solution:** Edit traffic_simulation.py, line 223, change port=5000 to port=5001

**Problem:** Module not found
**Solution:** Run: pip install flask numpy

**Problem:** Template not found
**Solution:** Make sure the 'templates' folder is in the same directory as traffic_simulation.py

## Features to Try:

1. **Start** the simulation
2. **Adjust sliders** to see real-time effects
3. **Switch to Crossroad** mode to see traffic lights
4. **Change number of cars** to test traffic density
5. **Modify reaction time** to see traffic wave formation
6. **Reset** to reinitialize with new parameters

Enjoy your traffic simulation!
