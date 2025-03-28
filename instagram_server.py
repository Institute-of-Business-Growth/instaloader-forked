#!/usr/bin/env python3

import re
import json
import os
import signal
import sys
from flask import Flask, request, jsonify
import instagram_shortcode_to_url

app = Flask(__name__)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def extract_shortcode(instagram_url):
    """Extract shortcode from an Instagram URL"""
    # Match patterns like:
    # https://www.instagram.com/p/{shortcode}/
    # https://www.instagram.com/reel/{shortcode}/
    # https://www.instagram.com/tv/{shortcode}/
    pattern = r'instagram\.com/(?:p|reel|tv)/([^/?]+)'
    match = re.search(pattern, instagram_url)
    
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Could not extract shortcode from URL: {instagram_url}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "ok"}), 200

@app.route('/get_video_url', methods=['GET'])
def get_instagram_video_url():
    try:
        # Get Instagram URL from request body
        instagram_url = request.args.get('url')
        
        if not instagram_url:
            return jsonify({"error": "Missing Instagram URL. Use ?url=instagram_url"}), 400
        
        # Extract shortcode from the URL
        shortcode = extract_shortcode(instagram_url)
        
        # Get video URL using the existing function
        video_url = instagram_shortcode_to_url.get_video_url(shortcode)
        
        # Return the result
        return jsonify({
            "instagram_url": instagram_url,
            "shortcode": shortcode,
            "video_url": video_url
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/batch_video_urls', methods=['POST'])
def batch_instagram_video_urls():
    try:
        # Try to get JSON data, regardless of Content-Type
        try:
            # First try Flask's built-in JSON parser
            if request.is_json:
                request_data = request.get_json()
            else:
                # If Content-Type is not application/json, try to parse the raw data
                request_data = json.loads(request.data.decode('utf-8'))
        except Exception as e:
            return jsonify({
                "error": f"Failed to parse JSON: {str(e)}",
                "help": "Make sure the request body contains valid JSON"
            }), 400
        
        if not request_data or 'urls' not in request_data:
            return jsonify({"error": "Missing 'urls' field in JSON body"}), 400
            
        instagram_urls = request_data['urls']
        
        if not isinstance(instagram_urls, list):
            return jsonify({"error": "'urls' must be an array of Instagram URLs"}), 400
            
        results = []
        errors = []
        
        # Process each URL
        for url in instagram_urls:
            try:
                shortcode = extract_shortcode(url)
                video_url = instagram_shortcode_to_url.get_video_url(shortcode)
                
                results.append({
                    "instagram_url": url,
                    "shortcode": shortcode,
                    "video_url": video_url
                })
            except Exception as e:
                errors.append({
                    "instagram_url": url,
                    "error": str(e)
                })
        
        # Return both successful results and errors
        return jsonify({
            "results": results,
            "errors": errors,
            "total": len(instagram_urls),
            "success_count": len(results),
            "error_count": len(errors)
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # In production, don't use debug mode and bind to all interfaces
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 