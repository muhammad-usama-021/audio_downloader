# Audio Downloader

A Python script to download audio segments from a given m3u8 playlist URL and convert them into MP3 format.

## Features
- Downloads audio segments from m3u8 playlists (for testing use "https://ottverse.com/free-hls-m3u8-test-urls/").
- Handles master playlists by selecting the first variant.
- Concatenates downloaded segments into a single audio file.
- Converts the final audio file to MP3 format using FFmpeg.

## Installation

### Step 1: Install Python

Ensure you have Python 3.x installed. You can download it from [python.org](https://www.python.org/downloads/).

### Step 2: Install FFmpeg

FFmpeg is required to convert audio files to MP3 format. Follow these steps to install it from Gyan.dev:

#### Windows

1. **Download FFmpeg**:
   - Visit the [FFmpeg builds page by Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
   - Under "Release", download the **"git-full"** version (e.g., `ffmpeg-release-full.7z`).

2. **Extract the ZIP file**:
   - Extract the downloaded archive using a program like 7-Zip to a directory of your choice (e.g., `C:\ffmpeg`).

3. **Add FFmpeg to System PATH**:
   - Right-click on "This PC" or "Computer" on your desktop or in File Explorer, and select "Properties."
   - Click on "Advanced system settings" on the left.
   - Click on the "Environment Variables" button.
   - In the "System variables" section, scroll down and select the `Path` variable, then click "Edit."
   - Click "New" and add the path to the `bin` directory of FFmpeg (e.g., `C:\ffmpeg\bin`).
   - Click "OK" to close all dialog boxes.

4. **Verify Installation**:
   - Open Command Prompt and run:
     ```bash
     ffmpeg -version
     ```
   - If installed correctly, you should see the FFmpeg version information.

#### macOS

1. **Install Homebrew** (if not already installed):
   - Open Terminal and run:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

2. **Install FFmpeg**:
   - Run the following command in Terminal:
     ```bash
     brew install ffmpeg
     ```

3. **Verify Installation**:
   - Run the following command to check the installation:
     ```bash
     ffmpeg -version
     ```

#### Linux

1. **Install FFmpeg**:
   - On Debian/Ubuntu, run:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - On CentOS/RHEL, run:
     ```bash
     sudo dnf install ffmpeg
     ```

2. **Verify Installation**:
   - Run the following command:
     ```bash
     ffmpeg -version
     ```

### Step 3: Clone the Repository

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your_username/audio_downloader.git
   cd audio_downloader

## License
This script is created by Muhammad Usama!