"""Service for fetching YouTube video information."""
import os
import re
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class YouTubeVideoInfo:
    video_id: str
    title: str
    duration: int  # in seconds
    channel: str
    thumbnail_url: str


def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration format (PT#H#M#S) to seconds."""
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration_str)
    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


def get_video_info(video_id: str) -> Optional[YouTubeVideoInfo]:
    """Fetch video information from YouTube Data API."""
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        return None

    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'snippet,contentDetails',
        'id': video_id,
        'key': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('items'):
            return None

        item = data['items'][0]
        snippet = item.get('snippet', {})
        content_details = item.get('contentDetails', {})

        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = (
            thumbnails.get('maxres', {}).get('url') or
            thumbnails.get('high', {}).get('url') or
            thumbnails.get('medium', {}).get('url') or
            thumbnails.get('default', {}).get('url') or
            ''
        )

        return YouTubeVideoInfo(
            video_id=video_id,
            title=snippet.get('title', ''),
            duration=parse_duration(content_details.get('duration', 'PT0S')),
            channel=snippet.get('channelTitle', ''),
            thumbnail_url=thumbnail_url
        )
    except Exception as e:
        print(f"Error fetching YouTube video info: {e}")
        return None
