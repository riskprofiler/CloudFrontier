package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/oracle/oci-go-sdk/common"
	"github.com/oracle/oci-go-sdk/objectstorage"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	//"github.com/aws/aws-sdk-go/service/sns"
)

var (
	dynamoDBClient *dynamodb.DynamoDB
	//snsClient      		*sns.SNS

	dynamoDBTableAssets  = os.Getenv("DynamoDBTableAssets")
	compartmentId        = os.Getenv("OracleTenancyId")
	nameSpace            = os.Getenv("OracleObjectStorageNamespace")
	configPath           = os.Getenv("OracleConfigPath")
	profileName          = os.Getenv("OracleConfigProfile")
	analyzeObjectStorage = os.Getenv("SNSTopicAnalyzeObjectStorageARN")
)

type BucketFindings struct {
	Type         string `json:"type"`
	Sk           string `json:"sk"`
	Provider     string `json:"provider"`
	PublicAccess bool   `json:"is_public"`
}

type snsMessageCollectObjectStorageData struct {
	ObjectStorage string `json:"object_storage"`
	Type          string `json:"type"`
}

func Init() {
	sess := session.New()
	dynamoDBClient = dynamodb.New(sess)
	//snsClient = sns.New(sess)
}

func StoreBucketFindings(item interface{}) (bool, error) {
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

func collectBucketHandler(ctx context.Context, snsEvent events.SNSEvent) {
	Init()
	client, err := objectstorage.NewObjectStorageClientWithConfigurationProvider(common.CustomProfileConfigProvider(configPath, profileName))
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	cntx := context.Background()
	listResp, err := client.ListBuckets(cntx, objectstorage.ListBucketsRequest{
		CompartmentId: &compartmentId,
		NamespaceName: &nameSpace,
	})

	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}
	fmt.Println("list public buckets")
	for _, bucket := range listResp.Items {

		var n *string = bucket.Name
		name := *n

		bucketDetails, err := client.GetBucket(ctx, objectstorage.GetBucketRequest{
			BucketName:    bucket.Name,
			NamespaceName: &nameSpace,
		})
		if err != nil {
			log.Fatal(err)
		}
		log.Println("PublicAccessType : ", bucketDetails.Bucket.PublicAccessType)
		var isPublic bool
		if bucketDetails.Bucket.PublicAccessType != "NoPublicAccess" {
			isPublic = true
		} else {
			isPublic = false
		}
		//if bucketDetails.Bucket.PublicAccessType != "NoPublicAccess" {
		fmt.Println("Save this bucket")
		fmt.Println(name)
		item := BucketFindings{
			Type:         "object_storage",
			Sk:           name,
			Provider:     "oracle",
			PublicAccess: isPublic,
		}
		isStored, err := StoreBucketFindings(item)

		if err != nil {
			log.Print("Failed to save Bucket ", err)

		}
		log.Print("Bucket saved : ", isStored)
		// snsMessage := &snsMessageCollectObjectStorageData{
		// 	ObjectStorage: 		name,
		// 	Type:   			"object_storage",
		// }
		//PublishSNSMessage(snsMessage, analyzeObjectStorage)
		//}

	}

}

func main() {
	lambda.Start(collectBucketHandler)
}

// PublishSNSMessage publishes the given SNS message to the given topic ARN.
// func PublishSNSMessage(messageStruct interface{}, topicARN string) {
// 	messageBytes, err := json.Marshal(messageStruct)
// 	if err != nil {
// 		fmt.Println("Error marshalling SNS message", err.Error())
// 		fmt.Println("Message struct:", messageStruct)
// 		os.Exit(1)
// 	}

// 	_, err = snsClient.Publish(&sns.PublishInput{
// 		Message:  aws.String(string(messageBytes)),
// 		TopicArn: aws.String(topicARN),
// 	})
// 	if err != nil {
// 		fmt.Println(err.Error())
// 		os.Exit(1)
// 	}
// }
