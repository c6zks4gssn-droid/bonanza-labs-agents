"""Bonanza Avatar — HeyGen-powered AI news anchor video generation."""

from __future__ import annotations
import os
import time
import httpx
from typing import Optional
from pydantic import BaseModel, Field


class Avatar(BaseModel):
    """Available HeyGen avatar."""
    avatar_id: str
    name: str
    gender: str = ""
    preview_url: str = ""
    type: str = "photo"  # photo, video, digital_twin


class Voice(BaseModel):
    """Available HeyGen voice."""
    voice_id: str
    name: str
    gender: str = ""
    language: str = ""
    preview_url: str = ""


class AvatarVideoRequest(BaseModel):
    """Request to generate an avatar video."""
    script: str
    avatar_id: str = ""  # Default: first available avatar
    voice_id: str = ""   # Default: first available voice
    title: str = ""
    resolution: str = "1080p"
    aspect_ratio: str = "16:9"
    background_color: str = "#0a0a0f"
    expressiveness: str = "high"
    speed: float = 1.0


class AvatarVideoResult(BaseModel):
    """Result of an avatar video generation."""
    video_id: str
    status: str
    video_url: str = ""
    thumbnail_url: str = ""
    error: str = ""


# ─── Pre-configured news anchors ───

NEWS_ANCHORS = {
    "female_pro": {
        "name": "Alexis (Professional Female)",
        "avatar_id": "",  # Will be populated after listing avatars
        "voice_id": "",
        "style": "professional",
    },
    "male_pro": {
        "name": "Marcus (Professional Male)",
        "avatar_id": "",
        "voice_id": "",
        "style": "professional",
    },
    "female_casual": {
        "name": "Sam (Casual Female)",
        "avatar_id": "",
        "voice_id": "",
        "style": "casual",
    },
    "male_casual": {
        "name": "Jordan (Casual Male)",
        "avatar_id": "",
        "voice_id": "",
        "style": "casual",
    },
}


class HeyGenClient:
    """HeyGen API client for avatar video generation."""

    BASE_URL = "https://api.heygen.com"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY", "")
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY required. Get yours at https://app.heygen.com/settings?nav=API")

    @property
    def headers(self):
        return {"x-api-key": self.api_key, "Content-Type": "application/json"}

    def list_avatars(self, limit: int = 20) -> list[Avatar]:
        """List available avatars."""
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{self.BASE_URL}/v2/avatars", headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            avatars = []
            for a in data.get("data", {}).get("avatars", [])[:limit]:
                avatars.append(Avatar(
                    avatar_id=a.get("avatar_id", ""),
                    name=a.get("avatar_name", "Unnamed"),
                    gender=a.get("gender", ""),
                    preview_url=a.get("preview_image_url", ""),
                    type=a.get("type", "photo"),
                ))
            return avatars

    def list_voices(self, language: str = "en") -> list[Voice]:
        """List available voices, optionally filtered by language."""
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{self.BASE_URL}/v2/voices", headers=self.headers, params={"language": language})
            resp.raise_for_status()
            data = resp.json()
            voices = []
            for v in data.get("data", {}).get("voices", []):
                voices.append(Voice(
                    voice_id=v.get("voice_id", ""),
                    name=v.get("display_name", v.get("name", "Unnamed")),
                    gender=v.get("gender", ""),
                    language=v.get("language", ""),
                    preview_url=v.get("preview_audio", ""),
                ))
            return voices

    def create_video(self, request: AvatarVideoRequest) -> AvatarVideoResult:
        """Create an avatar video. Returns video_id for polling."""
        # If no avatar/voice specified, use first available
        avatar_id = request.avatar_id
        voice_id = request.voice_id

        if not avatar_id or not voice_id:
            avatars = self.list_avatars()
            voices = self.list_voices()
            if not avatars:
                return AvatarVideoResult(video_id="", status="error", error="No avatars available")
            if not voices:
                return AvatarVideoResult(video_id="", status="error", error="No voices available")
            if not avatar_id:
                avatar_id = avatars[0].avatar_id
            if not voice_id:
                voice_id = voices[0].voice_id

        payload = {
            "avatar_id": avatar_id,
            "voice_id": voice_id,
            "script": request.script,
            "title": request.title or "Bonanza Labs News",
            "resolution": request.resolution,
            "aspect_ratio": request.aspect_ratio,
            "expressiveness": request.expressiveness,
            "voice_settings": {
                "speed": request.speed,
            },
            "background": {
                "type": "color",
                "value": request.background_color,
            },
        }

        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{self.BASE_URL}/v2/videos", headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return AvatarVideoResult(
                video_id=data.get("video_id", ""),
                status=data.get("status", "waiting"),
            )

    def get_video_status(self, video_id: str) -> AvatarVideoResult:
        """Check video generation status."""
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{self.BASE_URL}/v2/videos/{video_id}", headers=self.headers)
            resp.raise_for_status()
            data = resp.json().get("data", {})
            return AvatarVideoResult(
                video_id=video_id,
                status=data.get("status", "unknown"),
                video_url=data.get("video_url", ""),
                thumbnail_url=data.get("thumbnail_url", ""),
                error=data.get("error", ""),
            )

    def wait_for_video(self, video_id: str, timeout: int = 300, interval: int = 10) -> AvatarVideoResult:
        """Wait for video generation to complete."""
        start = time.time()
        while time.time() - start < timeout:
            result = self.get_video_status(video_id)
            if result.status in ("completed", "complete", "done"):
                return result
            if result.status in ("failed", "error"):
                return result
            time.sleep(interval)
        return AvatarVideoResult(video_id=video_id, status="timeout", error="Video generation timed out")

    def create_news_video(self, script: str, anchor: str = "female_pro",
                          aspect_ratio: str = "16:9", background: str = "#0a0a0f") -> AvatarVideoResult:
        """Create a news-style video with a pre-configured anchor."""
        request = AvatarVideoRequest(
            script=script,
            title=f"Bonanza Labs News",
            aspect_ratio=aspect_ratio,
            background_color=background,
            expressiveness="high",
            speed=1.0,
        )
        return self.create_video(request)