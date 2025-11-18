"""
YouTube Transcript Scraper
Extracts transcripts from YouTube playlists for RAG system
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import json
import time
from typing import List, Dict, Any
import re
from googleapiclient.discovery import build
import os
import dotenv

class YouTubeScraper:
    def __init__(self, api_key: str = None):
        """
        Initialize YouTube scraper
        
        Args:
            api_key: YouTube Data API v3 key (optional, needed for playlist parsing)
        """
        self.api_key = api_key
        if api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from URL"""
        match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else None
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_playlist_videos(self, playlist_id: str) -> List[Dict[str, str]]:
        """
        Get all video IDs and titles from a playlist using YouTube API
        Requires API key
        """
        if not self.api_key:
            print("Error: YouTube API key required for playlist parsing")
            return []
        
        videos = []
        next_page_token = None
        
        while True:
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                
                videos.append({
                    'video_id': video_id,
                    'title': title,
                    'channel': channel,
                    'url': f'https://www.youtube.com/watch?v={video_id}'
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return videos
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> Dict[str, Any]:
        """
        Get transcript for a video
        
        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])
        
        Returns:
            Dict with transcript data or None if unavailable
        """
        if languages is None:
            languages = ['en']
        
        try:
            # Correct API call - it's a list method that returns transcript objects
            transcript_list = YouTubeTranscriptApi.get_transcripts([video_id], languages=languages)
            transcript_data = transcript_list[0][video_id]
            
            return {
                'success': True,
                'video_id': video_id,
                'language': languages[0],
                'is_generated': True,
                'segments': transcript_data
            }
            
        except TranscriptsDisabled:
            return {'success': False, 'error': 'Transcripts disabled for this video'}
        except NoTranscriptFound:
            return {'success': False, 'error': 'No transcript found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def format_transcript_text(self, segments: List[Dict]) -> str:
        """Convert transcript segments to readable text"""
        return ' '.join([segment['text'] for segment in segments])
    
    def create_rag_document(self, video_info: Dict, transcript_data: Dict) -> Dict[str, Any]:
        """
        Create RAG-formatted document from video transcript
        
        Args:
            video_info: Video metadata (title, channel, etc.)
            transcript_data: Transcript segments
        
        Returns:
            Formatted document for RAG processing
        """
        full_text = self.format_transcript_text(transcript_data['segments'])
        
        return {
            'title': video_info['title'],
            'url': video_info['url'],
            'category': 'youtube_strategy',
            'sections': [{
                'heading': 'Transcript',
                'content': [full_text]
            }],
            'metadata': {
                'video_id': video_info['video_id'],
                'channel': video_info['channel'],
                'language': transcript_data['language'],
                'is_auto_generated': transcript_data['is_generated'],
                'total_segments': len(transcript_data['segments'])
            },
            'source': 'youtube'
        }
    
    def scrape_playlist(self, playlist_url: str, delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Scrape all videos from a playlist
        
        Args:
            playlist_url: YouTube playlist URL
            delay: Delay between requests (seconds)
        
        Returns:
            List of RAG-formatted documents
        """
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print(f"Error: Could not extract playlist ID from {playlist_url}")
            return []
        
        print(f"\nFetching videos from playlist: {playlist_id}")
        videos = self.get_playlist_videos(playlist_id)
        print(f"Found {len(videos)} videos")
        
        documents = []
        
        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}] {video['title']}")
            print(f"  Video ID: {video['video_id']}")
            
            # Get transcript
            transcript_data = self.get_transcript(video['video_id'])
            
            if transcript_data['success']:
                print(f"  ✓ Transcript: {len(transcript_data['segments'])} segments")
                print(f"    Language: {transcript_data['language']}")
                print(f"    Type: {'Auto-generated' if transcript_data['is_generated'] else 'Manual'}")
                
                # Create RAG document
                doc = self.create_rag_document(video, transcript_data)
                documents.append(doc)
            else:
                print(f"  ✗ Failed: {transcript_data['error']}")
            
            time.sleep(delay)
        
        return documents
    
    def scrape_multiple_playlists(self, playlist_urls: List[str], delay: float = 1.0) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape multiple playlists"""
        all_documents = []
        
        for i, url in enumerate(playlist_urls, 1):
            print(f"\n{'='*60}")
            print(f"PLAYLIST {i}/{len(playlist_urls)}")
            print(f"{'='*60}")
            
            docs = self.scrape_playlist(url, delay)
            all_documents.extend(docs)
            
            print(f"\n✓ Scraped {len(docs)} videos from playlist {i}")
        
        return {'youtube_strategy': all_documents}
    
    def save_to_json(self, data: Dict, filename: str):
        """Save scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved to: {filename}")


def main():
    """Main scraping function"""

    # Get API key from environment or user input
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("YouTube API Key not found in environment.")
        print("Get one from: https://console.cloud.google.com/apis/credentials")
        api_key = input("Enter your YouTube API key: ").strip()
    
    scraper = YouTubeScraper(api_key=api_key)
    
    # Your playlists
    playlists = [
        'https://www.youtube.com/playlist?list=PLUmau0-sP9xFw-Z5DFakzS-kZ4-orHl28',
        'https://www.youtube.com/playlist?list=PLUmau0-sP9xFMKZz6eMH15mrf3h-fhFCQ'
    ]
    
    # Scrape all playlists
    all_data = scraper.scrape_multiple_playlists(playlists, delay=1.0)
    
    # Save results
    scraper.save_to_json(all_data, 'data/raw/youtube/youtube_transcripts.json')
    
    # Print summary
    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    total = sum(len(docs) for docs in all_data.values())
    print(f"Total videos transcribed: {total}")
    for category, docs in all_data.items():
        print(f"  {category}: {len(docs)} videos")


if __name__ == "__main__":
    main()