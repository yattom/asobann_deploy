Deploy [asobann](https://github.com/yattom/asobann_app) to AWS ECS with CloudFormation.
Currently only as development environment.

## Limitations
- This works only for development environment for now.  
- ALL DATA WILL BE LOST upon deployment, updating stacks, and / or restarting tasks or instances.
- It has no stable URL.  You need to get new URL after deployment which recreates ALB.
- This deployment will not fit within AWS free tier, or so I think.
- EC2 instance type is fixed to t3.small.

## Prerequisite

- Python 3.6 >= and pip is installed.
- AWS CLI installed and set up.
- Checked out asobann https://github.com/yattom/asobann_app already.
- Checked out this repository.
- node >=v14 is installed.

## How to deploy

0. Make sure development environment is setup.  (Do this when library configuration is updated.)

   ```shell script
   % cd /path/to/asobann
   % npm install
   % pip install pipenv
   ```

1. Build asobann image and push to ECR.

   ```shell script
   % cd /path/to/asobann
   % npx webpack
   % pipenv sync
   % pipenv run pip freeze > requirements.txt
   % docker build -f Dockerfile.aws -t asobann_aws:latest .
   % docker tag asobann_aws 999999999999.dkr.ecr.REGION.amazonaws.com/asobann_aws
   % aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin \
       999999999999.dkr.ecr.REGION.amazonaws.com/asobann_aws
   % docker push 999999999999.dkr.ecr.REGION.amazonaws.com/asobann_aws
   ```

   Replace 999999999999 with your AWS account id and REGION with region name to deploy (e.g. us-east-1)

1. Deploy with CloudFromation

   ```shell script
   % cd /path/to/asobann_deploy
   % cd aws_dev
   % aws cloudformation package --template-file asobann_aws.yaml --s3-bucket CFN_BUCKET_NAME --s3-prefix dev \
       --output-template-file OUTPUT_TEMPLATE_FILE
   Uploading to xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.template  2500 / 2500.0  (100.00%)
   Successfully packaged artifacts and wrote output template to file /tmp/asobann_aws.yaml.
   Execute the following command to deploy the packaged template
   aws cloudformation deploy --template-file /tmp/asobann_aws.yaml --stack-name <YOUR STACK NAME>

   % aws cloudformation deploy --template-file OUTPUT_TEMPLATE_FILE --stack-name asobann-dev \
       --parameter-overrides PublicHostname=dev.asobann.example.com \
       MaintenanceIpRange=SSH_IP MongoDbPassword=MONGODB_PASSWORD \
       AppImage=999999999999.dkr.ecr.REGION.amazonaws.com/asobann_aws \
       AppTaskCount=1 CertificateArn=<Certificate ARN> GoogleAnalyticsId=NotAvailable \
       --capabilities CAPABILITY_IAM
   Waiting for changeset to be created..
   Waiting for stack create/update to complete
   Successfully created/updated stack - asobann-dev
   ```

    Replace CFN_BUCKET_NAME with a S3 bucket to put CloudFormation templates.  Maybe you need to create one.
    
    Replace OUTPUT_TEMPLATE_FILE for temporarily used template file to deploy.  I prefer /tmp/asobann_aws_dev.yaml
    
    You need to specify parameters.
    
    - SSH_IP: CIDR block for ssh connection.  Set IP range of your own PC like 1.2.3.4/24.  Set 10.0.0.0/16 to prevent ssh from outside. (I hope it works.)
    - MONGODB_PASSWORD: admin user of MongoDB will be created with this password.  Use a sensible one but MongoDB will not be exposed to the internet.
    - <Certificate ARN>: Certificate arn to use for https
    - GoogleAnalyticsId: Google Analytics ID like UA-000000000-0.  Disabled in development mode.
    - AppTaskCount: Desired task number for app service.  Default is 3.
    - AppImage: image of asobann you just pushed in step 1.
    
1. Access created service.  Get Service URL from outputs in created stacks.  Access from Web AWS Console, or awscli as below.

   Execute command below and look for "ServiceUrl' in Output section of LoadBalancer Stack part
   
    ```shell script
    % aws cloudformation describe-stacks
    ...
        {
            "OutputKey": "ServiceUrl",
            "OutputValue": "http://asoba-LoadB-XXXXXXXXXXXXX-9999999999.us-east-1.elb.amazonaws.com",
            "Description": "URL of the load balancer for the sample service."
        },
    ...
    ```
   
   Access the url and you will see deployed asobann.

### Sample alias

I set and use shell aliases like this:

```shell script
alias build_aws=' \
  # run from asobann_app dir
  set -x ; \
  npx watch ; \
  docker build -f Dockerfile.aws -t asobann_aws:latest . ; \
  docker tag asobann_aws 999999999999.dkr.ecr.us-east-1.amazonaws.com/asobann_aws ; \
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 999999999999.dkr.ecr.us-east-1.amazonaws.com/asobann_aws ; \
  docker push 999999999999.dkr.ecr.us-east-1.amazonaws.com/asobann_aws ; \
  set +x'
alias cfn_deploy_dev=' \
  # run from asobann_deploy/aws dir
  set -x ; \
  aws cloudformation package --template-file asobann_aws.yaml --s3-bucket YOURBUCKETNAME --s3-prefix dev --output-template-file /tmp/asobann_aws.yaml ;
  aws cloudformation deploy --template-file /tmp/asobann_aws.yaml --stack-name asobann-dev --parameter-overrides PublicHostname=dev.asobann.example.com MaintenanceIpRange=192.0.2.0/24 MongoDbPassword=LAMEPASSWORD AppImage=999999999999.dkr.ecr.us-east-1.amazonaws.com/asobann_aws AppTaskCount=1 CertificateArn=arn:aws:acm:us-east-1:999999999999:certificate/blahblahblah GoogleAnalyticsId=NotAvailable --capabilities CAPABILITY_IAM --tags ProjectName=asobann AsobannEnv=dev; \
  set +x'
alias cfn_deploy_prod=' \
  # run from asobann_deploy/aws dir
  set -x ; \
  aws cloudformation package --template-file asobann_aws.yaml --s3-bucket YOURBUCKETNAME --s3-prefix prod --output-template-file /tmp/asobann_aws.yaml ;
  aws cloudformation deploy --template-file /tmp/asobann_aws.yaml --stack-name asobann-prod --parameter-overrides PublicHostname=asobann.example.com MaintenanceIpRange=192.0.2.0/24 MongoDbPassword=SERIOUSPASSWORD AppImage=999999999999.dkr.ecr.us-east-1.amazonaws.com/asobann_aws AppTaskCount=3 CertificateArn=arn:aws:acm:us-east-1:999999999999:certificate/blahblahblah GoogleAnalyticsId=UA-000000000-0 --capabilities CAPABILITY_IAM --tags ProjectName=asobann AsobannEnv=prod ; \
  set +x'
```
