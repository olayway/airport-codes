# sync_to_supabase.py

import os
from supabase import create_client, Client
from pathlib import Path

def sync_directory_to_supabase(storage: Client, bucket_name: str, local_dir: str, remote_dir: str = ""):
    local_path = Path(local_dir)
    if not local_path.is_dir():
        print(f"Local directory {local_dir} does not exist.")
        return

    for file_path in local_path.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(local_path)
            remote_path = os.path.join(remote_dir, str(relative_path)).replace("\\", "/")  # Ensure forward slashes
            print(f"Uploading {file_path} to {bucket_name}/{remote_path}")
            with open(file_path, "rb") as file:
                try:
                    storage.from_(bucket_name).upload(remote_path, file, upsert=True)
                except Exception as e:
                    print(f"Failed to upload {file_path}: {e}")

def main():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    dataset_type = os.getenv("DATASET_TYPE", "free").lower()

    if not supabase_url or not supabase_service_role_key:
        print("Supabase URL or Service Role Key not set.")
        exit(1)

    if dataset_type not in ["free", "premium"]:
        print("Invalid DATASET_TYPE. Must be 'free' or 'premium'.")
        exit(1)

    supabase: Client = create_client(supabase_url, supabase_service_role_key)

    bucket_name = "datasets-free" if dataset_type == "free" else "datasets-premium"
    local_data_dir = "data"  # Assuming the data is in the 'data' folder at the repository root
    remote_dir = ""  # You can set a subdirectory in the bucket if needed

    sync_directory_to_supabase(supabase, bucket_name, local_data_dir, remote_dir)
    print("Data synchronization complete.")

if __name__ == "__main__":
    main()
