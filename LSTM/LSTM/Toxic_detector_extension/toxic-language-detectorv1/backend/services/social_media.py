# services/social_media.py
import requests
from typing import Dict, Any, List
import os

class FacebookAPI:
    def __init__(self):
        self.api_version = "v18.0"
        self.api_url = f"https://graph.facebook.com/{self.api_version}"
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    
    def get_post_comments(self, post_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get comments for a Facebook post
        
        Args:
            post_id (str): The Facebook post ID
            limit (int): Maximum number of comments to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of comments
        """
        endpoint = f"{self.api_url}/{post_id}/comments"
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "fields": "id,message,created_time,from"
        }
        
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if "data" in data:
            return data["data"]
        
        return []
    
    def get_page_posts(self, page_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get posts from a Facebook page
        
        Args:
            page_id (str): The Facebook page ID
            limit (int): Maximum number of posts to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of posts
        """
        endpoint = f"{self.api_url}/{page_id}/posts"
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "fields": "id,message,created_time,comments.limit(0).summary(true)"
        }
        
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if "data" in data:
            return data["data"]
        
        return []


class TwitterAPI:
    def __init__(self):
        self.api_url = "https://api.twitter.com/2"
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
    
    def get_tweet_replies(self, tweet_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get replies to a tweet
        
        Args:
            tweet_id (str): The Tweet ID
            max_results (int): Maximum number of results to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of replies
        """
        # Get conversation ID for the tweet
        tweet_endpoint = f"{self.api_url}/tweets/{tweet_id}"
        params = {
            "tweet.fields": "conversation_id"
        }
        
        response = requests.get(tweet_endpoint, headers=self.headers, params=params)
        tweet_data = response.json()
        
        if "data" not in tweet_data:
            return []
        
        conversation_id = tweet_data["data"].get("conversation_id", tweet_id)
        
        # Get replies in the conversation
        search_endpoint = f"{self.api_url}/tweets/search/recent"
        params = {
            "query": f"conversation_id:{conversation_id}",
            "max_results": max_results,
            "tweet.fields": "created_at,author_id,in_reply_to_user_id"
        }
        
        response = requests.get(search_endpoint, headers=self.headers, params=params)
        data = response.json()
        
        if "data" in data:
            return data["data"]
        
        return []
    
    def get_user_timeline(self, user_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get tweets from a user's timeline
        
        Args:
            user_id (str): The Twitter user ID
            max_results (int): Maximum number of tweets to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of tweets
        """
        endpoint = f"{self.api_url}/users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics"
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        data = response.json()
        
        if "data" in data:
            return data["data"]
        
        return []


class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.api_url = "https://www.googleapis.com/youtube/v3"
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get comments for a YouTube video
        
        Args:
            video_id (str): The YouTube video ID
            max_results (int): Maximum number of comments to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of comments
        """
        endpoint = f"{self.api_url}/commentThreads"
        params = {
            "key": self.api_key,
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(max_results, 100)  # YouTube API limit is 100 per request
        }
        
        comments = []
        next_page_token = None
        
        while len(comments) < max_results:
            if next_page_token:
                params["pageToken"] = next_page_token
            
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if "items" not in data:
                break
            
            for item in data["items"]:
                if "snippet" in item and "topLevelComment" in item["snippet"]:
                    comment = {
                        "id": item["id"],
                        "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                        "author": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                        "published_at": item["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
                        "like_count": item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
                    }
                    comments.append(comment)
                    
                    if len(comments) >= max_results:
                        break
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        
        return comments
    
    def search_videos(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of videos to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of videos
        """
        endpoint = f"{self.api_url}/search"
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50)  # YouTube API limit is 50 per request
        }
        
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        if "items" in data:
            videos = []
            for item in data["items"]:
                video = {
                    "id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"],
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
                }
                videos.append(video)
            return videos
        
        return []
