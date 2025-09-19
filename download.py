import kagglehub

# Download latest version
path = kagglehub.dataset_download("cwthompson/tectonic-plate-boundaries")

print("Path to dataset files:", path)