# Statistical Learning Virtual Machine

*Author*: Timm Nawrocki, Alaska Center for Conservation Science

*Last Updated*: 2020-06-07

*Description*: Instructions to create a virtual machine (vm) instance on Google Cloud Compute configured with 16 vCPUs, 60 GB of CPU memory, a 1000 GB persistent disk, and Ubuntu 18.04 LTS operating system. The machine will be capable of running Jupyter Notebooks from an Ananconda 3 installation through a web browser. Most of the Google Cloud Compute Engine configuration can be accomplished using the browser interface, which is how configuration steps are explained in this document. If preferred, all of the configuration steps can also be scripted using the Google Cloud SDK. Users should download and install the [Google Cloud SDK](https://cloud.google.com/sdk/) regardless because it is necessary for batch file uploads and downloads.

## 1. Configure project
Create a new project if necessary and enable API access for Google Cloud Compute Engine.

### Create a storage bucket for the project
Create a new storage bucket. Select "regional" and make the region the same as the region that your virtual machine will be in. If your virtual machines must be in multiple regions, it is not necessary to have a bucket for each region if you will just be uploading and downloading files between the two.

The storage bucket in this example is named "beringia".

Use the "gsutil cp -r" command in Google Cloud SDK to copy data to and from the bucket. Example:

```
gsutil cp -r gs://beringia/example/* ~/example/
```

The '*' is a wildcard. The target directory should already exist in the virtual machine or local machine. If the google bucket is the target, the bucket will create a new directory from the copy command. Load all necessary data for analysis into the google bucket. This is most easily done using the Google Cloud SDK rather than the browser interface.

### Configure a firewall rule to allow browser access of Jupyter Notebooks:
The firewall rule must be configured once per project. Navigate to VPC Network -> Firewall Rules and create new firewall rule with the following features:

*Name*: jupyter-rule

*Description*: Allows online access to Jupyter Notebooks and Jupyter Labs.

*Network*: default

*Priority*: 1000

*Direction of traffic*: Ingress

*Action on match*: Allow

*Targets*: All instances in the network

*Source filter*: IP ranges

*Source IP ranges*: 0.0.0.0/0

*Second source filter*: None

*Protocols/ports*: Specified protocols and ports
    Check "tcp" and enter "8888"

## 2. Configure a new vm instance
The following steps must be followed every time a new instance is provisioned. The first vm will serve as a image template for the additional vms. The software and data loaded on the template vm are exported as a custom disk image along with the operating system. Each additional instance can use the custom disk image rather than requiring independent software installation and data upload.

### Create a new instance with the following features:

*Name*: instance-#

*Region*: us-west1 (Oregon)

*Zone*: us-west1-b

*Machine type*: 16 vCPUs (60 GB memory)

*Boot disk*: Ubuntu 18.04 LTS

*Boot disk type*: Standard Persistent Disk

*Size (GB)*: 1000

*Service account*: Compute Engine default service account

*Access scopes*: Allow full access to all Cloud APIs

*Firewall*: Allow HTTP Traffic, Allow HTTPS traffic

*Deletion rule*: Uncheck

After hitting the create button, the new instance will start automatically.

Navigate to VPC Network -> External IP Addresses.

Change the instance IP Address to static from ephemeral and assign a name that matches the vm instance.

Launch the terminal in a browser window using ssh.

### Set up the system environment:

Update the system prior to installing software and then install necessary base packages.

```
sudo apt-get update
sudo apt-get install bzip2 git libxml2-dev vim
```

Install latest Anaconda release. The version referenced in the example below may need to be updated. The repository version should match the Ubuntu Linux release version.

```
wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.s
bash Anaconda3-2020.02-Linux-x86_64.sh
```

At the option to prepend the Anaconda3 install location to PATH in your /home... enter yes.

At the option to install Microsoft VSCode enter no.

Remove the installation file and start bashrc.

```
rm Anaconda3-2020.02-Linux-x86_64.sh
source ~/.bashrc
```

The statistical models require packages that are not included in the Anaconda distribution for bayesian optimization and gradient boosting. Those must be installed using pip.

```
python3 -m pip install --upgrade pip setuptools wheel
pip install GPy
pip install GPyOpt
pip install lightgbm
```

### Set up Jupyter Notebooks for browser access:

Generate a configuration file for the Jupyter Notebooks.

```
jupyter notebook --generate-config
```

Assign a password to Jupyter. Failure to assign a strong password can result in computational or other google resources being hijacked.

```
jupyter notebook password
Enter Password: -------------
Confirm Password: -------------
```

Use vim to edit the jupyter notebook configuration file to allow access from all IP addresses. To insert in vi, enter "i" and type or paste edits. When finished editting, enter ESC the ":wq" to end inserting, save, and quit.

```
cd ~/.jupyter/
vi jupyter_notebook_config.py
```

Add the following to the top of jupyter_notebook_config.py:

```
c = get_config()

# Support inline plotting by default
c.IPKernelApp.pylab = 'inline'
# Allow access from any IP address
c.NotebookApp.ip = '*'
# Do not open browser by default
c.NotebookApp.open_browser = False
# Set the port to the same port that the firewall rule designates
c.NotebookApp.port = 8888
```

#### Download files to the virtual machine:
```
cd ~
mkdir ~/example
gsutil cp -r gs://beringia/example/* ~/example/
```

The vm instance is now configured and ready to run Jupyter Notebooks and Labs.

### Create a custom disk image from template vm:
Creating a custom disk image will allow additional vms to be created that are identical to the template including all files and installed software. This can save much time when creating clusters of vms.
1. Stop the vm
2. Select Compute Engine -> Images
3. Click 'Create Image'
4. Name the image
5. Leave 'Family' blank
6. Select the template vm as the 'Source disk'

Once the image creates successfully, other vm can be created using the custom image, obviating the need to install software and load files for each vm independently.

## 3. Access the Jupyter Notebook
The following commands must be run every time the instance is started to launch the Jupyter Notebook server. These commands must be run from the instance terminal.

First, start Jupyter Notebook server from the ssh terminal. Jupyter Notebook will start running once the command is entered. While Jupyter Notebook is running, the ssh terminal will not be available for other tasks. The Jupyter Server must be stopped (e.g., by quitting in the Jupyter browser window) prior to using the ssh terminal to transfer files or accomplish other tasks.

```
jupyter notebook
```

In a browser, navigate to http://<your_VM_IP>:8888/. Enter the password into the prompt.

**IMPORTANT: When finished, the instance must be stopped to prevent being billed additional time.**

The instance can be stopped in the browser interface or by typing the following command into the Google Cloud console:

```
gcloud compute instances stop --zone=us-west1-b <instance_name>
```

**IMPORTANT: Release static ip address after instance is deleted to avoid being billed for unattached static ip.**