package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"cloud.google.com/go/storage"
	"google.golang.org/api/iterator"
	"google.golang.org/api/option"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
)

var (
	dynamoDBClient      *dynamodb.DynamoDB
	dynamoDBTableAssets = os.Getenv("DynamoDBTableAssets")
	credentialsFilePath = os.Getenv("GCPCredentialsFilePath")
	projectID           = os.Getenv("GCPProjectID")
)

type ObjectStorageFindings struct {
	Type         string `json:"type"`
	Sk           string `json:"sk"`
	Provider     string `json:"provider"`
	Country      string `json:"country_name"`
	CountryCode  string `json:"country_code"`
	PublicAccess bool   `json:"is_public"`
}

type Regions struct {
	Regions []Region `json:"regions"`
}

type Region struct {
	Name        string `json:"name"`
	Country     string `json:"country"`
	CountryCode string `json:"countrycode"`
}

func Init() {
	sess := session.New()
	dynamoDBClient = dynamodb.New(sess)
}

func StoreBucketsFindings(item interface{}) (bool, error) {
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

func collectBucketsHandler(ctx context.Context, snsEvent events.SNSEvent) {
	Init()
	//msgBody := snsEvent['Records'][0]['Sns']['Message'];
	cntx := context.Background()
	client, err := storage.NewClient(
		cntx,
		option.WithCredentialsFile(credentialsFilePath),
	)
	if err != nil {
		log.Fatal(err)
		os.Exit(1)
	}

	it := client.Buckets(cntx, projectID)

	for {
		battrs, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("UniformBucketLevelAccess : %#v\n", battrs.UniformBucketLevelAccess.Enabled)
		fmt.Printf("Name : %#v\n", battrs.Name)
		fmt.Printf("Location : %#v\n", battrs.Location)
		//fmt.Printf("LocationType : %#v\n",battrs.LocationType)

		var countryName string

		regiondata, err := GetCountryData(battrs.Location)
		if err != nil {
			fmt.Print("No country data found ")
			countryName = battrs.Location

		} else {
			countryName = regiondata.Country
		}
		bucket := client.Bucket(battrs.Name)

		policy, err := bucket.IAM().V3().Policy(ctx)
		if err != nil {
			log.Fatal(err)
		}

		var str string
		var isPublic bool
		for _, binding := range policy.Bindings {
			str += strings.Join(binding.Members[:], "#")
		}
		//fmt.Println(str)
		if strings.Contains(str, "allUsers") {
			isPublic = true
		} else {
			isPublic = false
		}
		//if strings.Contains(str, "allUsers") {
		fmt.Printf("Send this bucket to DB : %#v\n", battrs.Name)
		item := ObjectStorageFindings{
			Type:         "object_storage",
			Sk:           battrs.Name,
			Provider:     "gcp",
			Country:      countryName,
			CountryCode:  battrs.Location,
			PublicAccess: isPublic,
		}
		isStored, err := StoreBucketsFindings(item)

		if err != nil {
			log.Print("Failed to save Bucket ", err)

		}
		log.Print("Bucket saved : ", isStored)

		// } else {
		// 	fmt.Printf("Not this one : %#v\n", battrs.Name)
		// }

	}

}

func main() {
	lambda.Start(collectBucketsHandler)
}
