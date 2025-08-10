		
## Workspace and Source Directory Layout Complexity

Mulch supports multiple modes for workspace and source directory placement, designed to balance developer convenience and user-friendly layouts. However, this flexibility introduces some complexity in how paths are referenced in `workspace_manager.py` and related tooling.

### Workspace Location Options

* **Default (public)**: Workspaces live under `/workspaces/` relative to the project root.
* **User-friendly (`--here`)**: Workspaces are created directly in the current working directory, simplifying access for non-technical users.
* **Hidden (`--stealth`)** *(deprecated for `mulch workspace`)*: Workspaces are placed under `.mulch/workspaces/` for more discreet storage.

### Source Directory Placement

* **Public**: `src/` directory visible at the project root.
* **Hidden (`--stealth`)**: `src/` lives under `.mulch/src/` to keep code hidden from non-technical collaborators.

### The Challenge

When combining these options, the path references in `workspace_manager.py` can become inconsistent or incomplete:

* If the source directory is hidden but workspaces are public, references may not align.
* If both are hidden, references are consistent but less discoverable.
* Mixing public and hidden workspaces simultaneously creates ambiguity about which workspace paths the manager should track.

### Recommendations

To maintain clarity and reliable path resolution:

* Prefer a consistent mode per project for both `src` and `workspace` directories.
* Avoid mixing hidden and public workspace directories within the same project unless you explicitly manage multiple workspace roots.
* If you need multiple workspace sets (e.g., for config vs. user data), consider enhancing `workspace_manager.py` to support multiple roots or use external configuration to declare all workspace locations.
* Remember that `mulch workspace --stealth` is deprecated — for hidden workspaces, change your working directory into `.mulch/` and run `mulch workspace` instead.

