# Smart-Photo-Album-Backend
Lambda Functions for Backend. Templates for Cloud Formation and Code Pipeline
1. `lambda_function.py`
   1. to get image labels using AWS Rekognition 
   2. to append user custom labels
   3. to upload those labels to AWS OpenSearch Instance (previously AWS ElasticSearch)
   4. to upload the image to image storage s3 bucket
2. `CloudFormationTemplate.yaml`:
 A comprehensive Cloud Formation Template to automate the deployment of all required AWS Services
3. `buildspec.yml` and `samTemplate.yaml`
    1. These two files help facilitate the deployment of Lambda functions from GitHub to AWS Lambda Functions
    2. `samTemplate.yaml` is for implementing CodePipeline
4. `search_photos.py`
     1. Code to get the keywords from search query and making them compatible with OpenSearch indexes
     2. Getting the images matching with the search query and returning their URLs 