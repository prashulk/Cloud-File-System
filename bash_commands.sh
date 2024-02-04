#!/bin/bash

gcloud compute instances start praskumainstance2
gcloud compute instances list

gcloud compute scp /Users/prashulkumar/Documents/SEM-3/ECC/Assignment-3/testfuse5.py  praskumainstance2:pythonproject/
gcloud compute scp /Users/prashulkumar/Documents/SEM-3/ECC/Assignment-3/prashul-kumar-fall2023-23ecf366ca39.json praskumainstance2:pythonproject/

sudo apt-get install fuse
mkdir my_mount_point
chmod 777 my_mount_point/

python3 testfuse5.py /home/prashulkumar/my_mount_point
cd my_mount_point/


#Testcase1 -
touch testcase1.txt
cat > testcase1.txt
cat testcase1.txt 

echo "append to the same file" >> testcase1.txt 
cat testcase1.txt 
cd ..
umount my_mount_point 


#Testcase2 -

##Terminal1 -
python3 testfuse5.py /home/prashulkumar/my_mount_point

##Terminal2-
cd my_mount_point/
cat data.txt
cd ..
umount my_mount_point


#Testcase3 -

##Terminal1 -
python3 testfuse5.py /home/prashulkumar/my_mount_point

##Terminal2:
cd my_mount_point/
mkdir testfolder/
cd testfolder/
mkdir subtestfolder/
touch file1.txt
touch file2.txt
ls
rmdir subtestfolder/
ls
cd ..
ls
rmdir testfolder/
cd ..
umount my_mount_point



#TestCase4 -

##Terminal1:
python3 testfuse5.py /home/prashulkumar/my_mount_point

##Terminal2:
cd my_mount_point/
ls
touch file10.txt
ls
nano file10.txt
cd ..
umount my_mount_point 



#TestCase5 -

##Terminal1:
python3 testfuse5.py /home/prashulkumar/my_mount_point

##Terminal2:
cd my_mount_point/
touch testcase5.txt
ls
unlink testcase5.txt
ls
touch testrename.txt
ls
echo "some content" > testrename.txt 
mv testrename.txt testnewname.txt
ls
cat testnewname.txt 
link testnewname.txt hardlink.txt
ls
cd ..
umount my_mount_point



#Performance testing using fio -
#Test1 -
##Native Fs (VM) -
sudo apt-get install fio

mkdir test/
chmod 777 test/
cd test/
fio --name=test --size=25k --filename=/home/prashulkumar/test/testfile


##Mounted directory -
python3 testfuse5.py /home/prashulkumar/my_mount_point

cd my_mount_point/
ls
mkdir test/
chmod 777 test
ls
cd test/
fio --name=test --size=25k --filename=/home/prashulkumar/my_mount_point/test/testfile





