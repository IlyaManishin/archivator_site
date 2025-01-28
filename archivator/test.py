import subprocess

def _archivate(src_path):
    subprocess.call(["zip", src_path, "/home/mashina/Documents/projects/archivator_site_proj/media/storage/files_to_archivate"])
    
_archivate("/home/mashina/Documents/projects/archivator_site_proj/media/storage/files_to_archivate/ab5giesLYq_notes.zip")
