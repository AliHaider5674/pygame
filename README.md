Table of Contents
Overview

Getting Started

Prerequisites

Installation

Usage

Testing

Overview
Add a brief description of your project here. What does it do? What problem does it solve?

Getting Started
Prerequisites
This project requires the following dependencies:

Programming Language: Python

Package Manager: Conda

Installation
Build Pygame from the source and install dependencies:

Clone the repository:

❯ git clone https://github.com/AliHaider5674/pygame

Navigate to the project directory:

❯ cd pygame

Install the dependencies:

Using conda:

❯ conda env create -f conda.yml

Usage
Run the project with:

Using conda:

conda activate {venv}
python {entrypoint}

Testing
Pygame uses the {test_framework} test framework. Run the test suite with:

Using conda:

conda activate {venv}
pytest
