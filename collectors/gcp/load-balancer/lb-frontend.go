package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"google.golang.org/api/compute/v1"
	"google.golang.org/api/option"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/sns"
)

var (
	dynamoDBClient       *dynamodb.DynamoDB
	snsClient            *sns.SNS
	dynamoDBTableAssets  = os.Getenv("DynamoDBTableAssets")
	credentialsFilePath  = os.Getenv("GCPCredentialsFilePath")
	projectID            = os.Getenv("GCPProjectID")
	snsTopicAnalyzeIPARN = os.Getenv("SNSTopicAnalyzeIPARN")
)

type IPAddressFinding struct {
	Type     string `json:"type"`
	Sk       string `json:"sk"`
	Provider string `json:"provider"`
}

type Regions struct {
	Regions []Region `json:"regions"`
}

type Region struct {
	Name        string `json:"name"`
	Country     string `json:"country"`
	CountryCode string `json:"countrycode"`
}

type snsMessageAnalyzeIP struct {
	IPAddress string `json:"ip_address"`
	Type      string `json:"type"`
}

func Init() {
	sess := session.New()
	dynamoDBClient = dynamodb.New(sess)
	snsClient = sns.New(sess)
}

func StoreLBFindings(item interface{}) (bool, error) {
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

func GetCountryData(cc string) (Region, error) {
	var reg Region

	jsonFile, err := os.Open("servicedata/region.json")
	if err != nil {
		fmt.Println("error in opening region.json : ", err)
		return reg, err
	}
	fmt.Println("Successfully Opened region.json")

	defer jsonFile.Close()

	byteValue, _ := ioutil.ReadAll(jsonFile)
	data := Regions{}
	err = json.Unmarshal(byteValue, &data)
	if err != nil {
		fmt.Println("error in unmarshalling region.json:", err)
		return reg, err
	}

	for _, region := range data.Regions {
		if region.CountryCode == cc {
			reg = region
		}
	}
	fmt.Print("Found region ")
	fmt.Print(reg)
	return reg, nil
}

func collectLoadBalancers(ctx context.Context, snsEvent events.SNSEvent) {
	Init()
	cntx := context.Background()
	computeService, err := compute.NewService(
		cntx,
		option.WithCredentialsFile(credentialsFilePath),
	)
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	req := computeService.GlobalForwardingRules.List(projectID)
	if err := req.Pages(cntx, func(page *compute.ForwardingRuleList) error {
		for _, forwardingRule := range page.Items {
			item := IPAddressFinding{
				Type:     "ip_address",
				Sk:       forwardingRule.IPAddress,
				Provider: "gcp",
			}
			isStored, err := StoreLBFindings(item)

			if err != nil {
				log.Print("Failed to save Load balancer data ", err)

			}
			log.Print("Data saved : ", isStored)
			snsMessage := &snsMessageAnalyzeIP{
				IPAddress: forwardingRule.IPAddress,
				Type:      "ip_address",
			}
			PublishSNSMessage(snsMessage, snsTopicAnalyzeIPARN)

		}
		return nil
	}); err != nil {
		log.Fatal(err)
	}
}

func main() {
	lambda.Start(collectLoadBalancers)
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
