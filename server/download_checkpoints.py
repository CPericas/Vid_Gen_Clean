from huggingface_hub import hf_hub_download
import shutil
import os

# Where to put the files
target_dir = os.path.join(os.getcwd(), "SadTalker", "checkpoints")
os.makedirs(target_dir, exist_ok=True)

files = [
    "checkpoints/mapping_00109.pth.tar",
    "checkpoints/mapping_00229.pth.tar",
    "checkpoints/facevid2vid_00189.pth.tar"
]

for fname in files:
    print(f"Downloading {fname}...")
    path = hf_hub_download(
        repo_id="vinthony/SadTalker",
        filename=fname
    )
    shutil.copy(path, os.path.join(target_dir, os.path.basename(fname)))
    print(f"Copied {os.path.basename(fname)} to {target_dir}")
