dummy_template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Stack 3",
    "Resources": {
        "VPC": {
            "Properties": {
                "CidrBlock": "192.168.0.0/16",
            },
            "Type": "AWS::EC2::VPC"
        }
    },
    "Outputs": {
        "VPC": {
            "Value": {"Ref": "VPC"},
            "Description": "This is a description."
        }
    }
}
