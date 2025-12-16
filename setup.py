"""
Setup Script for Logistics AI Platform
Automated initialization and data generation
"""

import os
import sys
import subprocess

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n✓ {description}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"  ✅ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print_header("Logistics AI - Advanced Full-Stack Platform")
    print("\n🚀 Starting Setup Process...")
    
    # Step 1: Generate Data
    print_header("Step 1: Generating Synthetic Data")
    if not run_command(
        "python src/data/data_generator.py",
        "Generating fleet, orders, and historical demand data"
    ):
        print("\n⚠️ Warning: Data generation failed. Will use existing data if available.")
    
    # Step 2: Train ML Model
    print_header("Step 2: Training Demand Forecasting Model")
    if not run_command(
        "python src/models/demand_predictor.py",
        "Training RandomForest demand prediction model"
    ):
        print("\n⚠️ Warning: Model training failed. Forecasting may not work.")
    
    # Step 3: Initialize Database
    print_header("Step 3: Initializing Database")
    if not run_command(
        "python src/persistence/db_init.py",
        "Creating database schema and seeding initial data"
    ):
        print("\n❌ Error: Database initialization failed!")
        return
    
    # Success Message
    print_header("Setup Complete! 🎉")
    print("\n✅ All setup steps completed successfully!")
    print("\n📋 Default Login Credentials:")
    print("   Admin:      username='admin',      password='admin123'")
    print("   Manager:    username='manager',    password='manager123'")
    print("   Dispatcher: username='dispatcher', password='dispatch123'")
    print("   Driver:     username='driver1',    password='driver123'")
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then visit: http://localhost:5000")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
