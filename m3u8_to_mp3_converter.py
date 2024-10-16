import os
import sys
import requests
from urllib.parse import urljoin, urlparse
import subprocess
import tempfile
import time

def is_master_playlist(m3u8_content):
    """
    Determines if the m3u8 content is a master playlist.

    Args:
        m3u8_content (str): The content of the m3u8 file.

    Returns:
        bool: True if it's a master playlist, False otherwise.
    """
    for line in m3u8_content.splitlines():
        if line.startswith('#EXT-X-STREAM-INF'):
            return True
    return False

def select_variant_playlist(m3u8_content, base_url):
    """
    Selects the first variant playlist from a master playlist.

    Args:
        m3u8_content (str): The content of the master m3u8 file.
        base_url (str): The base URL to resolve relative paths.

    Returns:
        str: The URL of the selected variant playlist.
    """
    lines = m3u8_content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('#EXT-X-STREAM-INF'):
            # The next line should be the URI of the variant
            if i + 1 < len(lines):
                variant_uri = lines[i + 1].strip()
                variant_url = urljoin(base_url, variant_uri)
                return variant_url
    return None

def download_m3u8_playlist(m3u8_url):
    """
    Downloads the m3u8 playlist content from the given URL.
    If it's a master playlist, selects a variant playlist.

    Args:
        m3u8_url (str): URL of the m3u8 playlist.

    Returns:
        list: A list of absolute URLs to the audio segments.
    """
    attempt = 0
    max_attempts = 3

    while attempt < max_attempts:
        try:
            response = requests.get(m3u8_url, timeout=10)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            attempt += 1
            print(f"Error fetching m3u8 playlist (attempt {attempt}/{max_attempts}): {e}")
            if attempt == max_attempts:
                sys.exit(1)
            time.sleep(2)  # Wait before retrying

    content = response.text
    base_url = m3u8_url.rsplit('/', 1)[0] + '/'

    if is_master_playlist(content):
        print("Master playlist detected. Selecting the first variant playlist...")
        variant_url = select_variant_playlist(content, base_url)
        if not variant_url:
            print("No variant playlists found in the master playlist.")
            sys.exit(1)
        print(f"Selected variant playlist: {variant_url}")
        return download_m3u8_playlist(variant_url)  # Recursive call with variant playlist
    else:
        print("Media playlist detected. Parsing segments...")
        lines = content.splitlines()
        segment_urls = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            segment_url = urljoin(m3u8_url, line)
            segment_urls.append(segment_url)

        if not segment_urls:
            print("No audio segments found in the playlist.")
            sys.exit(1)

        return segment_urls

def download_segment(segment_url, session, temp_dir, index):
    """
    Downloads a single audio segment.

    Args:
        segment_url (str): URL of the audio segment.
        session (requests.Session): The requests session object.
        temp_dir (str): Path to the temporary directory.
        index (int): Index of the segment for naming.

    Returns:
        str: Path to the downloaded segment file.
    """
    attempt = 0
    max_attempts = 3

    while attempt < max_attempts:
        try:
            response = session.get(segment_url, stream=True, timeout=10)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            attempt += 1
            print(f"Error downloading segment {segment_url} (attempt {attempt}/{max_attempts}): {e}")
            if attempt == max_attempts:
                sys.exit(1)
            time.sleep(2)  # Wait before retrying

    # Determine file extension based on Content-Type or URL
    if 'Content-Type' in response.headers:
        content_type = response.headers['Content-Type']
        if 'audio' in content_type:
            ext = '.aac'  # Common audio segment extension
        else:
            ext = '.ts'  # Default to .ts
    else:
        ext = os.path.splitext(urlparse(segment_url).path)[1] or '.ts'

    segment_path = os.path.join(temp_dir, f"segment_{index:05d}{ext}")
    try:
        with open(segment_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except IOError as e:
        print(f"Error writing segment to file {segment_path}: {e}")
        sys.exit(1)

    return segment_path

def concatenate_segments(segment_paths, output_path):
    """
    Concatenates all audio segments into a single file.

    Args:
        segment_paths (list): List of paths to segment files.
        output_path (str): Path to the concatenated output file.
    """
    try:
        with open(output_path, 'wb') as outfile:
            for segment in segment_paths:
                with open(segment, 'rb') as infile:
                    outfile.write(infile.read())
    except IOError as e:
        print(f"Error concatenating segments: {e}")
        sys.exit(1)

def convert_to_mp3(input_path, output_path):
    """
    Converts the input audio file to MP3 format using FFmpeg.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to the output MP3 file.
    """
    try:
        subprocess.run(
            [
                'ffmpeg', '-y',
                '-i', input_path,
                '-vn',
                '-acodec', 'libmp3lame',
                '-ab', '128k',
                output_path
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"Error converting to MP3: {e.stderr.decode()}")
        sys.exit(1)
    except FileNotFoundError:
        print("FFmpeg is not installed or not found in PATH. Please install it.")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python download_audio.py <m3u8_url> <output_mp3>")
        sys.exit(1)

    m3u8_url = sys.argv[1]
    output_mp3 = sys.argv[2]

    # Validate the URL format
    if not m3u8_url.startswith('http://') and not m3u8_url.startswith('https://'):
        print("Invalid URL provided. Please provide a valid m3u8 URL.")
        sys.exit(1)

    if not output_mp3.endswith('.mp3'):
        print("Output file must have .mp3 extension.")
        sys.exit(1)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print("Downloading m3u8 playlist...")
            segment_urls = download_m3u8_playlist(m3u8_url)

            print(f"Found {len(segment_urls)} segments. Starting download...")
            session = requests.Session()
            segment_paths = []
            for index, segment_url in enumerate(segment_urls, start=1):
                print(f"Downloading segment {index}/{len(segment_urls)}: {segment_url}")
                segment_path = download_segment(segment_url, session, temp_dir, index)
                segment_paths.append(segment_path)

            concatenated_path = os.path.join(temp_dir, "concatenated.aac")  # Use .aac or .ts based on segments
            print("Concatenating segments...")
            concatenate_segments(segment_paths, concatenated_path)

            print("Converting to MP3...")
            convert_to_mp3(concatenated_path, output_mp3)

            print(f"MP3 file saved as: {output_mp3}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
