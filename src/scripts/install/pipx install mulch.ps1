# Run pipx install (you can add --force or upgrade flags)
pipx install mulch

# Build mulch folder (change 'userprofile' to 'localappdata' if desired)
.\build-local-mulch-dir.ps1 -Location userprofile

# Apply registry context menu integration
.\install-mulch-context.ps1
