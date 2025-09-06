DOTMULCH_STANDARD_SCAFFOLD = {
        "": ["scripts", "tools", "templates", "configurations", "about_this_workspace.md"],
        "configurations": ["default-workspace.toml", "logging.json"],
        "scripts": ["to-be-run-at-creation.yaml"],
        "tools": ["to-be-used-as-needed.toml"]
    }
        
def build_dotmulch_standard_contents(target_dir, scaffold_dict = None):
    if scaffold_dict is None:
        scaffold_dict = DOTMULCH_STANDARD_SCAFFOLD
        