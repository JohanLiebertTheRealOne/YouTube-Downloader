#!/usr/bin/env python3
"""
YTGrabber - A modern, efficient YouTube content downloader
"""

import os
import sys
import re
import time
import json
import random
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Color constants for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

class YTGrabber:
    def __init__(self):
        # Initialize paths and settings
        self.app_name = "YTGrabber"
        self.app_version = "1.0.0"
        self.downloads_folder = Path("Downloads")
        self.downloads_folder.mkdir(exist_ok=True)
        self.cookie_file = None
        self.supported_formats = {
            "video": {"desc": "Video (mp4)", "ext": "mp4"},
            "audio": {"desc": "Audio only (mp3)", "ext": "mp3"},
            "best": {"desc": "Best quality (mp4)", "ext": "mp4"}
        }
        
        # Show welcome message and check dependencies
        self.show_welcome()
        self.check_dependencies()
        self.update_yt_dlp()
    
    def show_welcome(self):
        """Display welcome message with app info"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
        print(f"{Colors.CYAN}{Colors.BOLD}  {self.app_name} v{self.app_version} - YouTube Content Downloader{Colors.ENDC}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Download videos, playlists, and channels with ease{Colors.ENDC}")
        print(f"Downloads will be saved to: {Colors.GREEN}{self.downloads_folder.absolute()}{Colors.ENDC}\n")
    
    def check_dependencies(self) -> bool:
        """Check and install required dependencies"""
        print(f"{Colors.BOLD}Checking dependencies...{Colors.ENDC}")
        
        # Check for yt-dlp
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, check=False)
            print(f"{Colors.GREEN}✓ yt-dlp is installed{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.YELLOW}Installing yt-dlp...{Colors.ENDC}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
                print(f"{Colors.GREEN}✓ yt-dlp installed successfully{Colors.ENDC}")
            except subprocess.CalledProcessError:
                print(f"{Colors.RED}✗ Failed to install yt-dlp. Please install it manually with 'pip install yt-dlp'{Colors.ENDC}")
                return False
        
        # Check for FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=False)
            print(f"{Colors.GREEN}✓ FFmpeg is installed{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.YELLOW}⚠ FFmpeg not found. Some features may not work properly.{Colors.ENDC}")
            print(f"{Colors.YELLOW}  Please install FFmpeg from https://ffmpeg.org/download.html{Colors.ENDC}")
            
        return True
    
    def update_yt_dlp(self):
        """Update yt-dlp to the latest version"""
        print(f"{Colors.BOLD}Updating yt-dlp to latest version...{Colors.ENDC}")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                                    capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✓ yt-dlp updated successfully{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠ yt-dlp update might have failed, but we'll continue anyway{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Could not update yt-dlp: {str(e)}{Colors.ENDC}")
    
    def create_cookie_file(self) -> str:
        """Create a temporary cookie file to help bypass restrictions"""
        if self.cookie_file and os.path.exists(self.cookie_file):
            return self.cookie_file
            
        cookie_file = tempfile.mktemp(suffix=".txt")
        expiry = int(time.time()) + 31536000  # Current time + 1 year
        
        with open(cookie_file, 'w') as f:
            f.write('# Netscape HTTP Cookie File\n')
            f.write(f'# Created by {self.app_name} on {datetime.now().strftime("%Y-%m-%d")}\n\n')
            
            # Add various cookies that help bypass restrictions
            visitor_id = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_', k=26))
            ysc = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_', k=11))
            
            # Cookies that help bypass age restrictions and region locks
            f.write(f".youtube.com\tTRUE\t/\tTRUE\t{expiry}\tCONSENT\tYES+cb.20230717-07-p0.en+FX+{random.randint(100, 999)}\n")
            f.write(f".youtube.com\tTRUE\t/\tTRUE\t{expiry}\tVISITOR_INFO1_LIVE\t{visitor_id}\n")
            f.write(f".youtube.com\tTRUE\t/\tTRUE\t{expiry}\tPREF\tf6=8&f5=30&hl=en\n")
            f.write(f".youtube.com\tTRUE\t/\tTRUE\t{expiry}\tYSC\t{ysc}\n")
            f.write(f".youtube.com\tTRUE\t/\tTRUE\t{expiry}\tGPS\t1\n")
        
        self.cookie_file = cookie_file
        return cookie_file
    
    def get_random_user_agent(self) -> str:
        """Get a random modern browser user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
        ]
        return random.choice(user_agents)
    
    def normalize_url(self, url: str) -> str:
        """Normalize YouTube URL to standard format"""
        # Handle channel handles (@username)
        if url.startswith('@'):
            return f"https://www.youtube.com/{url}"
            
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            if url.startswith(('youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be')):
                return f"https://{url}"
        
        return url
    
    def get_content_type(self, url: str) -> str:
        """Determine if URL is for video, playlist, or channel"""
        url = self.normalize_url(url)
        
        # YouTube shorts
        if '/shorts/' in url:
            return 'video'
            
        # Channel patterns
        if any(pattern in url for pattern in ['/c/', '/channel/', '/user/', '@']):
            if '/videos' in url:  # Explicitly a channel videos page
                return 'channel'
            else:  # Could be a specific video on a channel
                return self.probe_url_type(url)
        
        # Playlist pattern
        if 'list=' in url:
            return 'playlist'
        
        # Default to video
        return 'video'
    
    def probe_url_type(self, url: str) -> str:
        """Use yt-dlp to determine content type for ambiguous URLs"""
        try:
            cmd = [
                'yt-dlp', '--skip-download', '--print', 'webpage_url', 
                '--no-warnings', url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            # Check output URL pattern to determine type
            output_url = result.stdout.strip()
            if 'list=' in output_url:
                return 'playlist'
            elif any(pattern in output_url for pattern in ['/channel/', '/c/', '/user/', '@']):
                if not any(vid_pattern in output_url for vid_pattern in ['watch?v=', '/shorts/']):
                    return 'channel'
            
            return 'video'
        except Exception:
            # If probing fails, assume it's a video
            return 'video'
    
    def ask_for_limit(self, content_type: str) -> str:
        """Ask user if they want to limit number of videos to download"""
        while True:
            resp = input(f"How many {content_type} videos do you want to download? "
                         f"[{Colors.CYAN}all{Colors.ENDC}/number]: ").strip().lower()
            
            if resp == "" or resp == "all":
                return "all"  # Download all videos
            
            try:
                limit = int(resp)
                if limit > 0:
                    return str(limit)
                print(f"{Colors.YELLOW}Please enter a positive number.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.YELLOW}Please enter 'all' or a number.{Colors.ENDC}")
    
    def build_download_command(self, url: str, content_type: str, 
                              format_type: str = 'best', limit: str = 'all') -> List[str]:
        """Build the yt-dlp command for downloading content"""
        # Prepare download directory and filename template
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if content_type == 'video':
            output_template = f"{self.downloads_folder}/%(title)s_{timestamp}.%(ext)s"
        elif content_type == 'playlist':
            output_template = f"{self.downloads_folder}/%(playlist_title)s/%(title)s_{timestamp}.%(ext)s"
        else:  # channel
            output_template = f"{self.downloads_folder}/%(uploader)s/%(title)s_{timestamp}.%(ext)s"
        
        # Base command with standard options
        cmd = [
            'yt-dlp',
            '--ignore-errors',
            '--no-warnings',
            '--geo-bypass',
            '--add-metadata',
            '--user-agent', self.get_random_user_agent(),
            '--cookies', self.create_cookie_file(),
            '--output', output_template,
            '--no-overwrites',
            '--continue',
        ]
        
        # Format-specific options
        if format_type == 'audio':
            cmd.extend([
                '--format', 'bestaudio',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '192K',
            ])
        elif format_type == 'best':
            cmd.extend([
                '--format', 'bestvideo+bestaudio/best',
                '--merge-output-format', 'mp4',
            ])
        else:  # default video
            cmd.extend([
                '--format', 'best',
                '--merge-output-format', 'mp4',
            ])
        
        # Content-specific options
        if content_type in ['playlist', 'channel'] and limit != 'all':
            cmd.extend(['--playlist-items', f'1-{limit}'])
            
        # Add verbose flag for debugging
        cmd.append('--verbose')
        
        # Add the URL last
        cmd.append(url)
        
        return cmd
        
    def download(self, url: str, content_type: str = None, format_type: str = 'best', limit: str = 'all') -> bool:
        """Download content from YouTube"""
        # Normalize URL and detect content type if not provided
        url = self.normalize_url(url)
        if not content_type:
            content_type = self.get_content_type(url)
        
        print(f"\n{Colors.BOLD}Starting download:{Colors.ENDC}")
        print(f"  {Colors.CYAN}URL:{Colors.ENDC} {url}")
        print(f"  {Colors.CYAN}Type:{Colors.ENDC} {content_type}")
        print(f"  {Colors.CYAN}Format:{Colors.ENDC} {self.supported_formats[format_type]['desc']}")
        
        if content_type in ['playlist', 'channel']:
            if limit == 'all':
                print(f"  {Colors.CYAN}Limit:{Colors.ENDC} All videos")
            else:
                print(f"  {Colors.CYAN}Limit:{Colors.ENDC} {limit} videos")
        
        # Build and execute download command
        cmd = self.build_download_command(url, content_type, format_type, limit)
        print(f"\n{Colors.YELLOW}Executing download command...{Colors.ENDC}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Process and display output with some filtering for better UI
            for line in process.stdout:
                line = line.strip()
                # Filter out verbose debug info but keep important progress info
                if '[debug]' in line.lower():
                    continue
                    
                if 'error' in line.lower():
                    print(f"{Colors.RED}{line}{Colors.ENDC}")
                elif any(marker in line for marker in ['download', 'progress', 'ETA', '%']):
                    # Clean up progress lines for better display
                    if '[download]' in line and '%' in line:
                        # Replace the line in place for a nicer progress display
                        sys.stdout.write(f"\r{Colors.GREEN}{line}{Colors.ENDC}")
                        sys.stdout.flush()
                        continue
                    print(f"{Colors.GREEN}{line}{Colors.ENDC}")
                else:
                    print(line)
            
            process.wait()
            print()  # Add a newline after the progress display
            
            if process.returncode == 0:
                print(f"{Colors.GREEN}{Colors.BOLD}✓ Download completed successfully!{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.RED}{Colors.BOLD}✗ Download failed with error code {process.returncode}.{Colors.ENDC}")
                # Try fallback method if first attempt failed
                return self.download_fallback(url, content_type, format_type, limit)
                
        except Exception as e:
            print(f"{Colors.RED}{Colors.BOLD}✗ An error occurred during download:{Colors.ENDC}")
            print(f"{Colors.RED}{str(e)}{Colors.ENDC}")
            # Try fallback method if first attempt failed
            return self.download_fallback(url, content_type, format_type, limit)
    
    def download_fallback(self, url: str, content_type: str, format_type: str, limit: str) -> bool:
        """Fallback method for downloading with simplified options"""
        print(f"\n{Colors.YELLOW}Trying fallback download method...{Colors.ENDC}")
        
        # Simplified command with fewer options to avoid potential issues
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if content_type == 'video':
            output_template = f"{self.downloads_folder}/%(title)s_fallback_{timestamp}.%(ext)s"
        elif content_type == 'playlist':
            output_template = f"{self.downloads_folder}/%(playlist_title)s/%(title)s_fallback_{timestamp}.%(ext)s"
        else:  # channel
            output_template = f"{self.downloads_folder}/%(uploader)s/%(title)s_fallback_{timestamp}.%(ext)s"
        
        cmd = [
            'yt-dlp',
            '--ignore-errors',
            '--format', 'best',  # Simplified format selection
            '--output', output_template,
            '--no-overwrites',
            '--geo-bypass',
        ]
        
        # Add audio extraction if needed
        if format_type == 'audio':
            cmd.extend(['--extract-audio', '--audio-format', 'mp3'])
        
        # Content-specific options (simplified)
        if content_type in ['playlist', 'channel'] and limit != 'all':
            cmd.extend(['--playlist-items', f'1-{limit}'])
            
        # Add the URL last
        cmd.append(url)
        
        try:
            print(f"{Colors.YELLOW}Executing fallback command...{Colors.ENDC}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            for line in process.stdout:
                line = line.strip()
                if 'error' in line.lower():
                    print(f"{Colors.RED}{line}{Colors.ENDC}")
                elif any(marker in line for marker in ['download', 'progress', 'ETA', '%']):
                    if '[download]' in line and '%' in line:
                        sys.stdout.write(f"\r{Colors.YELLOW}{line}{Colors.ENDC}")
                        sys.stdout.flush()
                        continue
                    print(f"{Colors.YELLOW}{line}{Colors.ENDC}")
                else:
                    print(line)
            
            process.wait()
            print()  # Add a newline after progress
            
            if process.returncode == 0:
                print(f"{Colors.GREEN}{Colors.BOLD}✓ Fallback download completed successfully!{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.RED}{Colors.BOLD}✗ Fallback download also failed.{Colors.ENDC}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}✗ Fallback download error: {str(e)}{Colors.ENDC}")
            print(f"{Colors.RED}✗ Unable to download the requested content.{Colors.ENDC}")
            return False
            
    def run(self):
        """Main program loop"""
        while True:
            print(f"\n{Colors.CYAN}{Colors.BOLD}==== {self.app_name} Main Menu ===={Colors.ENDC}")
            print(f"{Colors.BOLD}1. {Colors.BLUE}Download Video{Colors.ENDC}")
            print(f"{Colors.BOLD}2. {Colors.BLUE}Download Playlist{Colors.ENDC}")
            print(f"{Colors.BOLD}3. {Colors.BLUE}Download Channel{Colors.ENDC}")
            print(f"{Colors.BOLD}4. {Colors.BLUE}Auto-detect and Download{Colors.ENDC}")
            print(f"{Colors.BOLD}5. {Colors.RED}Exit{Colors.ENDC}")
            
            choice = input(f"\n{Colors.BOLD}Enter your choice (1-5): {Colors.ENDC}")
            
            if choice == '5':
                print(f"\n{Colors.YELLOW}Thanks for using {self.app_name}! Goodbye.{Colors.ENDC}")
                break
                
            if choice not in ['1', '2', '3', '4']:
                print(f"{Colors.RED}Invalid choice! Please select 1-5{Colors.ENDC}")
                continue

            # Get URL
            url = input(f"\n{Colors.BOLD}Enter YouTube URL: {Colors.ENDC}").strip()
            if not url:
                print(f"{Colors.RED}URL cannot be empty!{Colors.ENDC}")
                continue
                
            # Normalize URL
            url = self.normalize_url(url)
                
            # Determine content type based on selection or auto-detect
            content_types = {
                '1': 'video',
                '2': 'playlist',
                '3': 'channel',
                '4': self.get_content_type(url)
            }
            content_type = content_types[choice]
            
            if choice == '4':
                print(f"{Colors.YELLOW}Auto-detected content type: {content_type}{Colors.ENDC}")
            
            # Ask for format
            print(f"\n{Colors.BOLD}Available formats:{Colors.ENDC}")
            print(f"1. {Colors.BLUE}Best quality (video+audio){Colors.ENDC}")
            print(f"2. {Colors.BLUE}Audio only (mp3){Colors.ENDC}")
            
            format_choice = input(f"\n{Colors.BOLD}Select format (1-2) [{Colors.CYAN}1{Colors.ENDC}]: {Colors.ENDC}").strip()
            format_type = 'best' if format_choice != '2' else 'audio'
            
            # For playlists and channels, ask for video limit
            limit = 'all'
            if content_type in ['playlist', 'channel']:
                limit = self.ask_for_limit(content_type)
                
            # Download the content
            success = self.download(url, content_type, format_type, limit)
            
            if success:
                print(f"\n{Colors.GREEN}Content downloaded successfully to:{Colors.ENDC}")
                print(f"{Colors.GREEN}{self.downloads_folder.absolute()}{Colors.ENDC}")
            else:
                print(f"\n{Colors.RED}Download failed. Please check the URL and try again.{Colors.ENDC}")
                print(f"{Colors.YELLOW}Tips for successful downloads:{Colors.ENDC}")
                print(f"1. Make sure the URL is correct and accessible")
                print(f"2. For channels, try different URL formats (e.g., /channel/ID, @username)")
                print(f"3. Some videos may be region-restricted or age-restricted")
                print(f"4. Search for the video directly on YouTube and copy the URL")
            
            # Ask to continue
            cont = input(f"\n{Colors.BOLD}Download another? ({Colors.GREEN}y{Colors.ENDC}/{Colors.RED}n{Colors.ENDC}): {Colors.ENDC}").lower()
            if cont != 'y':
                print(f"\n{Colors.YELLOW}Thanks for using {self.app_name}! Goodbye.{Colors.ENDC}")
                break

def main():
    """Main entry point"""
    try:
        # Clear screen for better experience
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create and run the YTGrabber
        grabber = YTGrabber()
        grabber.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Program interrupted by user. Exiting...{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}An unexpected error occurred:{Colors.ENDC}")
        print(f"{Colors.RED}{str(e)}{Colors.ENDC}")
        print(f"\n{Colors.YELLOW}Please report this issue if it persists.{Colors.ENDC}")
    finally:
        # Clean up any temporary files
        try:
            if grabber.cookie_file and os.path.exists(grabber.cookie_file):
                os.remove(grabber.cookie_file)
        except:
            pass

if __name__ == "__main__":
    main()