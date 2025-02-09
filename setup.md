# Invisible Watermark Setup Guide

Welcome to the Invisible Watermark project! Follow this guide to set up the project step by step.

## Prerequisites
- Python 3.8 or later installed.
- Git (optional, if cloning from a repository).
- Basic command-line knowledge.

## Step 1: Clone or Download the Repository
If you have Git installed, open your terminal and run:
    
    git clone <repository_url>
    cd invisible_watermark

Alternatively, download the project as a ZIP file and extract it.

## Step 2: Create a Virtual Environment (Recommended)
Set up a virtual environment to manage dependencies. In your project directory, run:

    python -m venv venv

Activate the virtual environment:
- On Windows:
    
      venv\Scripts\activate

- On macOS/Linux:
    
      source venv/bin/activate

## Step 3: Install Dependencies
With the virtual environment activated, install the required libraries using pip:

    pip install -r requirements.txt

This command installs libraries like numpy, torch, scipy, Pillow, Flask, requests, and concrete-ml.

## Step 4: Understand the Project Structure
- **Readme.md:** Overview, features, and evaluation metrics.
- **setup.md:** This setup guide.
- **server/** and **client/** (if applicable): Contain server-client implementation details.
- **utils/:** Holds various utility functions.
- **zama_bounty.py:** Contains the main execution logic including FHE and watermark processing.

## Step 5: Running the Project
You can execute the project in different modes:

- **Server Mode:**  
      
      python zama_bounty.py --server

- **Client Mode:**  
      
      python zama_bounty.py --client

- **Default Mode:**  
If no additional argument is passed, the project will run its main function.

## Step 6: Configuring FHE Processing
The project leverages Concrete-ML for fully homomorphic encryption (FHE) processing. Key FHE parameters (such as n_bits, rounding_threshold, and p_error) can be adjusted in the source code as needed.


