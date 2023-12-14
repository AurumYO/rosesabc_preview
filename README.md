# Your Project Name

[![Build Status](https://travis-ci.org/AurumYO/yourproject.svg?branch=main)](https://travis-ci.org/AurumYO/rosesabc_preview.git)

## Description

A digital Encyclopedia of roses. Here gathered all information on rose varieties and a catalogue of articles on growing roses.

## Features

- Bilingual (English / Ukrainian) interface and content. The multilanguage supprt is build with django-parler library; 
- User authentication and authorization system
- Search functionality with advanced filters
- Multi-language support
- Posibility to share with content via mail
- Customizable user profiles
- Support for file uploads
- Automated testinggit add .
- RESTful API (only few features due to luck of necessity so far)

## Screenshots

![Home page from a Desktop](rosesabc/screenshots/prototype_site_1.jpg)
![User page with list of all downloaded photos, from a Desktop](rosesabc/screenshots/prototype_site_2.jpg)
![New User registration form, Mobile view](rosesabc/screenshots/prototype_site_3.jpg)

## Installation

The installation process is described bellow. However note, that the code provided in given repository is only for preliminary review of the application. 
Since the application is alive non-profit project, the full code is not provided in given repository.

```bash
# Clone the repository
git clone https://github.com/AurumYO/rosesabc_preview.git

# Change into the project directory
cd yourproject

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver