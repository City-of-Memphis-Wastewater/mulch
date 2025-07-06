from mulch import WorkspaceFactory, load_scaffold, workspace_factory

from pathlib import Path


# Step 1: Get parent directory of current working directory
parent_dir = Path.cwd().parent

# Step 2: Create a new subdirectory under that parent
rootdir_name = "experiment0"
rootdir_dir = Path(parent_dir) / rootdir_name
rootdir_dir.mkdir(parents=True, exist_ok=True)

scaffold = load_scaffold() # expect fallback scaffold when no file is found

print(f"scaffold = {scaffold}")

# Demonstrate another way to get the fallback scaffold
wf0 = WorkspaceFactory(
    base_path=rootdir_dir,
    workspace_name="placeholder",
    lock_data = {}
)
#print(f"wf0.FALLBACK_SCAFFOLD = {wf0.FALLBACK_SCAFFOLD}")


lock_data={
    "scaffold": scaffold,
    "generated_by": "script",
    "generated_at": "2025-07-06T12:00:00Z"
}


wf = WorkspaceFactory(
    base_path=rootdir_dir,
    workspace_name="default",
    lock_data=lock_data
)

wf.check_and_create_workspace_dirs_from_scaffold()
wf.seed_scaffolded_workspace_files()