# Fetch_DE_Challenge

<b> 1. How will you read messages from the queue?</b>
<br /><br />
To read messages from the Amazon SQS queue, I used the boto3 library, which is the AWS SDK for Python. Reading the message involves two steps - i. Client initialization and ii. Receive messages.
<br />
* SQS Client Initialization: A client for SQS is created using boto3.client('sqs', creds). The client is configured with the endpoint URL, region, and credentials, which work with localstack.
* Receive Messages: Messages are received using sqs.receive_message(...), which pulls messages from the specified SQS queue. The function uses long polling (WaitTimeSeconds=20), a strategy that reduces the number of empty responses by allowing the SQS service to wait until a message is available in the queue before sending a response. This method is efficient because it reduces the number of API calls made when the queue is empty and can retrieve messages as soon as they become available.


<b> 2. What type of data structures should be used?</b>
<br />
* Dictionaries: Used for handling JSON data from SQS messages which is later flattened. Dictionaries offer a flexible way to store and retrieve data by key, which is ideal for JSON.
* Lists: Used to aggregate transformed data entries before batch insertion into PostgreSQL. This allows efficient handling of multiple records in a single database transaction.

<b> 3. How will you mask the PII data so that duplicate values can be identified?</b>
<br />
<br />
To mask Personally Identifiable Information (PII) such as device IDs and IP addresses while ensuring that duplicates can be identified, the SHA-256 hashing function from hashlib is used.

* Hash Function: SHA-256 converts PII into a fixed-size string. This function is deterministic, so the same input will always produce the same output hash, which is crucial for identifying duplicates.
* Security: SHA-256 is secure and the hashing is irreversible. Hence we cannot retrieve the original data from the hash enhancing data security by protecting the actual PII values.

<b> 4. What will be your strategy for connecting and writing to Postgres?</b>
<br /><br />
I have used the psycopg2 library to connect to the Postgres DB. This makes the integration with Python feasible. Parameters such as dbname, user, password, host, and port are sent as connection parameters to establish a connection to the Postgres DB. The connection object is further used to perform CRUD operations on the database through the python script.

<b> 5. Where and how will your application run? </b>
<br /><br />
The script is designed to be run as a standalone Python application, which is executed on a local development environment in a docker container. Pre-existing docker images are used, which are further used to build the docker containers that run the application.
