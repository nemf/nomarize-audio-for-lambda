import boto3
import os
import subprocess
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def get_max_volume(file_path):
    cmd = [
        "ffmpeg", "-i", file_path,
        "-af", "volumedetect", "-f", "null", "/dev/null"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split('\n'):
        if "max_volume" in line:
            return float(line.split(':')[1].strip().split(' ')[0])
    return None

def normalize_audio(input_path, output_path, target_level=-5):
    max_volume = get_max_volume(input_path)
    if max_volume is None:
        raise ValueError("Failed to get max volume")
    
    volume_increase = target_level - max_volume
    cmd = [
        "ffmpeg", "-i", input_path,
        "-af", f"volume={volume_increase}dB",
        "-c:v", "copy", output_path
    ]
    subprocess.run(cmd, check=True)

def ensure_s3_folder_exists(bucket, folder):
    try:
        s3_client.put_object(Bucket=bucket, Key=(folder + '/'))
    except Exception as e:
        logger.error(f"Error creating folder {folder} in bucket {bucket}: {str(e)}")
        raise

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    logger.info(f"File {key} was uploaded to bucket {bucket}")
    
    file_name = os.path.basename(key)
    tmp_input_path = f"/tmp/{file_name}"
    tmp_output_path = f"/tmp/normalized_{file_name}"
    
    try:
        # Download file from S3
        s3_client.download_file(bucket, key, tmp_input_path)
        logger.info(f"File downloaded to {tmp_input_path}")
        
        # Check file size
        file_size = os.path.getsize(tmp_input_path)
        logger.info(f"File size: {file_size} bytes")
        
        # Normalize audio
        normalize_audio(tmp_input_path, tmp_output_path)
        logger.info(f"Audio normalized and saved to {tmp_output_path}")
        
        # Ensure 'source' folder exists, create if necessary
        ensure_s3_folder_exists(bucket, 'source')
        
        # Upload normalized file to S3 'source' folder
        normalized_s3_key = f"source/normalized_{file_name}"
        s3_client.upload_file(tmp_output_path, bucket, normalized_s3_key)
        logger.info(f"Normalized file uploaded to s3://{bucket}/{normalized_s3_key}")
        
        # Optional: Delete original S3 object
        s3_client.delete_object(Bucket=bucket, Key=key)
        logger.info(f"Original file {key} deleted from S3 bucket {bucket}")
        
        # Processing complete
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing file {key}: {str(e)}")
        raise
    finally:
        # Clean up temporary files
        for path in [tmp_input_path, tmp_output_path]:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Temporary file {path}th} removed")

    return {
        'statusCode': 200,
        'body': f'File processed and normalized successfully. Uploaded to s3://{bucket}/{normalized_s3_key}'
    }
