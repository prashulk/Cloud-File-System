# Cloud-File-System

<img width="869" alt="image" src="https://github.com/prashulk/Cloud-File-System/assets/67316162/d357846a-a206-4e59-ae76-e223de4ac7e8">

## Architecture -

### Components -

The GCS FUSE File System contains the following:

**- FUSE -** The FUSE library provides a bridge between user-space and kernel-space. It intercepts file system calls and redirects them to the GCS File System.

**- GCS_Bucket_FS -** The GCS_Bucket_FS class implements the file system operaAons using the FUSE library. It interacts with Google Cloud Storage to manage files and directories. This class also maintains in-memory data structures to track file metadata and content.

**- Google Cloud Storage -** The GCS component stores the actual data. The GCS File System interacts with GCS to upload, download, and manage files and directories.

#### File system operations supported are -
  
- chmod: Change file permissions.
- chown: Change file ownership.
- create: Create a new file.
- open: Open an exisAng file.
- close: Close a file.
- getattr: Retrieve file or directory attributes.
- getxattr: Retrieve extended attributes (placeholder implementation).
- read: Read file content.
- truncate: Truncate a file to a specified length.
- write: Write data to a file.
- mkdir: Create a new directory.
- rmdir: Remove a directory.
- readdir: List directory contents.
- opendir: Open a directory.
- flush: Flush cached data for a file.
- fsync: Synchronize file data to storage.
- rename: Rename a file or directory.
- link: Create a hard link.
- unlink: Delete a file (unlink).

### Design -

#### File and Directory Operations -

**- Creation and Deletion –** To support the creation and deletion of files and directories. Deletion of files and directories is also efficiently handled, with associated GCS objects being removed.

**- Reading and Writing -** The read operation allows users to retrieve content from GCS objects, while the write operation permits them to update these objects. This design enables users to read from and write to GCS objects as if they were local files.

**- Error Handling -** In this design, the raised error codes are defined in the ‘errno’ module (e.g., ENOENT, EROFS, ENOTEMPTY, EEXIST) when errors occur. These error codes convey specific information about the nature of the error, aiding users in identifying and resolving issues effectively which are put in place based on the logs messages generated.

**- Directory Listing -** To ensure that users can easily list the contents of directories, including subdirectories and files. The ‘readdir’ operation lets users list directory contents, files and subdirectories.

**- Performance Optimization -** The system incorporates a caching mechanism using a dictionary data structure. The ```self.data``` dictionary stores file content, enhancing read performance by serving data from the cache when available. This design effectively reduces the need for frequent network requests and enhances overall performance.

**- Logging and Debugging -** This has integrated  Python ‘logging’ library to log operations, errors, and informational messages. This design allows users to adjust the logging level for debugging purposes.
  
**- Handling Read-Only Files -** In my system, I track read-only files and raise an error (EROFS) when users attempt to modify them. This design choice ensures that read-only and read-write objects are handled correctly, maintaining data integrity.

**- Open and Close Operations -** This system keeps track of file descriptors (fd) to manage open files. Users can open and close files as needed, and the ‘close’ operation updates timestamps to reflect changes.

**- Existing File and Directory Population -** The functionality of populating existing files and directories from the GCS bucket when initiated. This design choice ensures that the local file system reflects the structure and contents of the GCS bucket, making it easy for users to work with their data.

### Execution - 
<img width="874" alt="image" src="https://github.com/prashulk/Cloud-File-System/assets/67316162/4046f007-fcfc-437e-af8a-bade01b3bafd">

To run the fuse file system –
```
python3 testfuse5.py /home/prashulkumar/my_mount_point
```

This code starts the FUSE file system and mounts the created directory.
<img width="923" alt="image" src="https://github.com/prashulk/Cloud-File-System/assets/67316162/076d9ae0-0099-43ad-bdd0-a0082efa80c8">

**Test Case:** This test case shows a simple loop combining various operations –
```
Mount->create->open->write->read->close loop
```

Sequence of commands –

```
touch testcase1.txt
cat > testcase1.txt
this is some content
this is another content
echo "append to the same file" >> testcase1.txt
cat testcase1.txt
this is some content
this is another content
append to the same file
cd ..
umount my_mount_point
```
<img width="1000" alt="image" src="https://github.com/prashulk/Cloud-File-System/assets/67316162/da576efa-3a42-4a29-9def-55caf4f02725">


### Performance Testing Comparison b/w Native and Fuse(GCS):

**- First test for our native file system –**

```
sudo apt-get install fio
fio --name=test --size=25k -- filename=/home/prashulkumar/test/testfile
```

**- Now let’s go for our mounted gcs_fuse system –**
```
fio --name=test --size=25k -- filename=/home/prashulkumar/my_mount_point/test/testfile
```

**- Native FS Results:**
  • Read IOPS :1000
  • Bandwidth: 4000 KiB/s (4096 KB/s)
  • Average Read Latency: 868,778.33 ns
  • Maximum Read Latency: 3,787,000 ns
  • Standard Deviation of Read Latency: 1,535,956.75 ns
  
**- GCS Mounted Directory Results:**
  • Read IOPS: 138
  • Bandwidth: 333 KiB/s (341 KB/s)
  • Average Read Latency: 11,821,201.00 ns
  • Maximum Read Latency: 35,460,000 ns
  • Standard Deviation of Read Latency: 20,471,535.49 ns

  
- In the Native FS scenario, the system demonstrated significantly higher read performance compared to the GCS Mounted Directory. The Native FS achieved 1000 IOPS with an average latency of 868,778.33 ns. In contrast, the GCS Mounted Directory had a lower read performance, achieving 138 IOPS with an average latency of 11,821,201.00 ns.
  
**- Conclusion:**
The Native FS exhibited superior read performance in terms of both IOPS and latency, making it the preferred choice for scenarios where high read performance is essential.
These results indicate that the NaAve FS is better suited for read-heavy workloads, while the GCS Mounted Directory would have performance limitations due to its interaction with cloud storage as well as the too-many read requests limit set on the GCS bucket.




