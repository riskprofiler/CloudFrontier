![Logo](frontend/public/images/logo.png)

![GitHub](https://img.shields.io/github/license/riskprofiler/Cloud-Frontier)
![Supports AWS](https://img.shields.io/badge/Supports-AWS-orange)
![Supports GCP](https://img.shields.io/badge/Supports-GCP-1a73e8)
![Supports Azure](https://img.shields.io/badge/Supports-Azure-89c402)
![Supports DigitalOcean](https://img.shields.io/badge/Supports-DigitalOcean-0069ff)
![Supports Oracle Cloud](https://img.shields.io/badge/Supports-Oracle_Cloud-e55844)

> Monitor the internet attack surface of various public cloud environments.

Currently supports AWS, GCP, Azure, DigitalOcean and Oracle Cloud.

## ⚙️ Setting up

The project is built using multiple serverless stacks which can be deployed to
AWS. For this, you'll need to configure the credentials of the AWS account to
which you want to deploy to.

Once you've done that, you can start setting up the cloud accounts you want to
scan using Cloud Frontier.

### Setting up your cloud accounts

Templates for the credentials are available in the `credentials` directory and
have they have the suffix `.example`. To create the actual environment/credential
file, you can simply create a copy of the template, dropping the `.example` from
the end.

- #### AWS

  Upload the CloudFormation template `CloudFrontierAWS.yml` to the account whose
  assets you want to collect. The output of this stack will be an IAM role's ARN
  that Cloud Frontier will use to collect the assets. Copy the ARN and paste it
  in `credentials/aws.env`.

- #### GCP

  To collect assets from your GCP account, you'll need to
  [create a service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

  Once you've created the key, add it to `credentials/gcp.json`, and also add
  the GCP project ID to `credentials/gcp.env`.

- #### Azure

  - **Create application in Azure Active Directory**
    1. [Login into your azure account.](https://portal.azure.com/)
    1. Select Azure Active directory in the left sidebar.
    1. Click on App registrations.
    1. Click + Add.
    1. Enter the application name, select application type(web app/api) and sign-on-url.
    1. Click on create button.
  - **Get Subscription ID**
    1. [Login into your azure account.](https://portal.azure.com/)
    1. Select Subscriptions in the left sidebar.
    1. Select whichever subscription is needed.
    1. Click on overview.
    1. Copy the Subscription ID.
  - **Get Tenant ID**
    1. [Login into your azure account.](https://portal.azure.com/)
    1. Select azure active directory in the left sidebar.
    1. Click properties.
    1. Copy the directory ID.
  - **Get Client ID**
    1. [Login into your azure account.](https://portal.azure.com/)
    1. Select azure active directory in the left sidebar.
    1. Click Enterprise applications.
    1. Click All applications.
    1. Select the application which you have created.
    1. Click Properties.
    1. Copy the Application ID .
  - **Get Client secret**
    1. [Login into your azure account.](https://portal.azure.com/)
    1. Select azure active directory in the left sidebar.
    1. Click App registrations.
    1. Select the application which you have created.
    1. Click on All settings.
    1. Click on Keys.
    1. Type Key description and select the Duration.
    1. Click save.
    1. Copy and store the key value. You won't be able to retrieve it after you leave this page.

- #### Digital Ocean

  To collect assets from your DigitalOcean account, you'll have to create a
  [personal access token](https://www.digitalocean.com/docs/apis-clis/api/create-personal-access-token/)
  and an [access key for Spaces](https://www.digitalocean.com/community/tutorials/how-to-create-a-digitalocean-space-and-api-key#creating-an-access-key).

  When you're creating the access token you only need to select the `read` scope
  since that's all that we require.

  Paste the personal access token and the Spaces access key and secret in the
  `credentials/digitalocean.env` file.

- #### Oracle Cloud

  To access your Oracle Cloud resources and services you need to create a key and get the Orale Cloud Identifiers  [Required Keys and OCIDs](https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#Required_Keys_and_OCIDs). Paste this API key in `credentials/analyzers.env`.

- #### Shodan

  To be able to get port scan results for IP addresses from Shodan you'll need
  to have an API key, which you can get for free by
  [registering on Shodan](https://account.shodan.io/register). Once you generate
  the API key, paste it in `credentials/analyzers.env`.

- #### VirusTotal

  In order to get the reputation of an IP address or domain, you must have a
  VirusTotal account, which can be created for free by registering to
  [VirusTotal Community](https://www.virustotal.com/gui/join-us). Once you
  generate the API key, paste it in `credentials/analyzers.env`.

### Local setup

#### Getting all the dependencies

1. Make sure you have all the requirements installed.

    - Python 3.8
    - Node.js 10.x or later
    - Golang 1.x
    - `pipenv`
    - `npm`

1. Inside the root folder, run the following command.

    ```sh
    npm install --save-dev
    ```

1. To deploy all the stacks, simply run the deployment script:

    ```sh
    ./deploy.sh
    ```

    You can pass the same options to this script as you would to the
    `serverless deploy` command, such as `--profile`, `--stage`, `--region` etc.

1. Add your credentials for cloud services in the credential folder.

### Docker

1. Build the Docker image

    ```sh
    docker build -t cloud-frontier .
    ```

1. Run the following command to deploy the stacks:

    ```sh
    docker run -v ~/.aws:/root/.aws deploy-cloud-frontier
    ```

    You can pass the same options here as you would to the `serverless deploy`
    command, such as `--profile`, `--stage`, `--region` etc.

    NOTE: the `~/.aws` directory is mounted inside the container so that your
    AWS account profile can be easily made available to the deployment script
    that's running inside the container.

## 🎁 Current Resources and Services

### AWS

- API Gateway
- EC2
- Elastic Beanstalk
- Elastic Load Balancers
- Elasticsearch Service
- Elasticache
- RDS
- S3

### Azure

- Content Delivery Network
- Public IP Addresses
- Blob

### DigitalOcean

- Domains
- Floating IPs
- Spaces
- Load Balancers

### GCP

- Domain Name Service
- Public IP Address
- Storage Buckets
- Forwarding Rules

### Oracle Cloud

- DNS Zones
- Public IP Addresses
- Storage Buckets

## ✨ Components

![cloudfrontier-components](https://github.com/riskprofiler/Nights-Watch/blob/master/component-cf.png)

## 🛣️ Roadmap

- Add authentication using Cognito
- Perform port scanning in IPs using Nmap

## ⭐ Contributors

- Setu Parimi
  <a href="https://github.com/setuparimi">![GitHub followers](https://img.shields.io/github/followers/setuparimi?style=social)</a>
  <a href="https://twitter.com/setuparimi">![Twitter Follow](https://img.shields.io/twitter/follow/setuparimi?style=social)</a>
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/sethuparimi)
- Syed Faheel Ahmad
  <a href="https://github.com/faheel">![GitHub followers](https://img.shields.io/github/followers/faheel?style=social)</a>
  <a href="https://twitter.com/FaheelAhmad">![Twitter Follow](https://img.shields.io/twitter/follow/FaheelAhmad?style=social)</a>
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/faheel)
- Pranay Kumar Paine
  <a href="https://github.com/pranaypaine">![GitHub followers](https://img.shields.io/github/followers/pranaypaine?style=social)</a>
  <a href="https://twitter.com/pranaypaine">![Twitter Follow](https://img.shields.io/twitter/follow/pranaypaine?style=social)</a>
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/pranaykumarpaine)
- Nikhil Goyal
  <a href="https://github.com/nikkkhilgoyal">![GitHub followers](https://img.shields.io/github/followers/nikkkhilgoyal?style=social)</a>
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/nikhil-goyal-726b1b19b)
- Roma Negi
  <a href="https://github.com/negiroma">![GitHub followers](https://img.shields.io/github/followers/negiroma?style=social)</a>
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/roma-negi-63508314b)
- Gargi Chakroborty
   <a href="https://github.com/setuparimi">![GitHub followers](https://img.shields.io/github/followers/c-gargi?style=social)</a>
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/cgargi)
- Shivam Kumar
  <a href="https://github.com/shivamethicalhat">![GitHub followers](https://img.shields.io/github/followers/shivamethicalhat?style=social)</a>
- Prabhakar Upadhyay
  <a href="https://github.com/prabhakarUpadhyay007">![GitHub followers](https://img.shields.io/github/followers/prabhakarUpadhyay007?style=social)</a>
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/prabhakar-upadhyay-254465102)
  
  
## 👍 Contributting

   We are happy to receive issues and review pull requests. Please make sure to write tests for the code you are introducing and make sure it doesn't break already passing tests.

   Read the following sections for an introduction into the code.

## ⚖️ License

This project is licensed under the terms of the [Apache license](LICENSE).
