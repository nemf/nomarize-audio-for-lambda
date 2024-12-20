# S3 Audio Normalizer Lambda Function

This AWS Lambda function automatically normalizes the volume of audio files (MKV format) uploaded to an S3 bucket. It uses FFmpeg to analyze and adjust the audio volume, then uploads the normalized file to a 'source' folder within the same S3 bucket.

## Features

- Triggers on S3 object creation events
- Downloads the audio file to Lambda's ephemeral storage
- Analyzes the audio to determine the maximum volume
- Normalizes the audio volume to a target level (-5dB by default)
- Creates a 'source' folder in the S3 bucket if it doesn't exist
- Uploads the normalized audio file to the 'source' folder
- Logs all operations to CloudWatch Logs

## Prerequisites

- AWS account with permissions to create and manage Lambda functions, S3 buckets, and IAM roles
- FFmpeg Lambda Layer (see setup instructions below)

## Setup

1. Create an S3 bucket or use an existing one.
2. Create a Lambda function and upload the provided Python code.
3. Set up an FFmpeg Lambda Layer:
   - Create a Lambda Layer containing the FFmpeg binary.
   - Attach this layer to your Lambda function.
4. Configure the Lambda function:
   - Set the runtime to Python 3.9 or later.
   - Increase the timeout to at least 1 minute (adjust based on your average file size).
   - Increase the memory allocation if necessary (e.g., 1024 MB).
5. Set up the IAM role for the Lambda function with the following permissions:
   - S3 read and write access to the relevant bucket
   - CloudWatch Logs write access
6. Configure an S3 trigger for the Lambda function on object creation events.

## Configuration

You can adjust the following parameters in the code:

- `target_level` in the `normalize_audio` function (default is -5dB)
- The name of the 'source' folder (default is 'source')

## Usage

Once set up, the function will automatically process any new MKV files uploaded to the configured S3 bucket. The normalized files will be placed in the 'source' folder within the same bucket.

## Logging

The function logs its operations to CloudWatch Logs. You can monitor these logs for information about each file processed, including:

- File download and upload confirmations
- Original file size
- Normalization process status
- Any errors encountered during processing

## Error Handling

The function includes basic error handling and logging. If an error occurs during processing, it will be logged to CloudWatch Logs, and the function will raise an exception.

## Limitations

- The function is designed for MKV files. Other formats may require code modifications.
- Large files may exceed Lambda's ephemeral storage limit (10.24GB).
- Processing very large files may cause the function to timeout. Adjust the timeout setting as needed.

## Contributing

Contributions to improve the function are welcome. Please submit a pull request or create an issue to discuss proposed changes.
