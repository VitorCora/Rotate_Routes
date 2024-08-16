import argparse
import sys
import boto3
import json
from datetime import datetime

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
    uploadtemplate_to_s3(s3name, file_path, account_id, vpc_id)

def uploadtemplate_to_s3(s3name, file_path, account_id, vpc_id):
    # Create an S3 client
    s3 = boto3.client('s3')
    # Create the folder key with a trailing slash
    folder_key = account_id +'/'+ vpc_id+'/'+file_path  
    s3.upload_file(file_path, s3name, folder_key)
    print("File uploaded to S3 bucket.")

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

def generate_cloudformation_template(subnet_ids, vpcens, filename,vpces3,s3name, account_id, vpc_id):
    ec2_client = boto3.client('ec2')
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {}
    }
    vpc_id = None
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
        else:
            status = "ERROR"
            message = f"No route table found for subnet {subnet_id}"
            log_to_logfile(filename, message, status)
            upload_to_s3(s3name, filename, account_id, vpc_id)
            raise ValueError(message)
            message = "Exiting the program"
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
            if vpc_id is None:
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
        route_table_resources = {
            f"RouteTableCopy{sanitized_subnet_id}": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "VpcId": {
                        "Ref": "VpcId"
                    }
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
                    "VpcEndpointId": vpcen
                }
            }
            for vpcen in vpcens
        }
        # Add existing routes to the template
        if existing_routes:
            route_resources.update(existing_routes)
        # Add the route resources to the template
        template["Resources"].update(route_resources)
    # Add VPC ID parameter to the template
    template["Parameters"] = {
        "VpcId": {
            "Type": "String",
            "Default": vpc_id
        }
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

def main(vpcens, subnet_ids, s3name):
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
    template = generate_cloudformation_template(subnet_ids, vpcens, filename,vpces3,s3name, account_id, vpc_id)
    create_templatefile(template,s3name, account_id, vpc_id,current_time)
    status = "INFO"
    message = f"AWS Cloudformation Template to Rotate Routes uploaded successfully to the s3 bucket {s3name}/{account_id}/{vpc_id}"
    print(message)
    log_to_logfile(filename, message, status)
    upload_to_s3(s3name, filename, account_id, vpc_id)
    
    print(json.dumps(template, indent=4))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--vpcendpoint", help="VPC Endpoit for Trend Network Security")
    parser.add_argument("--subnet1", help="Source Subnet ID - Public Subnet ID")
    parser.add_argument("--subnet2", help="Destination Subnet ID - Private Subnet ID")
    parser.add_argument("--s3bucket", help="S3 bucket where logs will be uploaded to")
    args = parser.parse_args()                                                            

    subnet_ids = [args.subnet1, args.subnet2]

    if not all(vars(args).values()):
        parser.print_help()
        print ("Usage: python3 rotateroutes.py --vpcendpoint <VPC_Endpoint_ID> --subnet1 <Subnet1_ID> --subnet2 <Subnet2_ID> --s3bucket <S3Bucket_Name>")
        sys.exit(1)

    # Call the main function and pass the arguments
    main(args.vpcendpoint, subnet_ids, args.s3bucket)
