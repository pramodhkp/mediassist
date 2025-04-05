# MediaAssist Demo Scripts

This directory contains scripts for setting up and demonstrating the MediaAssist application.

## Generate Demo Data

The `generate_demo_data.py` script creates mock data for the past two weeks and triggers the insights generation process. This is useful for demonstrating the application with realistic data.

### Prerequisites

1. Make sure MongoDB is running locally on the default port (27017)
2. Ensure the MediaAssist backend API is running (`python -m mediassist-backend.api.app`)
3. Install the required dependencies: `pip install -r ../requirements.txt`

### Running the Script

```bash
# From the mediassist-backend directory
python -m scripts.generate_demo_data

# Or from the scripts directory
cd scripts
python generate_demo_data.py
```

### What the Script Does

1. Creates a user profile with age, gender, height, and weight
2. Generates nutrition data entries for the past 14 days
3. Adds medical conditions (both chronic and temporary)
4. Triggers the API to generate and store daily and weekly insights

### After Running

After running the script, you can:

1. Access the daily insights at: http://localhost:5000/daily_insights
2. Access the weekly insights at: http://localhost:5000/weekly_insights
3. View the data in the frontend application

### Troubleshooting

If you encounter any issues:

1. Make sure MongoDB is running
2. Ensure the backend API is running and accessible
3. Check the console output for any error messages