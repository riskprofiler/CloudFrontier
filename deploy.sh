#!/bin/bash

trap 'exit' ERR

red='\033[0;31m'
green='\033[0;32m'
green_bold='\033[1;32m'
blue='\033[0;34m'
blue_bold='\033[1;34m'
magenta='\033[0;35m'
reset='\033[0m'     # reset style

npx -v >&/dev/null
npx_return_code=$?

serverless -v >&/dev/null
serverless_return_code=$?

if [ $npx_return_code -eq 0 ]
then
	deploy_command="npx serverless deploy $@ --verbose"
elif [ $serverless_return_code -eq 0 ]
	deploy_command="serverless deploy $@ --verbose"
else
	printf "${red}Serverless is not installed. Please run npm install --save-dev first and try again.${reset}\n"
	exit 1
fi

printf "[1/4] ${blue}Deploying the core stack...${reset}\n"
(cd core && $deploy_command)
printf "${green}Core stack deployed!${reset}\n\n"

printf "[2/4] ${blue}Deploying collectors and analyzers...${reset}\n"
num_collectors_being_deployed=0
# Deploy the stacks which have an environment file:
if [[ -f credentials/analyzers.env ]]; then
    (cd analyzers && $deploy_command)&
else
    printf "[x] ${red}Unable to deploy the analyzers - environment file does not exist${reset}\n"
    exit 1
fi
if [[ -f credentials/aws.env ]]; then
    printf "${blue}Deploying AWS collectors...${reset}\n"
    (cd collectors/aws && $deploy_command)&
    ((num_collectors_being_deployed+=1))
else
    printf "[!] ${magenta}Skipped deployment of AWS collectors - environment file does not exist${reset}\n"
fi
if [[ -f credentials/azure.env ]]; then
    printf "${blue}Deploying Azure collectors...${reset}\n"
    (cd collectors/azure && $deploy_command)&
    ((num_collectors_being_deployed+=1))
else
    printf "[!] ${magenta}Skipped deployment of Azure collectors - environment file does not exist${reset}\n"
fi
if [[ -f credentials/digitalocean.env ]]; then
    printf "${blue}Deploying DigitalOcean collectors...${reset}\n"
    (cd collectors/digitalocean && $deploy_command)&
    ((num_collectors_being_deployed+=1))
else
    printf "[!] ${magenta}Skipped deployment of DigitalOcean collectors - environment file does not exist${reset}\n"
fi
if [[ -f credentials/gcp.json ]]; then
    printf "${blue}Deploying GCP collectors...${reset}\n"
    (cd collectors/gcp && $deploy_command)&
    ((num_collectors_being_deployed+=1))
else
    printf "[!] ${magenta}Skipped deployment of GCP collectors - environment file does not exist${reset}\n"
fi
if [[ -f credentials/oracle/oci_api_key.pem ]]; then
    printf "${blue}Deploying Oracle collectors...${reset}\n"
    (cd collectors/oracle && $deploy_command)&
    ((num_collectors_being_deployed+=1))
else
    printf "[!] ${magenta}Skipped deployment of Oracle collectors - environment file does not exist${reset}\n"
fi

if [[ $num_collectors_being_deployed -eq 0 ]]; then
    printf "[x] ${red}No collectors were deployed. Please create the environment file for at least one collecter to proceed${reset}\n"
    exit 1
else
    wait    # for all the parallel (background) deployments to finish
    printf "${green}Collectors and analyzers deployed!${reset}\n\n"
fi

printf "[3/4] ${blue}Deploying the APIs...${reset}\n"
(cd api && $deploy_command)
printf "${green}APIs deployed!${reset}\n\n"

printf "[4/4] ${blue}Building and deploying the front-end...${reset}\n"
(cd frontend && npm install && npm run build && $deploy_command)
frontend_domain=$(cat frontend/temp-frontend-output | grep -o "[a-z0-9]*\.cloudfront\.net")
rm frontend/temp-frontend-output
frontend_url="https://${frontend_domain}"
printf "${green}Front-end deplyed!${reset}\n\n"

printf "${green_bold}Deployment is complete!${reset} Visit ${blue_bold}${frontend_url}${reset} to get started.\n"
