# Production LLM RAG Course Setup Guide

## Prerequisites
   ### Windows WSL
      - Windows users should use  Windows subsystem for linux (WSL) Ubunutu 22.04.5 LTS (Jammy Jellyfish)
                  NOTE: Help can be found here: https://learn.microsoft.com/en-us/windows/wsl/install

   ### AWS
      - Create a free tier account at [AWS](https://aws.amazon.com)
      - AWS Account Inforamtion - This is not an AWS tutorial, you can find instructions on how to setup and get these values from AWS documentsion
                  AWS_REGION="eu-central-1"                                   # AWS region for cloud services
                  AWS_ACCESS_KEY="<aws_access_key>"                           # AWS access key for authentication
                  AWS_SECRET_KEY="<aws_secret_key>"                           # AWS secret key for authentication
                  AWS_CROSS_ACCOUNT_ROLE_ARN="<aws_cross_account_role_arn>"   # ARN for AWS cross-account access role
                  AWS_S3_BUCKET_NAME="decodingml-public-data"               # Name of the S3 bucket for storing application data(Keep this as 'decodingml-public-data')
                  NOTE: 
                     - Non Organizations
                        Help can be found here: https://docs.aws.amazon.com/cli/v1/userguide/cli-authentication-user.html
                     - With Organizations
                        Help can be found here: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#sso-configure-profile-token-auto-sso
      - AWS CLI version 2.22.24
                        NOTE: Help can be foudn here: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
                        NOTE: ensure after setting up your creds that on the command line you rum: `export AWS_PROFILE=<profile_name>`

   ### MongoDB CLI (optional)
      - It might come in handy to have a  way to get interactive tool for querying, optimizing, and analyzing your MongoDB data
      - CLI
                        - after install you can test: mongosh --host localhost --port 27017 --username decodingml -password decodingml
                           - show dbs
                           - use second_brain
                           - show collections
                           - db.raw_data.find().pretty()
                           - db.rag_data.find().pretty()
                           - db.runCommand({ listSearchIndexes: "rag_data" } )
                           - db.rag_data.findOne()
                           - db.rag_data.countDocuments({"embedding": {$exists: true}})
                           - db.raw_data.find({}, { content: 1, _id: 0 })
                        NOTE: https://www.mongodb.com/docs/mongodb-shell/install/

   ### OPIK
      - create a free account with Comet: https://www.comet.com/signup
      - create your project "second_brain_course"
      - get your api keys
### Notion (optional)
      - If you want to use your own data from notion
1. Go to [https://www.notion.so/profile].
2. Create an integration following [this tutorial](https://developers.notion.com/docs/authorization).
3. Copy your integration secret to programatically read from Notion.
4. Share your database with the integration:
   - Open your Notion database
   - Click the '...' menu in the top right
   - Click 'Add connections'
   - Select your integration
5. Get the correct database ID:
   - Open your database in Notion
   - Copy the ID from the URL: 
     ```
     https://www.notion.so/{workspace}/{database_id}?v={view_id}
     ```
   - The database ID is the part between the workspace name and the question mark

   
### Required Accounts & Services
1. **AWS Account**
   - Create a free tier account at [AWS](https://aws.amazon.com)
   - Set up IAM user with appropriate permissions for S3
   - Configure AWS CLI with credentials

2. **MongoDB Atlas Account**
   - Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free cluster
   - Create a database user
   - Whitelist your IP address
   - Get your connection string

3. **Notion (Optional)**
   - Create account at [Notion](https://www.notion.so)
   - Set up integration (see Notion Setup section)
   - Get integration secret
   - Share database with integration

4. **Hugging Face Account**
   - Create account at [Hugging Face](https://huggingface.co)
   - Generate API token
   - Save token securely

### Local Environment Setup

# Create and activate virtual environment using uv
To set it up and run online pipeline

```bash
# uv venv
source .venv/bin/activate
uv sync
```

# run
python main.py
