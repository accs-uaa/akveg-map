# Start a new Virtual Machine on Google Cloud Compute Engine for geospatial processing in R

*Author*: Timm Nawrocki, Alaska Center for Conservation Science

*Created on*: 2018-09-10

*Description*: Instructions to create a virtual machine (vm) instance configured with 4 vCPUs, 26 GB of CPU memory, a 1000 GB persistent disk, and Ubuntu 18.04 LTS operating system. The machine will be capable of running R scripts from a RStudio Server installation through a web browser. Most of the Google Cloud Compute Engine configuration can be accomplished using the browser interface, which is how configuration steps are explained in this document. If preferred, all of the configuration steps can also be scripted using the Google Cloud SDK. Users should download and install the [Google Cloud SDK](https://cloud.google.com/sdk/) regardless because it is necessary for batch file uploads and downloads.

## Configure project
Create a new project if necessary and enable API access for Google Cloud Compute Engine. To encourage organization of tasks, it may be helpful to keep geospatial processors and machine learners in separate projects.

### Create a storage bucket for the project
Create a new storage bucket. Select "regional" and make the region the same as the region that your virtual machine will be in. If your virtual machines must be in multiple regions, it is not necessary to have a bucket for each region if you will just be uploading and downloading files between the two.

The storage bucket in this example is named "us-west1-11387".

Use the "gsutil cp -r" command to copy data to and from the bucket. Example:
`gsutil cp -r gs://us-west1-11387/speciesData/* ~/speciesData/`
The '*' is a wildcard. The target directory should already exist in the virtual machine or local machine. If the google bucket is the target, the bucket will create a new directory from the copy command.

### Configure a firewall rule to allow browser access of RStudio Server
The firewall rule must be configured once per project. Navigate to VPC Network -> Firewall Rules and create new firewall rule with the following features:

*Name*: rstudio-rule

*Description*: Allows online access to RStudio Server.

*Network*: default

*Priority*: 1000

*Direction of traffic*: Ingress

*Action on match*: Allow

*Targets*: All instances in the network

*Source filter*: IP ranges

*Source IP ranges*: 0.0.0.0/0

*Second source filter*: None

*Protocols/ports*: Specified protocols and ports
    Check "tcp" and enter "8787"

## Configure a new vm instance
The following steps must be followed every time a new instance is provisioned. The first vm will serve as a image template for the additional vms. The software and data loaded on the template vm are exported as a custom disk image along with the operating system. Each additional instance can use the custom disk image rather than requiring independent software installation and data upload.

### Use the Google Cloud Compute interface to create a new instance with the following features:

*Name*: instance-#

*Region*: us-west1 (Oregon) **Region should remain the same unless limited by infrastructure quotas**

*Zone*: us-west1-b

*Machine Type*: 4 vCPUs (26 GB memory)

*Boot Disk*: Ubuntu 18.04 LTS

*Boot Disk Type*: Standard Persistent Disk

*Delete Disk*: Uncheck

*Size (GB)*: 1000

*Service Account*: Compute Engine default service account

*Access scopes*: Allow full access to all Cloud APIs

*Firewall*: Allow HTTP Traffic, Allow HTTPS traffic

### After hitting the create button, the new instance will start automatically

### Navigate to VPC Network -> External IP Addresses
Change the instance IP Address to static from ephemeral and assign a name that matches the vm instance.

### Launch the terminal in a browser window using ssh
Using ssh for the first time will create an SSH directory and key with optional password.

#### Update apt-get
`sudo apt-get update`

#### Install bzip2, git, libxml2-dev, and vim
`sudo apt-get install bzip2 git libxml2-dev vim`

#### Install latest R release and additional packages to enable RStudio Server
```
sudo apt-get install r-base
sudo apt install libgeos-dev libproj-dev libgdal-dev libudunits2-dev
```

#### Install latest RStudio Server
```
sudo apt-get install gdebi-core
wget https://download2.rstudio.org/server/bionic/amd64/rstudio-server-1.2.5019-amd64.deb
sudo gdebi rstudio-server-1.2.5019-amd64.deb
```

#### Remove the installation file
`rm rstudio-server-1.2.5019-amd64.deb`

#### Create a user for RStudio Server and a password
Add a separate user for RStudio that will have a password separate from the Google authentication. Enter the password at the prompt.
`sudo adduser <username_rstudio>`

Add the new user to the super user group.

`sudo usermod -aG sudo <username_rstudio>`

The new username and password will serve as the login information for RStudio Server. All of the files accessible to RStudio must be added to the RStudio user. To switch user within the Ubuntu shell, enter the following command:

`su <username_rstudio>`

To enable RStudio to have read and write access over the new user directory:

```
sudo chown -R <username_rstudio> /home/<username_rstudio>/
sudo chmod -R 770 /home/<username_rstudio>/
```

Once own/mod priveleges are transferred to the <username_rstudio> user, the <username> user will not be able to access the files. To explore the files as the <username> user, the directory ownership must be changed back to the <username> user.

```
sudo chown -R <username> /home/<username_rstudio>/
sudo chmod -R 770 /home/<username_rstudio>/
```

When transferring files after transferring ownership, 'sudo' must precede the 'gsutil' call. Ownership does not need to be transferred back to the <username> user to transfer files to the Google Cloud Storage Bucket as long as 'sudo' is used.

#### Download the Google Storage bucket contents to the virtual machine
```
cd ~
mkdir ~/example
gsutil cp -r gs://us-west1-11387/example/* ~/example/
```

The vm instance is now configured and ready to run RStudio Server.

## Create a custom disk image from template vm
Creating a custom disk image will allow additional vms to be created that are identical to the template including all files and installed software. This can save much time when creating clusters of vms.
1. Stop the vm
2. Select Compute Engine -> Images
3. Click 'Create Image'
4. Name the image
5. Leave 'Family' blank
6. Select the template vm as the 'Source disk'

Once the image creates successfully, other vm can be created using the custom image, obviating the need to install software and load files for each vm independently.

## Start RStudio Server
RStudio will be running automatically once set up and does not need manual start and stop.

### Open RStudio Server
In a browser, navigate to http://<your_VM_IP>:8787/

### Upload predictions to Google Cloud storage bucket
`gsutil cp -r ~/<predictions_folder>/* gs://<bucket>/<predictions_folder>`

Make sure that the predictions folder exists in the storage bucket prior to upload.

# IMPORTANT: When finished, the instance must be stopped to prevent being billed additional time
The instance can be stopped in the browser interface or by typing the following command into the Google Cloud console:

`gcloud compute instances stop --zone=us-west1-b <instance_name>`

# IMPORTANT: Release static ip address after instance is deleted to avoid being billed for reserving an unattached static ip.
