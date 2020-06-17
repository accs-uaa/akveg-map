# Geospatial Processing Virtual Machine

*Author*: Timm Nawrocki, Alaska Center for Conservation Science

*Last Updated*: 2020-06-07

*Description*: Instructions to create a virtual machine (vm) instance on Google Cloud Compute configured with 2 vCPUs, 7.5 GB of CPU memory, a 1000 GB persistent disk, and Ubuntu 18.04 LTS operating system. The machine will be capable of running R scripts from a RStudio Server installation through a web browser. Most of the Google Cloud Compute Engine configuration can be accomplished using the browser interface, which is how configuration steps are explained in this document. If preferred, all of the configuration steps can also be scripted using the Google Cloud SDK. Users should download and install the [Google Cloud SDK](https://cloud.google.com/sdk/) regardless because it is necessary for batch file uploads and downloads.

## 1. Configure project
Create a new project if necessary and enable API access for Google Cloud Compute Engine.

### Create a storage bucket for the project:
Create a new storage bucket. Select "regional" and make the region the same as the region that your virtual machine will be in. If your virtual machines must be in multiple regions, it is not necessary to have a bucket for each region if you will just be uploading and downloading files between the two.

The storage bucket in this example is named "beringia".

Use the "gsutil cp -r" command to copy data to and from the bucket. Example:

```
gsutil cp -r gs://beringia/speciesData/* ~/speciesData/
```

The '*' is a wildcard. The target directory should already exist in the virtual machine or local machine. If the google bucket is the target, the bucket will create a new directory from the copy command.

### Configure a firewall rule to allow browser access of RStudio Server:
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

## 2. Configure a new vm instance
The following steps must be followed every time a new instance is provisioned. The first vm will serve as a image template for the additional vms. The software and data loaded on the template vm are exported as a custom disk image along with the operating system. Each additional instance can use the custom disk image rather than requiring independent software installation and data upload.

### Create a new instance with the following features:

*Name*: instance-#

*Region*: us-west1 (Oregon) 

*Zone*: us-west1-b

*Machine Type*: 2 vCPUs (7.5 GB memory)

*Boot Disk*: Ubuntu 18.04 LTS

*Boot Disk Type*: Standard Persistent Disk

*Size (GB)*: 1000

*Service Account*: Compute Engine default service account

*Access scopes*: Allow full access to all Cloud APIs

*Firewall*: Allow HTTP Traffic, Allow HTTPS traffic

*Deletion Rule*: Uncheck



After hitting the create button, the new instance will start automatically.

Navigate to VPC Network -> External IP Addresses.

Change the instance IP Address to static from ephemeral and assign a name that matches the vm instance.

Launch the terminal in a browser window using ssh.

### Set up the system environment:

Update the system prior to installing software and then install necessary base packages.

```
sudo apt-get update
```

Install latest R release. The version referenced in the example below may need to be updated. The repository version should match the Ubuntu Linux LTS release version.

```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
sudo add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran40/'
sudo apt update
sudo apt install r-base
sudo apt install libgeos-dev libproj-dev libgdal-dev libudunits2-dev
sudo apt-get update
sudo -i R
```

Once R has started in the root directory, install the necessary libraries.

```
install.packages('dplyr')
install.packages('raster')
install.packages('rgdal')
install.packages('sp')
install.packages('stringr')
```

To quit R, type `q()`.

Install latest R Studio Server.

```
sudo apt-get install gdebi-core
wget https://download2.rstudio.org/server/bionic/amd64/rstudio-server-1.3.959-amd64.deb
sudo gdebi rstudio-server-1.3.959-amd64.deb
rm rstudio-server-1.2.5019-amd64.deb
```

Once R Studio Server is installed, it will automatically start running.

### Set up RStudio Server user and password:

Add a separate user for R Studio that will have a password separate from the Google authentication. Enter the password at the prompt.

```
sudo adduser <username_rstudio>
```

Add the new user to the super user group.

```
sudo usermod -aG sudo <username_rstudio>
```

The new username and password will serve as the login information for RStudio Server. All of the files accessible to RStudio must be added to the RStudio user. To switch user within the Ubuntu shell, enter the following command:

```
su <username_rstudio>
```

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

### Download files to the virtual machine:
```
cd ~
mkdir ~/example
gsutil cp -r gs://beringia/example/* ~/example/
```

The vm instance is now configured and ready to run processes on R Studio Server.

### Create a custom disk image from template vm:
Creating a custom disk image will allow additional vms to be created that are identical to the template including all files and installed software. This can save much time when creating clusters of vms.
1. Stop the vm
2. Select Compute Engine -> Images
3. Click 'Create Image'
4. Name the image
5. Leave 'Family' blank
6. Select the template vm as the 'Source disk'

Once the image creates successfully, other vm can be created using the custom image, obviating the need to install software and load files for each vm independently.

## 3. Access R Studio Server
RStudio will be running automatically once set up and does not need manual start and stop. In a browser, navigate to http://<your_VM_IP>:8787/

**IMPORTANT: When finished, the instance must be stopped to prevent being billed additional time**.

The instance can be stopped in the browser interface or by typing the following command into the Google Cloud console:

```
gcloud compute instances stop --zone=us-west1-b <instance_name>
```

**IMPORTANT: Release static ip address after instance is deleted to avoid being billed for unattached static ip.**