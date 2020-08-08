package main

import (
	"context"
	"fmt"	
	"log"
	"os"
	"encoding/json"
	

	"github.com/oracle/oci-go-sdk/dns"
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
	snsClient      		*sns.SNS
	dynamoDBTableAssets = os.Getenv("DynamoDBTableAssets")
	compartmentId 		= os.Getenv("OracleTenancyId")
	configPath 			= os.Getenv("OracleConfigPath")
    profileName 		= os.Getenv("OracleConfigProfile")
    analyzeDomain       = os.Getenv("SNSTopicAnalyzeDomainARN")
)

type DNSFindings struct {
	Type 					string 		`json:"type"`
    Sk  					string 		`json:"sk"`
    Provider 				string  	`json:"provider"`
}

type snsMessageCollectDomainData struct {
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


func collectDNSHandler(ctx context.Context, snsEvent events.SNSEvent) {
	Init()
	client, err := dns.NewDnsClientWithConfigurationProvider(common.CustomProfileConfigProvider(configPath, profileName))
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }

    cntx := context.Background()
    listResp, err := client.ListZones(cntx, dns.ListZonesRequest{
        CompartmentId: &compartmentId,
        SortBy:        dns.ListZonesSortByTimecreated,
        SortOrder:     dns.ListZonesSortOrderAsc,
    })
    if err != nil {
        log.Fatal(err)
        os.Exit(1)
    }
    fmt.Println("list dns zones")
    for _, dnsItem := range listResp.Items {
        
        var n * string = dnsItem.Name
        name := *n
        fmt.Println("Name : ", name)
        //fmt.Println("ZoneType : ", dnsItem.ZoneType)

		item := DNSFindings{
			Type: "domain",
		    Sk: name,
		    Provider: "oracle",  
		}
		isStored, err := StoreDNSFindings (item)

		if err != nil {
		    log.Print("Failed to save DNS ", err)
		    
		}
		log.Print("DNS saved : ", isStored)
		snsMessage := &snsMessageCollectDomainData{
			Domain: name,
			Type:   "domain",
		}
		PublishSNSMessage(snsMessage, analyzeDomain)
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
