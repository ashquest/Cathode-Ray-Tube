import json
import time
import requests
import yt_dlp
import os
import random
import re

# --- CONFIGURATION ---
KEY = "6X93>._R`a]<W&UVrZ+fuX1Q"
LOCAL_FILE = 'lists/list.json'
REMOTE_URL = 'https://ytch.tv/lists/list.json'

def ytch_codec_fixed(data, key=KEY, mode="encode"):
    xor_mask = 0
    for char in key: xor_mask ^= ord(char)
    xor_mask &= 0xFF 
    if mode == "decode":
        bytes_list = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]
        return "".join([chr(b ^ xor_mask) for b in bytes_list])
    else:
        return "".join([f"{(ord(c) ^ xor_mask) & 0xFF:02x}" for c in data])

def get_videos_from_source(source):
    # Fix for channel homepages: force the /videos tab
    if "youtube.com/@" in source and "/videos" not in source:
        source = source.rstrip('/') + "/videos"

    is_url = re.match(r'^https?://', source)
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'clean_infojson': True,
    }
    
    query = source if is_url else f"ytsearch20:{source}"
    video_entries = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            if not result: return []
            entries = result.get('entries', [result])

            for entry in entries:
                if not entry: continue
                duration = int(entry.get('duration') or 0)
                if duration < 60: continue # Filter Shorts
                if entry.get('playable_in_embed') is False: continue
                if entry.get('age_limit', 0) >= 18: continue

                video_entries.append({
                    "id": entry.get('id'),
                    "duration": duration,
                    "ratio": round(entry.get('width', 16) / entry.get('height', 9), 3) if entry.get('height') else 1.778
                })
        return video_entries
    except Exception as e:
        print(f"    [!] Error processing {source}: {e}")
        return []

def sync_and_update():
    # Load Local Data first to preserve list_of_urls
    if not os.path.exists(LOCAL_FILE):
        local_data = {}
    else:
        with open(LOCAL_FILE, 'r') as f:
            try: local_data = json.load(f)
            except: local_data = {}

    # 1. Sync Remote & Merge
    print(f"[*] Fetching remote channels from {REMOTE_URL}...")
    try:
        response = requests.get(f"{REMOTE_URL}?t={int(time.time())}")
        response.raise_for_status()
        remote_data = response.json()
        
        for ch_id, ch_content in remote_data.items():
            if ch_id in local_data and "list_of_urls" in local_data[ch_id]:
                # PRESERVE local list_of_urls but take remote metadata (name, etc)
                print(f"  [+] Merging remote channel {ch_id} with local custom URLs")
                # Update only the remote video data into local, keeping our tags
                local_data[ch_id]["remote_videos"] = ch_content.get("videos", {})
                local_data[ch_id]["name"] = ch_content.get("name", local_data[ch_id].get("name"))
            else:
                # Standard overwrite/add for channels without custom lists
                local_data[ch_id] = ch_content
    except Exception as e:
        print(f"Remote sync failed: {e}")

    # 2. Sequential Processing
    start_epoch = int(time.time())

    for channel_id in list(local_data.keys()):
        channel = local_data[channel_id]
        
        if "list_of_urls" in channel and isinstance(channel["list_of_urls"], list):
            print(f"\n📺 Processing Channel ID {channel_id}: {channel.get('name')}")
            
            all_gathered_videos = []

            # A. Add Remote Videos if they were fetched
            if "remote_videos" in channel:
                print(f"  -> Extracting {len(channel['remote_videos'])} videos from Remote ytch.tv source")
                for r_idx in channel["remote_videos"]:
                    v = channel["remote_videos"][r_idx]
                    all_gathered_videos.append({
                        "id": ytch_codec_fixed(v["id"], mode="decode"),
                        "duration": v["duration"],
                        "ratio": v.get("r", 1.778)
                    })
                del channel["remote_videos"] # Clean up temporary tag

            # B. Add Local Custom URL Videos
            for source in channel["list_of_urls"]:
                print(f"  -> Gathering from local source: {source}")
                found = get_videos_from_source(source)
                print(f"     Found {len(found)} valid videos.")
                all_gathered_videos.extend(found)
            
            # C. Shuffle and Re-index
            if all_gathered_videos:
                random.shuffle(all_gathered_videos)
                
                new_videos = {}
                current_play_at = start_epoch
                
                for idx, meta in enumerate(all_gathered_videos):
                    encoded_id = ytch_codec_fixed(meta["id"], mode="encode")
                    new_videos[str(idx)] = {
                        "id": encoded_id,
                        "playAt": current_play_at,
                        "duration": meta["duration"],
                        "r": meta["ratio"]
                    }
                    current_play_at += meta["duration"]
                
                channel["videos"] = new_videos
                print(f"  [+] SUCCESS: Mixed & updated {len(new_videos)} videos.")

    with open(LOCAL_FILE, 'w') as f:
        json.dump(local_data, f, indent=4)
    
    print(f"\n✅ Updated {LOCAL_FILE}")

if __name__ == "__main__":
    sync_and_update()