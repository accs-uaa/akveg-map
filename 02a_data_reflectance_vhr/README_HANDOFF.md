Project Handoff: Maxar TOA/SR Processing Pipeline (v9.1.1 Update)

Technical Context

Automating a high-resolution remote sensing pipeline for Maxar imagery using Orfeo ToolBox 9.1.1. Outputs are 16-bit TOA reflectance (scaled 0-10000) for cross-sensor regression matching with Landsat SR.

1. Installation Method (OTB v9.1.1)
010_env_setup.md.md

OTB is installed as a standalone binary archive in /opt/otb/OTB-9.1.1-Linux.

Method: curl download of .tar.gz archive followed by tar extraction.

Initialization: Requires a one-time sudo run of otbenv.profile to patch internal paths.

Geoid Download: The egm96.grd file must be downloaded manually (Step 2b of setup_env.md).

Geoid Path: /opt/otb/OTB-9.1.1-Linux/share/otb/geoid/egm96.grd

2. File Architecture

100_process_maxar.py: Parent orchestrator in otb_env. Handles ortho, pansharpening, and TOA calibration via pyotb.

110_process_maxar_omnimask.py: Child inference script in omni environment. Performs cloud/shadow masking via PyTorch.

3. Critical Orchestration

The parent script uses conda run -n omni to execute the masking logic, ensuring the OTB C++ libraries in /opt/otb do not conflict with the deep learning stack.

4. Scaling & Data Format

Input: Raw Maxar NITF/RPC.

Intermediate: 16-bit uint16 TOA Reflectance (Value = Reflectance * 10000).

Mask: 8-bit uint8 (0: Clear, 1: Cloud, 2: Shadow).

5. Transition to VS Code

Open the project root in VS Code.

Verify the Geoid file exists at the specified path before running.

Reference these notes for Landsat regression module implementation.