import logging
from collections import defaultdict
from errno import ENOENT, EROFS, ENOTSUP, ENOTEMPTY, EEXIST
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time
import sys,os, threading
import urllib.parse
from google.cloud import storage
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class GCS_Bucket_FS(LoggingMixIn, Operations):

    def __init__(self, bucket):
        """
        Initializing the GCS FUSE file-system with below params.
        """
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        self.bucket = bucket
        self.populate_existing_files()
        now = time()
        self.files['/'] = dict(
            st_mode=(S_IFDIR | 0o755),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2)


    def chmod(self, path, mode):
        """
        To implement file changing permissions.
        """
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        """
        To implement changing file ownership.
        """
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid


    def create(self, path, mode):
        """
        Function to create a new file.
        """
        blob_name = path.lstrip('/')
        blob = self.bucket.blob(blob_name)

        content = b'' #just a sample content
        blob.upload_from_string(content)

        # Entry for the new file in FUSE-FS with modes and other basic params i am logging
        self.files[path] = dict(
            st_mode=(S_IFREG | mode),
            st_size=len(content),
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time(),
            st_nlink=1,
            is_read_only=False
        )

        self.fd += 1
        return self.fd


    def open(self, path, flags):
        """
        Opening file implementation.
        """
        self.fd += 1
        # read_only = flags & (os.O_RDONLY | os.O_WRONLY) == os.O_RDONLY  # Check if file is opened in read-only mode
        # self.files[path]['is_read_only'] = read_only  # Store read-only flag for later reference
        return self.fd


    def close(self,path, fh):
        """
        File close logic.
        """
        self.files[path]['st_mtime'] = time()
        return 0

    def populate_existing_files(self):
        """
        Retrieve and populate the existing files and directories present in the bucket.
        """
        blobs = list(self.bucket.list_blobs())
        
        # Get the blob name and its content
        for blob in blobs:
            blob_name = blob.name
            content = blob.download_as_text()

            # Directory is handled differently 
            is_directory = blob_name.endswith('/')
            if is_directory:
                directory_path = urllib.parse.unquote(blob_name)
                if directory_path.endswith('/'):
                    directory_path = directory_path[:-1]
                self.files['/' + directory_path] = dict(
                    st_mode=(S_IFDIR | 0o755),
                    st_size=0,  # Directories should have a size of 0
                    st_ctime=int(blob.time_created.timestamp()),
                    st_mtime=int(blob.updated.timestamp()),
                    st_atime=int(time()),
                    st_nlink=2,  # Assuming a directory has at least two links (self and parent)
                    is_read_only=False
                )
            else:
                # File is handled differently
                self.files['/' + blob_name] = dict(
                    st_mode=(S_IFREG | 0o755),
                    st_size=len(content),
                    st_ctime=int(blob.time_created.timestamp()),
                    st_mtime=int(blob.updated.timestamp()),
                    st_atime=int(time()),
                    st_nlink=1,  # Regular files generally have a link count of 1
                    is_read_only=False
                )

            self.data['/' + blob_name] = content





    def getattr(self, path, fh=None):
        """
        Get the file or directory attributes.
        """
        if path not in self.files:
            raise FuseOSError(ENOENT) # File or directory does not exist
                
        is_directory = self.files[path]['st_mode'] & S_IFDIR == S_IFDIR

        if is_directory:
            # print(f'Caught as dir {path}')
            st_mode = (S_IFDIR | self.files[path]['st_mode'])
            st_size = 0
        else:
            st_mode = self.files[path]['st_mode']
            st_size = self.files[path]['st_size']

        return {
            'st_mode': st_mode,
            'st_ctime': self.files[path]['st_ctime'],
            'st_mtime': self.files[path]['st_mtime'],
            'st_atime': self.files[path]['st_atime'],
            'st_nlink': self.files[path]['st_nlink'],
            'st_size': st_size,
            'is_read_only': self.files[path].get('is_read_only', False),
        }


    def getxattr(self, path, name):
        """
        Just a placeholder for extended attributes function.
        """
        return b'' # Just a dummy, as earlier whenever getxattr was called, it was raising error in the logs


    def read(self, path, size, offset, fh):
        """
        Read content from a file (GCS blob).
        """
        blob_name = path.lstrip('/')
        blob = self.bucket.blob(blob_name)
        content = blob.download_as_text()
        return content.encode()[offset:offset + size]
    
    def truncate(self, path, length, fh=None):
        """
        Truncate a file to the specified length.
        """
        if self.files[path]['is_read_only']:
            raise FuseOSError(EROFS) 

    def write(self, path, data, offset, fh):
        """
        Write data to a file.
        """
        if self.files[path]['is_read_only']:
            raise FuseOSError(EROFS)
        
        blob_name = path.lstrip('/')
        blob = self.bucket.blob(blob_name)
        current_content = blob.download_as_text()
        # print('curr_cont', current_content)
        # Fetch new content and append
        new_content = current_content[:offset] + data.decode(errors = 'ignore') + current_content[offset + len(data):]
        # print('new cont', new_content)
        # Upload the new content
        blob.upload_from_string(new_content)

        # Update the file system metadata
        self.files[path]['st_size'] = len(new_content)
        now = time()
        self.files[path]['st_ctime'] = now
        self.files[path]['st_mtime'] = now

        return len(data)


    def mkdir(self, path, mode):
        """
        Create a new directory in GCS.
        """
        blob_name = path.lstrip('/')

        if not blob_name.endswith('/'):
            blob_name += '/'  # Append '/' to the blob name
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string('')
        st_mode = S_IFDIR | mode

        self.files[path] = dict(
            st_mode=st_mode,
            st_nlink=2,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time()
        )

        parent_dir = os.path.dirname(path)
        self.files[parent_dir]['st_nlink'] += 1


    def rmdir(self, path):
        """
        Remove the directory.
        """
        if path not in self.files:
            raise FuseOSError(ENOENT)
       
        entries = 0

        for entry_path in self.files:
            if entry_path.startswith(path):
                entries += 1
                if entries > 1:
                    print('Not Empty')
                    raise FuseOSError(ENOTEMPTY) # If directory not empty, then not deleting
        
        blob_name = path.lstrip('/')

        if not blob_name.endswith('/'):
            blob_name += '/'

        blob = self.bucket.blob(blob_name)
        blob.delete()
        del self.files[path]
        parent_dir = os.path.dirname(path)
        self.files[parent_dir]['st_nlink'] -= 1


    def readdir(self, path, fh):
        """
        List directory contents.
        """
        entries = ['.', '..']  # Include current and parent directory
        # print('self files', self.files)

        for entry_path in self.files:
            if entry_path.startswith(path):
                subpath = entry_path[len(path):]

                if subpath == '':
                    continue
                # Split the subpath into components
                parts = subpath.split('/')
                # print(subpath)
                is_dir = self.files.get(entry_path, {}).get('st_mode', 0) & S_IFDIR == S_IFDIR

                if len(parts) == 1:
                    entries.append(parts[0])
                elif parts[0] not in entries:
                    entries.append(parts[-1])
                else:
                    pass

        for entry in entries:
            yield entry

    def opendir(self, path):
        """
        Open a directory.
        """
        print(f'opendir accessed for path: {path}')
        return 0
    
    def flush(self, path, fh):
        """
        Flush cached data for a file.
        """
        print(f'flush called for path: {path}')
        return 0
    
    def fsync(self, path, fdatasync, fh):
        """
        Synchronize file data to storage.
        """
        print(f'fsync called for path: {path}, fdatasync: {fdatasync}, fh: {fh}')
        return 0
    
    def rename(self, old, new):
        """
        Rename a file or directory.
        """
        if old not in self.files:
            raise FuseOSError(ENOENT)

        if new in self.files: # Ensuring destination does not already exists
            raise FuseOSError(EEXIST)

        # Renaming
        old_blob_name = old.lstrip('/')
        new_blob_name = new.lstrip('/')

        old_blob = self.bucket.blob(old_blob_name)
        new_blob = self.bucket.blob(new_blob_name)

        new_blob.upload_from_string(old_blob.download_as_text())
        old_blob.delete()

        self.files[new] = self.files[old]
        self.files[new]['st_mtime'] = time()
        self.files[new]['st_ctime'] = time()

        del self.files[old]

    def link(self, target, source):
        """
        Create a hard link.
        """
        if source not in self.files:
            raise FuseOSError(ENOENT)

        if target in self.files:
            raise FuseOSError(EEXIST)

        self.files[target] = self.files[source]
        self.files[target]['st_nlink'] += 1
        self.files[target]['st_mtime'] = time()
        self.files[target]['st_ctime'] = time()


    def unlink(self, path):
        """
        Delete a file (unlink).
        """
        blob_name = path.lstrip('/')
        blob = self.bucket.blob(blob_name)

        try:
            blob.delete()
        except Exception as e:
            raise FuseOSError(ENOENT)
        else:
            if path in self.files:
                del self.files[path]
    

if __name__ == '__main__':

    client = storage.Client.from_service_account_json('prashul-kumar-fall2023-23ecf366ca39.json')
    bucket_name = 'praskumabucket'
    bucket = client.bucket(bucket_name)

    print('Connected to the bucket successfully')

    mountpoint = sys.argv[1]
    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(GCS_Bucket_FS(bucket), mountpoint, foreground=True, allow_other=False, ro = False)
