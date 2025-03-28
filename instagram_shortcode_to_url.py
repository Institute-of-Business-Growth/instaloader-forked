#!/usr/bin/env python3

import sys
import os
import argparse

# Import directly from Instaloader
try:
    import instaloader
except ImportError:
    print("Error: Instaloader not installed. Please install it with: pip install instaloader")
    sys.exit(1)

def get_video_url(shortcode):
    """Get direct video URL from Instagram reel/post shortcode using Instaloader"""
    
    # Create an instance of Instaloader
    L = instaloader.Instaloader()
    
    try:
        # Get post from shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Check if it's a video
        if not post.is_video:
            raise ValueError(f"Post {shortcode} is not a video")
        
        # Get video URL directly from the post
        return post.video_url
        
    except instaloader.exceptions.InstaloaderException as e:
        raise Exception(f"Instaloader error: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Extract direct video URL from Instagram post/reel shortcode")
    parser.add_argument("shortcode", help="Instagram post/reel shortcode")
    args = parser.parse_args()
    
    # Remove leading '-' if present (like in Instaloader syntax)
    shortcode = args.shortcode
    if shortcode.startswith('-'):
        shortcode = shortcode[1:]
    
    try:
        video_url = get_video_url(shortcode)
        print(f"Direct video URL for {shortcode}:")
        print(video_url)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 