package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/Ullaakut/nmap/v2"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	// "github.com/aws/aws-sdk-go/service/sqs"
)

var (
	dynamoDBClient      *dynamodb.DynamoDB
	dynamoDBTableAssets = os.Getenv("DynamoDBTableAssets")
	// sqsClient           *sqs.SQS
)

func initial() {
	sess, err := session.NewSession()
	if err != nil {
		log.Println("Error creating new session: ", err)
	}
	// sqsClient = sqs.New(sess)
	dynamoDBClient = dynamodb.New(sess)
}

func scan(domainOrIP string) (*nmap.Run, error) {
	scanner, err := nmap.NewScanner(
		nmap.WithTargets(domainOrIP),
		nmap.WithMostCommonPorts(100),
		nmap.WithDefaultScript(),
		nmap.WithBinaryPath("/var/task/submit/nmap"),
	)
	if err != nil {
		return nil, err
	}
	results, _, err := scanner.Run()
	if err != nil {
		return nil, err
	}
	log.Println("Successfully completed the scan...")
	return results, nil
}

func handler(ctx context.Context, snsEvent events.SNSEvent) {
	initial()
	tableContents := make(map[string]string)
	json.Unmarshal([]byte(snsEvent.Records[0].SNS.Message), &tableContents)
	assetType := tableContents["type"]
	domainOrIP := tableContents[assetType]
	fmt.Println("Domain or IP: ", domainOrIP)
	runResults, err := scan(domainOrIP)
	if err != nil {
		log.Println("Error with completing scan: ", err)
	}
	results, err := dynamodbattribute.Marshal(runResults)
	if err != nil {
		log.Println("Error in dynamodbattribute.Marshal call: ", err)
	}
	_, err = dynamoDBClient.UpdateItem(&dynamodb.UpdateItemInput{
		TableName: &dynamoDBTableAssets,
		Key: map[string]*dynamodb.AttributeValue{
			"type": {
				S: aws.String(assetType),
			},
			"sk": {
				S: aws.String(domainOrIP),
			},
		},
		ExpressionAttributeNames: map[string]*string{
			"#NMAP": aws.String("nmap_results"),
		},
		ExpressionAttributeValues: map[string]*dynamodb.AttributeValue{
			":r": {
				M: results.M,
			},
		},
		UpdateExpression: aws.String("SET #NMAP = :r"),
	})
	if err != nil {
		log.Println("Error adding data: ", err)
	} else {
		log.Println("Successfully added data to table ", dynamoDBTableAssets)
	}
}

func main() {
	lambda.Start(handler)
}
