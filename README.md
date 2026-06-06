# Containerized Deployment

A Python-based project with Docker support for containerized deployments.

## Overview

This repository contains quiz-related code and configurations for running in containerized environments. It demonstrates best practices for deploying Python applications using Docker containers for consistency across development, testing, and production environments.

## Technology Stack

- **Python** (72.6%) - Core application logic
- **Dockerfile** (27.4%) - Container configuration

## Project Purpose

This project is designed to:
- Provide a scalable quiz application that can run in containerized environments
- Demonstrate Docker containerization best practices
- Enable seamless deployment across different platforms and environments
- Maintain consistency between development and production setups

## Features

- Python-based quiz application
- Docker containerization for easy deployment
- Environment-agnostic setup
- Docker support for isolated execution environments

## Getting Started

### Prerequisites
- Python 3.x
- Docker (optional, for containerized deployment)

### Installation

Clone the repository:
```bash
git clone https://github.com/arhamheer/quiz-3.git
cd quiz-3
```

### Running Locally

To run the application locally without Docker:
```bash
python -m pip install -r requirements.txt
python app.py
```

### Running with Docker

Build the Docker image:
```bash
docker build -t quiz-3 .
```

Run the container:
```bash
docker run -p 5000:5000 quiz-3
```

## Project Structure

The project includes:
- **Python application files** - Core quiz logic and application code
- **Dockerfile** - Container configuration for deployment
- **requirements.txt** - Python dependencies
