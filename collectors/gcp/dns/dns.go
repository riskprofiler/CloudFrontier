package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	"google.golang.org/api/dns/v1"

	"github.com/aws/aws-lambda-go/lambda"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/sns"
	"google.golang.org/api/option"
)

var (
	dynamoDBClient *dynamodb.DynamoDB
	snsClient      *sns.SNS

	dynamoDBTableAssets = os.Getenv("DynamoDBTableAssets")
	credentialsFilePath = os.Getenv("GCPCredentialsFilePath")
	projectID           = os.Getenv("GCPProjectID")
	analyzeDomain       = os.Getenv("SNSTopicAnalyzeDomainARN")
)

type DNSFindings struct {
	Type     string `json:"type"`
	Sk       string `json:"sk"`
	Provider string `json:"provider"`
}

type snsMessageAnalyzeDomainData struct {
	Domain string `json:"domain"`
	Type   string `json:"type"`
}

func Init() {
	sess := session.New()
	dynamoDBClient = dynamodb.New(sess)
	snsClient = sns.New(sess)
}

func StoreDNSFindings(item interface{}) (bool, error) {
	results, err := dynamodbattribute.MarshalMap(item)
	if err != nil {
		fmt.Println("Error marshalling new item:", err.Error())
		fmt.Println("Item:", item)
		return false, err
	}
	fmt.Println("Item Marshalled...")
	_, err = dynamoDBClient.PutItem(&dynamodb.PutItemInput{
		Item:      results,
		TableName: aws.String(dynamoDBTableAssets),
	})
	if err != nil {
		fmt.Println("Got error calling PutItem:", err.Error())
		return false, err
	}
	log.Print("Successfully added data to table " + dynamoDBTableAssets)
	return true, nil
}

func collectDNSHandler( ctx context.Context, snsEvent events.SNSEvent) {

	Init()
	//msgBody := snsEvent['Records'][0]['Sns']['Message'];
	cntx := context.Background()
	dnsService, err := dns.NewService(
		cntx,
		option.WithCredentialsFile(credentialsFilePath),
	)
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	req := dnsService.ManagedZones.List(projectID)

	if err := req.Pages(cntx, func(page *dns.ManagedZonesListResponse) error {
		for _, managedZone := range page.ManagedZones {
			if managedZone.Visibility == "public" {
				fmt.Println("Name : ", managedZone.DnsName)
				fmt.Println("Description : ", managedZone.Description)

				domain := strings.TrimRight(managedZone.DnsName, ".")
				item := DNSFindings{
					Type:     "domain",
					Sk:       domain,
					Provider: "gcp",
				}
				isStored, err := StoreDNSFindings(item)

				if err != nil {
					log.Print("Failed to save DNS ", err)

				}
				log.Print("Domain DNS saved : ", isStored)
				snsMessage := &snsMessageAnalyzeDomainData{
					Domain: domain,
					Type:   "domain",
				}
				PublishSNSMessage(snsMessage, analyzeDomain)
			}

		}
		return nil
	}); err != nil {
		log.Fatal(err)

	}

}

func main() {
	lambda.Start(collectDNSHandler)
}

// PublishSNSMessage publishes the given SNS message to the given topic ARN.
func PublishSNSMessage(messageStruct interface{}, topicARN string) {
	messageBytes, err := json.Marshal(messageStruct)
	if err != nil {
		fmt.Println("Error marshalling SNS message", err.Error())
		fmt.Println("Message struct:", messageStruct)
		os.Exit(1)
	}

	_, err = snsClient.Publish(&sns.PublishInput{
		Message:  aws.String(string(messageBytes)),
		TopicArn: aws.String(topicARN),
	})
	if err != nil {
		fmt.Println(err.Error())
		os.Exit(1)
	}
}
