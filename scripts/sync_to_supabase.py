import os
from supabase import create_client, Client
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(dotenv_path="/Users/o/Projects/airport-codes/.env")

def sync_directory_to_supabase(supabase: Client, bucket_name: str, dataset_name: str = ""):
    data_dir = Path('./data')
    dataset_version = "latest" # TODO: Implement versioning
    if not data_dir.is_dir():
        print(f"Local directory {data_dir} does not exist.")
        return

    for file_path in data_dir.rglob('*'):
        print(file_path)
        if file_path.is_file():
            remote_path = os.path.join(dataset_name, dataset_version , str(file_path)).replace("\\", "/")  # Ensure forward slashes
            print(f"Uploading {file_path} to {bucket_name}/{remote_path}")
            with open(file_path, "rb") as file:
                try:
                    supabase.storage.from_(bucket_name).upload(file=file,path=remote_path,file_options={"cache-control": "3600", "upsert": "true"})
                except Exception as e:
                    print(f"Failed to upload {file_path}: {e}")

def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_service_role_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    dataset_type = os.environ.get("DATASET_TYPE", "free")
    dataset_name = os.environ.get("GITHUB_ACTION_REPOSITORY")

    if not supabase_url or not supabase_service_role_key:
        print("Supabase URL or Service Role Key not set.")
        exit(1)

    if not dataset_name:
        print("GITHUB_ACTION_REPOSITORY not set.")
        exit(1)

    if dataset_type not in ["free", "premium"]:
        print("Invalid DATASET_TYPE. Must be 'free' or 'premium'.")
        exit(1)

    supabase: Client = create_client(supabase_url, supabase_service_role_key)

    bucket_name = "free" if dataset_type == "free" else "premium"

    sync_directory_to_supabase(supabase, bucket_name, dataset_name)
    print("Data synchronization complete.")

if __name__ == "__main__":
    main()
