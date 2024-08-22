import argparse
import sys
import boto3
import json
import logging
from datetime import datetime

#Clean up lambda

def generate_template_lambda(subnet_ids, subnet_routetable_ids):
    templatelambdarevert = {
        "LambdaExecutionRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                },
                "Policies": [
                    {
                        "PolicyName": "LambdaExecutionPolicy",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ec2:AssociateRouteTable"
                                    ],
                                    "Resource": "*"
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "RevertRoutesLambda": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Handler": "index.lambda_handler",
                "Role": {
                    "Fn::GetAtt": [
                        "LambdaExecutionRole",
                        "Arn"
                    ]
                },
                "Code": {
                    "ZipFile": "import boto3\nimport json\nimport logging\nimport cfnresponse\n\nlogger = logging.getLogger()\nlogger.setLevel(logging.INFO)\n\nec2 = boto3.client('ec2')\n\n\ndef lambda_handler(event, context):\n    logger.info(f\"Received event: {json.dumps(event)}\")\n    \n    request_type = event['RequestType']\n    properties = event['ResourceProperties']\n    \n    subnet_id = properties['Subnet1Id']\n    original_route_table_id = properties['RouteTable1Id']\n    second_subnet_id = properties['Subnet2Id']\n    second_route_table_id = properties['RouteTable2Id']\n    \n    if request_type in ['Create', 'Update']:\n        try:\n            # Perform necessary actions for create/update\n            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})\n        except Exception as e:\n            logger.error(f\"Failed to process {request_type} event: {e}\")\n            cfnresponse.send(event, context, cfnresponse.FAILED, {\"Message\": str(e)})\n    elif request_type == 'Delete':\n        try:\n            # Revert the route table association to the original one\n            ec2.associate_route_table(\n                SubnetId=subnet_id,\n                RouteTableId=original_route_table_id\n            )\n            # Associate the second route table with the second subnet\n            ec2.associate_route_table(\n                SubnetId=second_subnet_id,\n                RouteTableId=second_route_table_id\n            )\n            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})\n        except Exception as e:\n            logger.error(f\"Failed to associate route table: {e}\")\n            cfnresponse.send(event, context, cfnresponse.FAILED, {\"Message\": str(e)})\n"
                },
                "Runtime": "python3.8",
                "Timeout": 300
            }
        }
    }
    return templatelambdarevert

# Create AWS Cloudformation template and upload

def create_templatefile(template,s3name, account_id, vpc_id,current_time):
    #Set Status
    status="INFO"
    #Set message
    message = "AWS CloudFormation file created successfully"
    file_path = f"TrendNetworkSecurity_NewRoutes{current_time}.json"
    # Open the file in write mode ('w')
    with open(file_path, "w") as file:
        # Write the JSON dictionary to the file
        file.write(json.dumps(template, indent=4))
    # Close the file
    file.close()
    urlmessage = uploadtemplate_to_s3(s3name, file_path, account_id, vpc_id)
    return urlmessage

def uploadtemplate_to_s3(s3name, file_path, account_id, vpc_id):
    # Create an S3 client
    s3 = boto3.client('s3')
    # Create the folder key with a trailing slash
    folder_key = account_id +'/'+ vpc_id+'/'+file_path  
    s3.upload_file(file_path, s3name, folder_key)
    print("File uploaded to S3 bucket.")
    urlmessage = f"https://{s3name}.s3.amazonaws.com/{folder_key}"
    return urlmessage

def create_log_file(filename):
    #Acquire Time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # Configure logging
    file_path = filename+".log"
    #Set Status
    status="INFO"
    #Set message
    message = f"Log file created successfully, named {file_path}"
    print (message)
    # Open the file in write mode ('w')
    with open(file_path, "w") as file:
        # Perform operations on the file
        file.write(f"{current_time} {status} {message}\n")
    # Close the file
    file.close()

def log_to_logfile(filename, message, status):
    #Acquire Time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # Configure logging
    file_path = filename+".log"
    # Open the file in append mode ('a')
    with open(file_path, "a") as file:
        # Perform operations on the file
        file.write(f"{current_time} {status} {message}\n")
    # Close the file
    file.close()
  
def create_s3_folder(s3name, filename, account_id, vpc_id):
    # Create an S3 client
    s3 = boto3.client('s3')
    # Configure logging
    file_path = filename+".log"
    # Create the folder key with a trailing slash
    folder_key = account_id +'/'+ vpc_id+'/'+file_path
    print(folder_key)
    #Acquire Time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    #Set Status
    status="INFO"
    #Set message
    message = "Log folder created successfully for account id="+account_id+" and vpc id="+vpc_id
    # Open the file in append mode ('a')
    with open(file_path, "a") as file:
        # Perform operations on the file
        file.write(f"{current_time} {status} {message}\n")
    # Close the file
    file.close()
    # Create the folder in the bucket
    s3.upload_file(file_path, s3name, folder_key)

def upload_to_s3(s3name, filename, account_id, vpc_id):
    # Create an S3 client
    s3 = boto3.client('s3')
    # Configure logging
    file_path = filename+".log"
    # Create the folder key with a trailing slash
    folder_key = account_id +'/'+ vpc_id+'/'+file_path
    s3.upload_file(file_path, s3name, folder_key)
    print("File uploaded to S3 bucket.")

def get_account_id():
    sts_client = boto3.client('sts')
    response = sts_client.get_caller_identity()
    account_id = response['Account']
    return account_id

def get_vpc_id(subnet_id):
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_subnets(SubnetIds=[subnet_id])
    subnet = response['Subnets'][0]
    vpc_id = subnet['VpcId']
    return vpc_id

def get_region(vpc_id, account_id, filename, s3name):
    session = boto3.Session()
    client = session.client('ec2')
    # Describe the VPC
    response = client.describe_vpcs(VpcIds=[vpc_id])
    # Extract the region from the response metadata
    region = session.region_name
    status = "INFO"
    message=f"Region acquired, the region ID id {region}."
    print(message)
    log_to_logfile(filename,message,status)
    upload_to_s3(s3name, filename, account_id, vpc_id)
    return region
  
def check_vpc_id(vpc_id_0, vpc_id_1, filename):
    if vpc_id_0 == vpc_id_1:
        status = "INFO"
        message="The VPC IDs are equal."
        print(message)
        log_to_logfile(filename,message,status)
    else:
        status = "ERROR"
        message="The VPC IDs are not equal."
        print(message)
        log_to_logfile(filename,message,status)
        status = "ERROR"
        message="Exiting program."
        print(message)
        log_to_logfile(filename,message,status)
        sys.exit()

def check_nsendpoint(vpcens, filename, account_id, vpc_id, s3name):
    # Create an EC2 client
    ec2 = boto3.client('ec2')
    # Describe the VPC endpoint
    response = ec2.describe_vpc_endpoints(VpcEndpointIds=[vpcens])
    # Get the VPC ID associated with the VPC endpoint
    vpcens_vpc_id = response['VpcEndpoints'][0]['VpcId']
    # Compare the VPC ID with the desired VPC ID
    if vpcens_vpc_id == vpc_id:
        print("VPC endpoint belongs to the right VPC ID.")
        status = "INFO"
        message=f"The NS Endpoint belongs to the same VPC as the target Subnets (vpc id={vpc_id})."
        print(message)
        log_to_logfile(filename,message,status)
        upload_to_s3(s3name, filename, account_id, vpc_id)
    else:
        print("VPC endpoint does not belong to the right VPC ID.")
        status = "INFO"
        message=f"The NS Endpoint belongs to a different VPC (Subnets vpc id={vpc_id} and Endpoint vpc id={vpcens_vpc_id})."
        print(message)
        log_to_logfile(filename,message,status)
        upload_to_s3(s3name, filename, account_id, vpc_id)
        status = "ERROR"
        message="Exiting program."
        print(message)
        log_to_logfile(filename,message,status)
        upload_to_s3(s3name, filename, account_id, vpc_id)
        sys.exit()

def get_vpc_endpoint_subnet_id(vpcens):
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_vpc_endpoints(VpcEndpointIds=[vpcens])
    if 'VpcEndpoints' in response and len(response['VpcEndpoints']) > 0:
        vpc_endpoint = response['VpcEndpoints'][0]
        subnet_id = vpc_endpoint.get('SubnetIds', [])
        if not subnet_id:
            raise ValueError(f"No subnets found for VPC endpoint {vpcens}")
        return subnet_id
    else:
        raise ValueError(f"No VPC endpoint found with ID {vpcens}")

def generate_cloudformation_template(subnet_ids, vpcens, filename,vpces3,s3name, account_id, vpc_id, vpcens_subnet_id):
    ec2_client = boto3.client('ec2')
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {}
    }
    subnet_routetable_ids=[]
    availability_zone = None
    for subnet_id in subnet_ids:
        # Remove hyphens from subnet ID
        sanitized_subnet_id = subnet_id.replace("-", "")
        # Retrieve the route table ID associated with the subnet
        response = ec2_client.describe_route_tables(
            Filters=[
                {
                    'Name': 'association.subnet-id',
                    'Values': [subnet_id]
                }
            ]
        )
        if 'RouteTables' in response and len(response['RouteTables']) > 0:
            route_table_id = response['RouteTables'][0]['RouteTableId']
            subnet_routetable_ids.append(route_table_id)
        else:
            status = "ERROR"
            message = f"No route table found for subnet {subnet_id}"
            log_to_logfile(filename, message, status)
            upload_to_s3(s3name, filename, account_id, vpc_id)
            raise ValueError(message)
            message = "Exiting the program"
            print (message)
            log_to_logfile(filename, message, status)
            upload_to_s3(s3name, filename, account_id, vpc_id)
            sys.exit(1)
        # Retrieve the CIDR block and VPC ID for the subnet
        subnet_response = ec2_client.describe_subnets(
            Filters=[
                {
                    'Name': 'subnet-id',
                    'Values': [subnet_id]
                }
            ]
        )
        if 'Subnets' in subnet_response and len(subnet_response['Subnets']) > 0:
            subnet = subnet_response['Subnets'][0]
            cidr_block = subnet['CidrBlock']
            subnet_vpc_id = subnet['VpcId']
            subnet_az = subnet['AvailabilityZone']
            subnet_name = ""
            if subnet.get('Tags'):
                for tag in subnet['Tags']:
                    if tag.get('Key') == 'Name':
                        subnet_name = tag.get('Value', "")
                        break
            if availability_zone is None:
                vpc_id = subnet_vpc_id
                availability_zone = subnet_az
            else:
                if subnet_vpc_id != vpc_id or subnet_az != availability_zone:
                    status = "ERROR"
                    message = "Subnets are not in the same VPC or Availability Zone"
                    log_to_logfile(filename, message, status)
                    upload_to_s3(s3name, filename, account_id, vpc_id)
                    raise ValueError(message)
                    message = "Exiting the program"
                    log_to_logfile(filename, message, status)
                    upload_to_s3(s3name, filename, account_id, vpc_id)
                    sys.exit(1)
        else:
            status = "ERROR"
            message = f"No subnet found with ID {subnet_id}"
            log_to_logfile(filename, message, status)
            upload_to_s3(s3name, filename, account_id, vpc_id)
            raise ValueError(message)
            status = "ERROR"
            message = "Exiting the program"
            log_to_logfile(filename, message, status)
            upload_to_s3(s3name, filename, account_id, vpc_id)
            sys.exit(1)
        status = "INFO"
        message = "Subnets are in the same VPC or Availability Zone"
        print (message)
        log_to_logfile(filename, message, status)
        upload_to_s3(s3name, filename, account_id, vpc_id)
        # Create the resources for the route table
        if subnet_name == "":
            subnet_name = sanitized_subnet_id
        route_table_resources = {
            f"RouteTableCopy{sanitized_subnet_id}": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "VpcId": {
                        "Ref": "VpcId"
                    },
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": f"Security-{subnet_name}-rtb"
                        }
                    ]
                }
            },
            f"RouteTableAssociation{sanitized_subnet_id}": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "SubnetId": subnet_id,
                    "RouteTableId": {
                        "Ref": f"RouteTableCopy{sanitized_subnet_id}"
                    }
                }
            }
        }
        # Add the route table resources to the template
        template["Resources"].update(route_table_resources)
        # Fetch existing routes for the route table
        existing_routes = get_existing_routes(route_table_id, vpces3, subnet, filename, s3name, account_id, vpc_id)
        # Add routes from subnet 1 to subnet 2 and vice versa
        route_resources = {
            f"Route{sanitized_subnet_id}": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "RouteTableId": {
                        "Ref": f"RouteTableCopy{sanitized_subnet_id}"
                    },
                    "DestinationCidrBlock": cidr_block,
                    "VpcEndpointId": vpcens
                }
            }
            #for vpcen in vpcens
        }
        # Add existing routes to the template
        if existing_routes:
            route_resources.update(existing_routes)
        # Add the route resources to the template
        template["Resources"].update(route_resources)
    # Create Route Table for the Endpoint Subnet
    for subnet_id in vpcens_subnet_id:
        # Remove hyphens from subnet ID
        sanitized_subnet_id = subnet_id.replace("-", "")
        # Retrieve the route table ID associated with the subnet
        response = ec2_client.describe_route_tables(
            Filters=[
                {
                    'Name': 'association.subnet-id',
                    'Values': [subnet_id]
                }
            ]
        )
        if 'RouteTables' in response and len(response['RouteTables']) > 0:
            status = "INFO"
            message = f"Route table found for the Endpoint Subnet (subnet {subnet_id}), it will be overriden"
            log_to_logfile(filename, message, status)
            upload_to_s3(s3name, filename, account_id, vpc_id)
        # Create the resources for the route table
        route_table_resources = {
            f"SecurityEndpoint{sanitized_subnet_id}": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "VpcId": {
                        "Ref": "VpcId"
                    },
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "SecurityEndpoint-rtb"
                        }
                    ]
                }
            },
            f"RouteTableAssociation{sanitized_subnet_id}": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "SubnetId": subnet_id,
                    "RouteTableId": {
                        "Ref": f"SecurityEndpoint{sanitized_subnet_id}"
                    }
                }
            }
        }
        # Add the route table resources to the template
        template["Resources"].update(route_table_resources)
    templatelambdarevert = generate_template_lambda (subnet_ids,subnet_routetable_ids)
    template["Resources"].update(templatelambdarevert)
    status = "INFO"
    message="Lambda to revert routes added successfully to the AWS Cloudformation template"
    print(message)
    log_to_logfile(filename,message,status)    
    # Add VPC ID parameter to the template
    template["Parameters"] = {
        "VpcId": {
            "Type": "String",
            "Default": vpc_id
        },
        "Subnet1Id": {
            "Type": "String",
            "Default": subnet_ids[0]
        },
        "RouteTable1Id": {
            "Type": "String",
            "Default": subnet_routetable_ids[0]
        },
        "Subnet2Id": {
            "Type": "String",
            "Default": subnet_ids[1]
        },
        "RouteTable2Id": {
            "Type": "String",
            "Default": subnet_routetable_ids[1]
        },
    }
    status = "INFO"
    message="AWS Cloudformation template generated successfuly"
    print(message)
    log_to_logfile(filename,message,status)
    return template

def get_existing_routes(route_table_id, vpces3, subnet, filename, s3name, account_id, vpc_id):
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_route_tables(
        RouteTableIds=[route_table_id]
    )
    existing_routes = []
    for route_table in response['RouteTables']:
        for route in route_table['Routes']:
            if (
                'DestinationCidrBlock' in route
                and route['DestinationCidrBlock'] != 'local'  # Ignore the local route
                and 'VpcEndpointId' in route
                and route['VpcEndpointId'] in vpces3
                and route.get('DestinationPrefixListId') is None
                and route['VpcEndpointId'] != route.get('GatewayId')
            ):
                existing_routes.append(route)
    status = "INFO"
    message=f"Existing routes copied successfully for route table id {route_table_id}, that belongs to the subnet id {subnet['SubnetId']}"
    print(message)
    log_to_logfile(filename,message,status)
    return existing_routes

def get_s3_endpoints(region):
    client = boto3.client('ec2', region_name=region)
    response = client.describe_vpc_endpoints()
    endpoints = response['VpcEndpoints']
    s3_endpoints = [endpoint for endpoint in endpoints if 's3' in endpoint['ServiceName']]
    return s3_endpoints

def main(vpcens, subnet_ids, s3name, internet):
    # Variables

    vpces3=[]
    vpces3str=""
    
    current_time = datetime.now().strftime("%Y%m%d%I%M%p")
    filename = "Routechange" + current_time

    account_id = get_account_id()
    vpc_id_0 = get_vpc_id(subnet_ids[0])
    vpc_id_1 = get_vpc_id(subnet_ids[1])

    create_log_file(filename)
    create_s3_folder(s3name, filename, account_id, vpc_id_0)

    #Logfile and logfolder created
    
    check_vpc_id(vpc_id_0, vpc_id_1, filename)
    vpc_id = vpc_id_0

    if vpcens is None:
        status = "ERROR"
        message = "A VPC Endpoint for Network Security wasn't provided."
        print(message)
        log_to_logfile(filename, message, status)
        upload_to_s3(s3name, filename, account_id, vpc_id)
        sys.exit()
    else:
        status = "INFO"
        message = "A VPC Endpoint for Network Security was provided, vpc id=" + vpcens + "."
        print(message)
        log_to_logfile(filename, message, status)
        upload_to_s3(s3name, filename, account_id, vpc_id)

    vpcens_subnet_id = get_vpc_endpoint_subnet_id(vpcens)        
    status = "INFO"
    message = f"The subnet Id where the VPC Endpoint is attached is {vpcens_subnet_id}."
    print(message)
    log_to_logfile(filename, message, status)
    upload_to_s3(s3name, filename, account_id, vpc_id)

    check_nsendpoint(vpcens, filename, account_id, vpc_id, s3name)
    
    region = get_region(vpc_id, account_id,filename, s3name)

    endpoints = get_s3_endpoints(region)
    
    for endpoint in endpoints:
        vpces3.append(endpoint['VpcEndpointId'])
      
    status = "INFO"
    vpces3str=', '.join(map(str,vpces3))
    message = f"The following S3 VPC Endpoints were found : {vpces3str}"
    print(message)
    log_to_logfile(filename, message, status)
    upload_to_s3(s3name, filename, account_id, vpc_id)        
  
    status = "INFO"
    message = f"Starting Program for account id={account_id}"
    print(message)
    log_to_logfile(filename, message, status)
    upload_to_s3(s3name, filename, account_id, vpc_id)
    template = generate_cloudformation_template(subnet_ids, vpcens, filename,vpces3,s3name, account_id, vpc_id, vpcens_subnet_id)
    urlmessage = create_templatefile(template,s3name, account_id, vpc_id,current_time)
    status = "INFO"
    message = f"AWS Cloudformation Template to Rotate Routes uploaded successfully to the s3 bucket {s3name}/{account_id}/{vpc_id}"
    print(message)
    log_to_logfile(filename, message, status)
    upload_to_s3(s3name, filename, account_id, vpc_id)
    
    print(json.dumps(template, indent=4))
    print(f"Download your template from:")
    print(urlmessage)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--vpcendpoint", help="VPC Endpoit for Trend Network Security")
    parser.add_argument("--subnet1", help="Source Subnet ID - Public Subnet ID")
    parser.add_argument("--subnet2", help="Destination Subnet ID - Private Subnet ID")
    parser.add_argument("--s3bucket", help="S3 bucket where logs will be uploaded to")
    parser.add_argument("--internet", help="Intercept traffic to the IGw/NGw {YES/NO}", default="NO")
    args = parser.parse_args()                                                            

    subnet_ids = [args.subnet1, args.subnet2]

    if not all(vars(args).values()):
        parser.print_help()
        print ("Usage: python3 rotateroutes.py --vpcendpoint <VPC_Endpoint_ID> --subnet1 <Subnet1_ID> --subnet2 <Subnet2_ID> --s3bucket <S3Bucket_Name> --internet <YES/NO>")
        sys.exit(1)

    # Call the main function and pass the arguments
    main(args.vpcendpoint, subnet_ids, args.s3bucket, args.internet)
