import time
import os
from pathlib import Path  # <--- The Modern Fix
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- IMPORTS ---
from ingest_vectors import ingest_single_file
try:
    from batch_processor import process_single_file
except ImportError:
    # Fallback if import fails
    def process_single_file(input_path, output_dir):
        print(f"❌ MOCK CALL: Process {input_path}")

# --- CONFIGURATION ---
BASE_DIR = Path(os.getcwd()) # Current working directory as a Path object

DIRS = {
    "raw_retail":    BASE_DIR / "data" / "retail" / "scraped",
    "raw_inst":      BASE_DIR / "data" / "institutional" / "scraped",
    "proc_retail":   BASE_DIR / "data" / "retail" / "processed",
    "proc_inst":     BASE_DIR / "data" / "institutional" / "processed"
}

class PipelineHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return

        # Convert the incoming string path to a Path Object
        # This standardizes it immediately
        file_path = Path(event.src_path)
        filename = file_path.name
        
        # Ignore temp files
        if filename.startswith(".") or filename.startswith("~$"):
            return

        print(f"\n👀 Detected: {filename}")
        
        # Get the parent folder as a Path object
        parent_dir = file_path.parent

        # Wait for file write to complete
        time.sleep(1)

        # --- LOGIC: Compare Path Objects (Not Strings) ---
        
        # 1. RAW RETAIL
        if parent_dir == DIRS["raw_retail"]:
            print("   ✅ MATCH: Retail Raw -> Processing...")
            process_single_file(str(file_path), str(DIRS["proc_retail"]))

        # 2. RAW INSTITUTIONAL
        elif parent_dir == DIRS["raw_inst"]:
            print("   ✅ MATCH: Institutional Raw -> Processing...")
            process_single_file(str(file_path), str(DIRS["proc_inst"]))

        # 3. PROCESSED RETAIL
        elif parent_dir == DIRS["proc_retail"] and filename.endswith(".json"):
            print("   ✅ MATCH: Retail JSON -> Ingesting...")
            ingest_single_file(str(file_path), "retail")

        # 4. PROCESSED INSTITUTIONAL
        elif parent_dir == DIRS["proc_inst"] and filename.endswith(".json"):
            print("   ✅ MATCH: Institutional JSON -> Ingesting...")
            ingest_single_file(str(file_path), "institutional")

        else:
            print("   ❌ IGNORED: File is in a folder we aren't targeting.")
            print(f"      File is in: {parent_dir}")
            print(f"      We want:    {DIRS['raw_retail']}")

def start_pipeline():
    observer = Observer()
    
    # Schedule watchers for all 4 folders
    for key, path_obj in DIRS.items():
        # Ensure folder exists
        path_obj.mkdir(parents=True, exist_ok=True)
        
        # Watchdog needs string paths, not Path objects
        observer.schedule(PipelineHandler(), str(path_obj), recursive=False)
        print(f"🔭 Watching: {path_obj}")

    observer.start()
    print("\n✅ PIPELINE ACTIVE (Pathlib Mode).")
    print("   [Ctrl+C to stop]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Pipeline stopped.")
    
    observer.join()

if __name__ == "__main__":
    start_pipeline()