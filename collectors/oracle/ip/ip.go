package main

import (
	"context"
	"fmt"	
	"log"
	"os"
	"encoding/json"

	"github.com/oracle/oci-go-sdk/core"
    "github.com/oracle/oci-go-sdk/common"
    

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/sns"
)

var (
	dynamoDBClient      *dynamodb.DynamoDB
	snsClient           *sns.SNS
	dynamoDBTableAssets = os.Getenv("DynamoDBTableAssets")
	compartmentId 		= os.Getenv("OracleTenancyId")
	configPath 			= os.Getenv("OracleConfigPath")
    profileName 		= os.Getenv("OracleConfigProfile")
    analyzeIP           = os.Getenv("SNSTopicAnalyzeIPARN")
)

type IPFindings struct {
	Type 					string 		`json:"type"`
    Sk  					string 		`json:"sk"`
    Provider 				string  	`json:"provider"`
}

type snsMessageCollectIPData struct {
	IPAddress string `json:"ip_address"`
	Type      string `json:"type"`
}

func Init() {
	sess := session.New()
	dynamoDBClient = dynamodb.New(sess)
	snsClient = sns.New(sess)
}

func StoreIPFindings(item interface{}) (bool, error) {
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


func collectIPsHandler(ctx context.Context, snsEvent events.SNSEvent) {
	Init()
    client, err := core.NewVirtualNetworkClientWithConfigurationProvider(common.CustomProfileConfigProvider(configPath, profileName))
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }

    cntx := context.Background()
    listResp, err := client.ListPublicIps(cntx, core.ListPublicIpsRequest{
        CompartmentId: &compartmentId,
        Scope: "REGION",
    })
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
    fmt.Println("list public IPs")
    for _, ipItem := range listResp.Items {
        
        var n * string = ipItem.IpAddress
        address := *n
        fmt.Println("Address : ", address)

		item := IPFindings{
			Type: "ip_address",
		    Sk: address,
		    Provider: "oracle",    
		}
		isStored, err := StoreIPFindings (item)

		if err != nil {
		    log.Print("Failed to save IPs ", err)
		    
		}
		log.Print("IP saved : ", isStored)
		// publish SNS message to trigger scans for this IP address:
		snsMessage := &snsMessageCollectIPData{
			IPAddress: address,
			Type:      "ip_address",
		}
		PublishSNSMessage(snsMessage, analyzeIP)
    }



}

func main() {
	lambda.Start(collectIPsHandler)
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