# codepipeline-slack-approver
CodePipeline To Slack Approver

Adoption of https://aws.amazon.com/blogs/devops/use-slack-chatops-to-deploy-your-code-how-to-integrate-your-pipeline-in-aws-codepipeline-with-your-slack-channel/

This solution requires the slack token to be precreate in AWS SSM Parameter Store with the following structure:

Name: /CodeBuild/SLACK_TOKEN Value: *slack_token_value* Type: SecureString
