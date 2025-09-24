# Alleviate Phone Number update

Hi! This repo contains the code that exposes an API endpoint using AWS Lambda where you can send a phone number to update the phone number of a patient in the Alleviate Portal.

# Files

To get started with this solution I did in 3 parts.

1. Build a selenium script that can do the RPA tasks, I have experience with selenium so I chose this as my preferred framework. The script can be found in lambda\selenium-base.py. In this folder you will also find script.py which was the conversion of selenium-base.py into a python file that could be ran in lambda, but this also didn't work so I made another tester.py which just loaded up google.com using selenium and slowly added in step by step what I needed to complete this task.
2. Set up API Gateway and Lambda using an AWS tutorial https://catalog.us-east-1.prod.workshops.aws/workshops/10141411-0192-4021-afa8-2436f3c66bd8/en-US. This was helpful but I later took out the API Gateway portion due to it timing out while the lambda function ran. This also scaffolded most of the IAC portion using the AWS CDK. (You need to have AWS CLI set up for this to work). The hello.js file in the lambda folder is from this tutorial.
3. The last portion was containerizing the selenium code and running the container using Lambda which I researched is possible before I started development. https://medium.com/@kroeze.wb/running-selenium-in-aws-lambda-806c7e88ec64

## Requirements

Before getting started, ensure you have the following:

- AWS account
- Docker installed locally
- AWS CLI configured with appropriate permissions
- Node.js and npm installed

## How to run

You will need to have set up AWS CLI and use that to install + setup the cdk

```
npm install -g aws-cdk
git clone https://github.com/PrianshuVerma/lamb.git
cd lamb
npm install # installs dependencies
```

Bootstrap CDK (for first time users)

```
cdk bootstrap aws://<AWS_ACCOUNT_ID>/<AWS_REGION>
```

Build and Deploy

```
npm build
cdk synth # views what it's gonna build
cdk deploy
```

This will output a URL that you can then use to curl and make the request

```
curl "<AWS-Given-URL-Here>?phone=1234567089"
```

## Next Steps

This is something I am happy to submit while balancing time and output, it does the job. However given more time there are many ways I would make this better

- Not hard code the credentials to log in to the portal
  - Could store them as ENV variables
  - Store them as Github Secrets
  - Pass them in the URL the same way the phone number is passed
- Clean up the file structure a bit, I left the old files there to show you how the workflow went step by step, but ideally I would store these in another repo or locally as a reminder on how I did it
- Use Github actions to automate the deployment
  - Already had access to the Yamls for the GitHub actions
  - Need to create the AWS credentials as secrets so your pipeline can pick them up to deploy
  - Would make things easier for the user to use this, but it would probably take me a few hours of tinkering to get that to work
