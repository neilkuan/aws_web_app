# 引用設定
import variable

# 服務名稱
bucketName = variable.bucketName
queueName = variable.queueName
tableName = variable.tableName

# 服務連線
s3_resource = variable.s3_resource
sqs_client = variable.sqs_client
dynamoDB_resource = variable.dynamoDB_resource

# 使用的參數
# http://s3.vcloudlab.pro:4569/S3/vcloudlab_bucket/
baseUrl = variable.baseURL
# 若是創建過服務就直接調用
# 調用 SQS
vlabQueues = sqs_client.list_queues( QueueNamePrefix = 'vcloudlab_sqs_queue' )
queue_url = vlabQueues['QueueUrls'][0]
print(queue_url)

# 調用 dynamoDB Table
vlabTable = dynamoDB_resource.Table(tableName)

# 用 flask 建立上傳環境
import os
import datetime
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/app/pic/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'chickenleg'

# 解析檔案名稱
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pre_show():
    
    from flask_table import Table, Col
    
    class ItemTable(Table):
        ID = Col('ID')
        Filename = Col('Filename')
        Url = Col('FileURL')
        Datetime = Col('Datetime')
    res =  vlabTable.scan(AttributesToGet=['id'])
    ID_MAX =res['Count']

    class Items(object):
        def __init__(self, ID, Filename, Url, Datetime):
            self.ID = ID
            self.Filename = Filename
            self.Url = Url
            self.Datetime = Datetime
    if ID_MAX == 0 :
        items = [Items(' ',' ',' ',' ')]
        table = ItemTable(items,border="1")
    else :    
        for item_id in range(1,ID_MAX+1):
            response = vlabTable.get_item(
                Key={
                    'id': str(item_id),
                }
            )

            item = response['Item']

            if item_id == 1 :
                items = [Items(item['id'], item['filename'], 
                        item['fileurl'], item['datetime'])]
            else : 
                items += [Items(item['id'], item['filename'], 
                        item['fileurl'], item['datetime'])]

        table = ItemTable(items,border="1")
        print(table.__html__())
    return (table)

def show_table(table):
    from flask import render_template
    
    return render_template('table.html',table=table)

pre_show()

from flask import send_from_directory
# 建立轉址位址

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
@app.route('/show', methods=['GET', 'POST'])
def show():
#    if request.method == 'POST':       
    if request.form.get('back') == "back":
        return redirect(url_for('upload_file'))
    table = pre_show()
    return show_table(table)

# 建立上傳網址
@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        
        if request.form.get('Upload') == "Upload":
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                                # 儲存在 jupyter 本地端
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                        # 上傳到 S3
                s3_resource.meta.client.upload_file(
                    '/app/pic/'+str(filename), 
                    bucketName, 
                    str(filename)
                )

                enqueue_response = sqs_client.send_message(
                    QueueUrl = queue_url, 
                    MessageBody = filename
                )
                print('Message ID : ',enqueue_response['MessageId'])
                
                                            # 透過 SQS  將 filename 抓取
                while True:
                    messages = sqs_client.receive_message(
                      QueueUrl = queue_url,
                      MaxNumberOfMessages = 10
                    ) 
                    if 'Messages' in messages: 
                        for message in messages['Messages']: # 'Messages' is a list
                            # process the messages
                            print(message['Body'])

                            # 先判斷目前的 id
                            res =  vlabTable.scan(AttributesToGet=['id'])
                            getId = res['Count']
                            setId = getId+1

                            # 將取得的 filename 存入 dynamodb
                            time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                            vlabTable.put_item(
                               Item = {
                                   'id': str(setId),
                                   'datetime': str(time),
                                   'fileurl': str(baseUrl)+str(filename),
                                   'filename': str(filename),
                               }
                            )

                            # 將在SQS佇列的Message刪除
                            sqs_client.delete_message(
                              QueueUrl = queue_url,
                              ReceiptHandle=message['ReceiptHandle']
                            )
                    else:
                        print('Queue is now empty')
                        break


                return '''
                <!doctype html>
                <title>Upload Success</title>
                <style>
                body {
                  background-image: url("https://i.imgur.com/W7d0Df4.png");
                  background-repeat: no-repeat;
                  background-position: top right;
                  background-size: 660px 820px;
                }
                div {
                  background-image: linear-gradient(white, green);
                }
                h1,h2 {
                  font-family: verdana;
                  text-shadow: 2px 2px 5px green;
                }
                </style>
                <h1>Upload Success</h1>
                <br>
                <br>
                <form method=post>
                  <input type=submit value=back name=back>
                </form>
                '''




        elif request.form.get('back', None) == "back":
            if request.form.get('back') =="back":
                return redirect(url_for('upload_file'))

        elif request.form.get('show', None) == "show":
            return redirect(url_for('show'))



        else :
            return "上傳失敗"
            


    
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <style>
    div {
      background-image: linear-gradient(white, green);
    }
    h1,h2 {
      font-family: verdana;
      text-shadow: 2px 2px 5px green;
    }
    body {
      background-image: url("https://i.imgur.com/W7d0Df4.png");
      background-repeat: no-repeat;
      background-position: top right;
      background-size: 660px 820px;
    }
    </style>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload name=Upload>
    </form>
    <br>
    <br>
    <h2>Show DynamoDB Table</h2>
    <form method=post>
      <input type=submit value=show name=show>
    </form>
    '''
app.run(host='0.0.0.0')
