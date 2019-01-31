import boto3

# varible
tableName = 'vcloudlab_picture'
bucketName = 'vcloudlab-bucket'
queueName = 'vcloudlab_sqs_queue'

s3_endpoint_url = 'http://s3.vcloudlab.pro:4569'
sqs_endpoint_url = 'http://ap-northeast-1.queue.amazonaws.com/204065533127/vcloudlab_sqs_queue'
dynamoDB_endpoint_url = 'http://dynamodb.vcloudlab.pro:8000'

baseURL = "http://s3-ap-northeast-1.amazonaws.com/vcloudlab-bucket/"

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
sqs_client = boto3.client('sqs')
sqs_resource = boto3.resource('sqs')
dynamoDB_client = boto3.client('dynamodb')
dynamoDB_resource = boto3.resource('dynamodb')
# function
def send_message(filename):
    
    # 調用 SQS
    vlabQueues = sqs_client.list_queues( QueueNamePrefix = queueName )
    queue_url = vlabQueues['QueueUrls'][0]
    # print(queue_url)
    
    # 將 filename 透過 SQS 傳輸
    enqueue_response = sqs_client.send_message(
        QueueUrl = queue_url, 
        MessageBody = filename
    )
    # print('Message ID : ',enqueue_response['MessageId'])
    return True
    
