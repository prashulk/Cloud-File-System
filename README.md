# Cloud-File-System

<img width="869" alt="image" src="https://github.com/prashulk/Cloud-File-System/assets/67316162/d357846a-a206-4e59-ae76-e223de4ac7e8">

## Architecture -

### Components -

The GCS FUSE File System contains the following:

**- FUSE -** The FUSE library provides a bridge between user-space and kernel-space. It intercepts file system calls and redirects them to the GCS File System.
**- GCS_Bucket_FS -** The GCS_Bucket_FS class implements the file system operaAons using the FUSE library. It interacts with Google Cloud Storage to manage files and directories. This class also maintains in-memory data structures to track file metadata and content.
**- Google Cloud Storage -** The GCS component stores the actual data. The GCS File System interacts with GCS to upload, download, and manage files and directories.

- File system operations supported are -
chmod: Change file permissions.
chown: Change file ownership.
create: Create a new file.
open: Open an exisAng file.
close: Close a file.
getattr: Retrieve file or directory attributes.
getxattr: Retrieve extended attributes (placeholder implementation).
read: Read file content.
truncate: Truncate a file to a specified length.
write: Write data to a file.
mkdir: Create a new directory.
rmdir: Remove a directory.
readdir: List directory contents.
opendir: Open a directory.
flush: Flush cached data for a file.
fsync: Synchronize file data to storage.
rename: Rename a file or directory.
link: Create a hard link.
unlink: Delete a file (unlink).
