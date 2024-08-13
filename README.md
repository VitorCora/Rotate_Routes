# Subnet Traffic Rotator

## Overview

The **Subnet Traffic Rotator** is a Python program designed to help you to dynamically intercept the traffic from two AWS subnets in the same VPC (Virtual Private Cloud) by a security tool that is leveraging AWS Gateway loadbalancer technology, enabling enhanced monitoring, intrusion prevention, analysis of network activities and any further capabilities provided by the selected security tool.

This tool is particularly useful for network administrators, cloud architects, cloud developers, devops, devsecops and security professionals who want to ensure that their security tools are effectively intercepting and analyzing traffic from and to their services.

This tool works by creating an AWS Cloudformation template with a copy of the original route tables with the addition of a route in between them that targets the provided Gatewayloadbalancer VPC Endpoint, the outputed AWS Cloudformation can then be used to associate those new route tables to the targeted subnets.

## Features

Dynamic Route Management: Automatically rotate routes between two specified subnets.
Traffic Interception: Redirect traffic to a designated security tool for analysis.
Configurable: Easily modify subnet addresses and security tool endpoints.
Logging: Keep track of route changes and intercepted traffic for auditing purposes.
Cross-Platform: Works on Windows, macOS, and Linux.
Prerequisites
Before running the program, ensure you have the following installed:

Python 3.6 or higher
Required libraries (listed in requirements.txt)
Installation
Clone the repository:

git clone https://github.com/yourusername/subnet-traffic-rotator.git
cd subnet-traffic-rotator
Install the required packages:

pip install -r requirements.txt
Configure the config.json file with your subnet details and security tool endpoint.

## Usage
The program uses a config.json file for configuration. Below is an example of how to structure this file:

{
    "subnet1": {
        "address": "192.168.1.0/24",
        "gateway": "192.168.1.1"
    },
    "subnet2": {
        "address": "192.168.2.0/24",
        "gateway": "192.168.2.1"
    },
    "security_tool": {
        "endpoint": "http://security-tool.local:8080"
    },
    "rotation_interval": 60
}
subnet1 and subnet2: Define the addresses and gateways of the subnets you want to rotate.
security_tool: Specify the endpoint of your security tool.
rotation_interval: Set the time interval (in seconds) for how often the routes should be rotated.
Usage
To run the program, execute the following command:

python subnet_traffic_rotator.py
The program will start rotating the routes between the two subnets based on the specified interval.

## Logging
The program logs all route changes and intercepted traffic to traffic_log.txt. You can review this file to monitor activities and ensure the program is functioning as expected.

## Contributing
Contributions are welcome! If you'd like to enhance the functionality or fix bugs, please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/YourFeature).
Make your changes.
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/YourFeature).
Open a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Python - The programming language used for this project.
Your Security Tool - The tool used for traffic interception.
Contact
For questions or support, please open an issue in the GitHub repository or contact me at [your-email@example.com].
