package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/sqs"
)

var sqsClient *sqs.SQS

func initial() {
	sess, err := session.NewSession()
	if err != nil {
		log.Println("Could not create new session: ", err)
	}
	sqsClient = sqs.New(sess)
}

func handler(ctx context.Context, snsEvent events.SNSEvent) {
	initial()
	msg := snsEvent.Records[0].SNS.Message
	fmt.Println("Message: ", msg)
	qURL := os.Getenv("SQSQueueNmapURL")
	res, err := sqsClient.SendMessage(&sqs.SendMessageInput{
		QueueUrl:    &qURL,
		MessageBody: &msg,
	})
	if err != nil {
		log.Println("Could not send SNS message: ", err)
		return
	}
	log.Println("Success: ", *res.MessageId)
}

func main() {
	lambda.Start(handler)
}
