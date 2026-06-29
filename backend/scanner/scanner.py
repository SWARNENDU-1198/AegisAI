from pathlib import Path

def scan_directory(directory):
    files = []

    path = Path(directory)

    for item in path.rglob("*"):

        if item.is_file():

            try:
                file_info = {
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size,
                    "extension": item.suffix
                }

                files.append(file_info)

            except Exception:
                pass

    return files
def scan_multiple_directories(directories):

    all_files = []

    for directory in directories:

        try:
            files = scan_directory(directory)
            all_files.extend(files)

        except Exception as e:
            print(f"Error scanning {directory}: {e}")

    return all_files
