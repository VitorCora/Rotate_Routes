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

## Prerequisites

Before running the program, ensure you have the following installed:

Python 3.6 or higher
Required libraries (listed in requirements.txt):
    - boto3

## Installation

Clone the repository and open the cloned folder:
```
git clone https://github.com/VitorCora/Rotate_Routes.git
cd Rotate_Routes
```

## Install the required packages:

```
pip3 install -r requirements.txt
```

## Usage

You need to pass the parameters when you run the command:

```
python3 rotateroutes.py --vpcendpoint <VPC_Endpoint_ID> --subnet1 <Subnet1_ID> --subnet2 <Subnet2_ID> --s3bucket <S3Bucket_Name>
```

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

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Python - The programming language used for this project.
Your Security Tool - The tool used for traffic interception.
Contact
For questions or support, please open an issue in the GitHub repository or contact me at [your-email@example.com].


python3 rotateroutes.py --vpcendpoint=vpce-036d90bd427263372 --subnet1=subnet-063e0838ea01c2200 --subnet2=subnet-0919c23bc6e593883 --s3bucket=nsroutelogs
