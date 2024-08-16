# Subnet Traffic Rotator

## Overview

The **Subnet Traffic Rotator** is a Python program designed to help you to dynamically intercept the traffic from two AWS subnets in the same VPC (Virtual Private Cloud) by a security tool that is leveraging AWS Gateway loadbalancer technology, enabling enhanced monitoring, intrusion prevention, analysis of network activities and any further capabilities provided by the selected security tool.

This tool is particularly useful for network administrators, cloud architects, cloud developers, devops, devsecops and security professionals who want to ensure that their security tools are effectively intercepting and analyzing traffic from and to their services.

This tool works by creating an AWS Cloudformation template with a copy of the original route tables with the addition of a route in between them that targets the provided Gatewayloadbalancer VPC Endpoint, the outputed AWS Cloudformation can then be used to associate those new route tables to the targeted subnets.

## Features

Dynamic Route Management: Automatically rotate routes between two specified subnets.
Traffic Interception: Redirect traffic to a designated security tool for analysis.
Logging: Keep track of route changes and intercepted traffic for auditing purposes.
Cross-Platform: Works on Windows, macOS, and Linux.

## Limitations

The program have the following limitations at the moment:
    - Can only rotate the routes of 2 target subnets, here referenced as source (Public) and destination (Private)
        - Can be used to rotate the routes of 2 private subnets as well
    - Works per AZ (need to provide the 2 subnets that will be intercepted)
    - Not intended for edge deployment
    - Only applicable for deployments that are using Gateway load balancer, a Gateway Load Balancer endpoint must be provided
    - customer need to deploy and provide the vpc endpoint id
    - Works for hosted or customer owned appliance
    - Customer need to provide an aws S3 bucket for the logging to work
    - Does not add the S3 VPC endpoints back to the route tables

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

## Example

Topology AS-IS

![image](https://github.com/user-attachments/assets/6e81f796-39fa-4db2-a7c9-085141a2ec9d)

Topology after the Rotate_Routes program is run:

![image](https://github.com/user-attachments/assets/3037bdb6-0177-46ad-b05e-fd5abf699025)

## Logging
The program logs all route changes and intercepted traffic to traffic_log.txt. You can review this file to monitor activities and ensure the program is functioning as expected.

## Roadmap

This project will include the following features in the near future:
    - Create the Route Table for the Security Endpoint Subnet
    - Add the option to also intercept the traffic going to the Nat Gateway from the Private subnet
    - Add the S3 VPC Endpoints to the copied route tables, if any is present in the originals

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
Contact
For questions or support, please open an issue in the GitHub repository or send me a message at https://www.linkedin.com/in/vitor-cor%C3%A1-930948b0.
