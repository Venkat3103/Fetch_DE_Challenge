# Fetch_DE_Challenge

## Decisions
<b> 1. How will you read messages from the queue?</b>
<br /><br />
To read messages from the Amazon SQS queue, I used the boto3 library, which is the AWS SDK for Python. Reading the message involves two steps - i. Client initialization and ii. Receive messages.
<br />
* SQS Client Initialization: A client for SQS is created using boto3.client('sqs', creds). The client is configured with the endpoint URL, region, and credentials, which work with localstack.
* Receive Messages: Messages are received using sqs.receive_message(), which pulls messages from the specified SQS queue. The function uses long polling (WaitTimeSeconds=20), a strategy that reduces the number of empty responses by allowing the SQS service to wait until a message is available in the queue before sending a response. This method is efficient because it reduces the number of API calls made when the queue is empty and can retrieve messages as soon as they become available.


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
I have used the psycopg2 library to connect to the Postgres DB. This makes the integration with Python feasible. Parameters such as dbname, user, password, host, and port are sent as connection parameters to establish a connection to the Postgres DB. The connection object is further used to perform CRUD operations on the database through the Python script.

<b> 5. Where and how will your application run? </b>
<br /><br />
The script is designed to be run as a standalone Python application, which is executed on a local development environment in a docker container. Pre-existing docker images are used, which are further used to build the docker containers that run the application.

Further with more time, I would explore other encryption/hashing mechanisms, deploy this on AWS, and look at ways to orchestrate the flow and manage the dependencies between the services present. Explore other services that are new to the market that could perform the same task with better efficiency. 

## Questions
<b> 1. How would you deploy this application in production?</b>
 * Move towards more sophisticated ways of transforming data. Meaning, say using a Glue Job with PySpark which will support distributed processing. This is useful when handling high-volume complex JSON data.
 * Deploying the application in the cloud - use services such as ECS or EKS which support container orchestration and can further handle deployment, scaling, and the management of these containerized applications.
 * Use AWS SQS for message queue and Amazon Aurora for Postgres. AWS SQS is reliable at scale and Aurora provides high availability.
 * Use AWS CloudFormation or Terraform to provision application code and support infrastructure.
 * Orchestrate the pipeline with Airflow, or AWS Glue workflows if using Glue.
 - Logging errors and performance metrics will help in proactive maintenance and troubleshooting of the pipeline. For example, AWS CloudWatch can be used to keep track of the application's performance and health in real time.


<b> 2. What other components would you want to add to make this production-ready?</b><br />
 * CI/CD, version control, and code review - implement CI/CD pipelines using tools like Jenkins, GitLab CI, or GitHub Actions to automate testing and deployment. This ensures that new changes are automatically tested and deployed efficiently.
 * Disaster prevention and recovery - multi-availability zone deployment, automated backups, continuous incremental backups, point-in-time recovery
 * Handling orchestration failures - allow retries, have call-back functions, notify developers on Slack
 * Consider having multiple environments to test the pipeline before moving into production. 
 * Documentation of pipeline design, and key decisions made when setting up pipelines and implementing specific features by developers and engineers


<b> 3. How can this application scale with a growing dataset?</b>
 * Auto-scaling of both containers and database:
   * Use ECS with Application Load Balancer to manage the containerized applications while ensuring high availability and fault tolerance.
   * Aurora's autoscaling capabilities dynamically adjust the number of replicas provisioned for an Aurora DB cluster enabling it to efficiently handle sudden increases in workload.
   * We can also use database features like sharding and partitioning to handle increasing data volume.
 * AWS SQS standard queues offer maximum throughput, at-least-once delivery, and best-effort ordering making them ideal for high-volume applications. Batching operations, and adjusting visibility timeout are a couple of ways to optimize SQS message throughput when it comes to high-volume applications.
 * Explore caching mechanism for frequently accessed data which will reduce load on the database and speed up response times.
 * Choosing spark-based transformations to leverage distributed data processing.


<b> 4. How can PII be recovered later on?</b>
 * To recover PII, a deterministic encryption technique can be used since it produces the same ciphertext for a given value and the values can be decrypted later using encryption keys. However, it has to be made sure that the encryption keys are secure and inaccessible to unauthorized members. AWS Key Management Service is a great option to store encryption keys.


<b> 5. What are the assumptions you made?</b><br />
 * Messages are processed assuming that the queue is a standard queue and not a FIFO queue
 * We do not need the messages once they are processed. They are deleted once consumed.
 * However duplicate entries are allowed in the user_logins table in the Postgres database if the same message is sent again in the queue. This is because of the lack of a unique key constraint in the user_logins table schema. Currently permits inserting the same records over and over again (but this can be fixed).
 * The given table schema does not comply with the type of data arriving in the queue and hence had to be altered. The app_version is modified to varchar from int after looking at sample queue data.
 * All records coming in have to follow the schema definition and contain the required fields to be inserted into user_logins. Otherwise considered as error records and inserted into an error log table.


## Set up

1. Install Python
```https://www.python.org/downloads/```

2. Install Docker Desktop
```https://docs.docker.com/get-docker/```

3. Install Postgres
```https://www.postgresql.org/download/```

## How to run the code?

1. Clone the repository in the terminal
```bash
git clone https://github.com/Venkat3103/Fetch_DE_Challenge.git
```

3. Move into the cloned repository
```bash
cd Fetch_DE_Challenge
```

3. Install requirements - this should install all the required libraries used in the code. 
```bash
pip install -r requirements.txt
```

4. Pull Postgres docker image
```bash
docker pull fetchdocker/data-takehome-postgres
```

5. Pull localstack docker image
```bash
docker pull fetchdocker/data-takehome-localstack:latest
  ```

6. Check if docker compose is installed. Should be installed automatically if the Docker desktop for Mac is downloaded.
```bash
docker-compose --version
```

7. run docker-compose to build the containers based on the config in docker-compose.yml

```bash
docker-compose up -d
```
![image](https://github.com/Venkat3103/Fetch_DE_Challenge/assets/53090670/031d27a8-b27f-4c50-b7b4-6cfeb4838d15)

<img width="1482" alt="image" src="https://github.com/Venkat3103/Fetch_DE_Challenge/assets/53090670/8e0da743-da2a-4e23-ac31-97f1409b2e3e">


8. Run the user_login python script
```bash
python3 user_login.py
```

Log Output:

![image](https://github.com/Venkat3103/Fetch_DE_Challenge/assets/53090670/3e517048-f13f-4010-919e-bdc3443d544b)


9. Connect to postgres
```bash
psql -d postgres -U postgres -p 5432 -h localhost -W
```

10. Display user_logins table to see populated data (Note - i. 99 records were inserted after omitting the error record. ii. app_version is varchar)
```bash
select * from user_logins limit 10;
```
![image](https://github.com/Venkat3103/Fetch_DE_Challenge/assets/53090670/911dd1e5-e12e-4483-a18c-d0b5aa0240f3)



11. Display error_log_table
```bash
select * from error_log_table;
```

![image](https://github.com/Venkat3103/Fetch_DE_Challenge/assets/53090670/428a9813-584b-4686-9271-e92dcdd1074f)

