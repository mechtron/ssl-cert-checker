# ssl-cert-checker

By Corey Gale (`mechtrondev[at]gmail.com`)

## Executive summary

Provisions a Lambda function that checks a configurable list of hostnames for SSL connectivity issues. Notifies you via email when checks fail. Includes a CLI tool for easy management of hostnames to monitor.

## Features

1. Checks for a variety of SSL failure modes including cert expiry, invalid hostname and broken cert chain
1. Email notifications for failures
1. List of hostnames to check stored in DynamoDB
1. Audit trail of failed checks persisted to DynamoDB (optional)
1. Includes CLI tool for managing the list of hostnames to check
1. Terraformed IaC (deploy to your AWS account in a single command)
1. Operates within AWS's free tier

#### Example notification

<img src="img/example_email_notification.png" width="500">

## CLI tool usage

Managing the list of hostnames to continually check for SSL issues is easy using. Simply use the included CLI tool:

#### Setup the CLI tool

1. Make sure Python 3 & Pip 3 are installed
1. Install pip dependencies: `pip3 install -r checker/requirements.txt --user`
1. Create a symlink to invoke the CLI tool: `ln -s $(pwd)/manage.py /usr/local/bin/ssl-cert-checker`

### Create a new check

To create a new SSL check, use the `create` action:

	ssl-cert-checker --action create --hostname example.com --notification-target admin@example.com

Here's a full list of supported parameters:

| Parameter     | Description   | Type | Default |
| :------------ |:--------------|:----:|:-------:|
| `hostname` | The hostname of the target service | required | |
| `port` | The port of the target service | optional | `443` |
| `check-interval-minutes` | How often (in minutes) to check the target hostname | required | `15` |
| `notification-target` | The target address to send failure notifications to | optional | |
| `notification-minutes-before-resending` | How long (in minutes) before re-sending failure notifications | optional | `30` |
| `cert-expiry-notify-before-days` | Notify me this many days before my certificate expires | optional | `30` |
| `failed-check-history-days` | How long (in days) to retain records of failed checks in DynamoDB (enter `0` for unlimited storage) | optional | `0` |

Example output:
	
	New on-going SSL check for example.com successfully created

### List all checks

You can list all hostnames to check for SSL issues using the `list` action:

	ssl-cert-checker --action list

Example output:

```
TODO
```

### List all check failures

You can list all failures for all hostnames using the `list-failures` action:

	ssl-cert-checker --action list-failures

Example output:

```
TODO
```

#### List check failures for a certain domain

You can list all failures for a certain hostname by adding the optional `--domain` switch:

	ssl-cert-checker --action list-failures --domain example.com

Example output:

```
TODO
```

### Delete a check

You can also delete users using the `delete` action:

	ssl-cert-checker --action delete --id 769d1308

Where `--id` is the check id which can be obtained using the `list` action.

Example output:

	SSL check with ID 769d1308 was successfully deleted

## AWS infrastructure

#### Resources

- Lambda function triggered by CloudWatch Events (fire every 5 minutes)
- DynamoDB table for hostname list and peristing failed checks
- SNS topic for email notifications
- CloudWatch Log Stream for Lambda function output

#### Estimated cost

All of the AWS resources provisioned by this project fit within [AWS's always-free tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=tier%23always-free), with a single exception that is SMS messages. Within the free tier, AWS includes 1000 notifications per month, which, depending on the reliability of your infrastructure, should be more than enough for all your failure notifications.

Just to be safe, to avoid bill shock I suggest that you set up a [billing alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) for your AWS account.

## Deploying `ssl-cert-manager` to your AWS account

#### Dependencies

1. `make`
1. Terraform v0.12.x
1. Terragrunt v0.20.x

#### Deploy an environment

1. Update the Terragrunt values in `terraform/terragrunt/terragrunt.hcl` to match your AWS account's configuration.
1. To deploy the `prod` environment (using the Terragrunt variables stored in `terraform/terragrunt/prod/terragrunt.hcl`):

		ENV=prod TF_ACTION=apply make terragrunt

#### Destroy an environment

To destroy an environment (in this case `prod`), set the `TF_ACTION` environment variable to `destroy`:

	ENV=prod TF_ACTION=destroy make terragrunt

#### Creating new environments

Creating new environments is as easy as creating a new Terragrunt environment folder:

1. Copy `terraform/terragrunt/prod/terragrunt.hcl` to a new sub-directory under `terraform/terragrunt/`. The name that you choose for this directory will be your new environment's name.
1. Update the environment's name in the newly copied `terragrunt.hcl` file under the `inputs` section near the end of the file.
1. Deploy your environment with `make`:
		
		ENV=<ENV> TF_ACTION=apply make terragrunt
		
	Where `<ENV>` is your new environment's name.

## To do

1. Add TTL to DynamoDB items in failed checks history table
1. Send `SSL_CERTIFICATE_EXPIRED` alerts before cert actually expires
1. Add support for "Fixed: back online" notifications
1. Add support for Slack notifications
1. Add GitHub Actions deployment pipeline
