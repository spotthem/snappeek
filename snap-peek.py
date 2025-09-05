#!/usr/bin/env python3
import json
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
}


def print_banner():
    print(r"""
   _____                           _____                  _    
  / ____|                         |  __ \                | |   
 | (___    _ __     __ _   _ __   | |__) |   ___    ___  | | __
  \___ \  | '_ \   / _` | | '_ \  |  ___/   / _ \  / _ \ | |/ /
  ____) | | | | | | (_| | | |_) | | |      |  __/ |  __/ |   < 
 |_____/  |_| |_|  \__,_| | .__/  |_|       \___|  \___| |_|\_\
                          | |                                  
                          |_|                                  
    """)


def parse_snapchat_data(username):
    r = requests.get(
        f"https://www.snapchat.com/@{username}", headers=headers, timeout=10
    )

    response_text = r.text

    soup = BeautifulSoup(response_text, "html.parser")

    profile_data = {}

    script_tag = soup.find("script", id="__NEXT_DATA__")

    if script_tag:
        json_data = json.loads(script_tag.string)

        props = json_data.get("props", {}).get("pageProps", {})

        user_case = props.get("userProfile", {}).get("$case")

        if not user_case:
            return profile_data

        user_profile = props.get("userProfile", {}).get(user_case)

        if user_profile:
            if user_profile.get("displayName"):
                profile_data["name"] = user_profile["displayName"]

            if user_profile.get("title"):
                profile_data["name"] = user_profile["title"]

            if user_profile.get("bio"):
                profile_data["bio"] = user_profile["bio"]

            if user_profile.get("websiteUrl"):
                profile_data["website"] = user_profile["websiteUrl"]

            if user_profile.get("address"):
                profile_data["location"] = user_profile["address"]

            if user_profile.get("creationTimestampMs", {}).get("value"):
                profile_data["created_at"] = datetime.fromtimestamp(
                    int(user_profile["creationTimestampMs"]["value"]) / 1000.0
                ).strftime("%Y-%m-%d %H:%M:%S")

            if user_profile.get("lastUpdateTimestampMs", {}).get("value"):
                profile_data["last_updated"] = datetime.fromtimestamp(
                    int(user_profile["lastUpdateTimestampMs"]["value"]) / 1000.0
                ).strftime("%Y-%m-%d %H:%M:%S")

            image_urls = []

            if user_profile.get("profilePictureUrl"):
                image_urls.append(user_profile["profilePictureUrl"])

            if user_profile.get("bitmoji3d"):
                if user_profile["bitmoji3d"].get("avatarImage"):
                    if user_profile["bitmoji3d"]["avatarImage"].get("url"):
                        image_urls.append(
                            user_profile["bitmoji3d"]["avatarImage"]["url"]
                        )

            if user_profile.get("snapcodeImageUrl"):
                image_urls.append(user_profile["snapcodeImageUrl"])

            if user_profile.get("squareHeroImageUrl"):
                image_urls.append(user_profile["squareHeroImageUrl"])

            if image_urls:
                profile_data["image_urls"] = image_urls

    return profile_data


def main():
    print_banner()
    if len(sys.argv) < 2:
        print("Usage: python snap-peek.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    print(f"Username provided: {username}")

    profile_data = parse_snapchat_data(username)

    if profile_data:
        print("Extracted Snapchat Profile Data:\n")

        for key, value in profile_data.items():
            if key == "image_urls":
                print("Image URLs:")
                for url in value:
                    print(f"  - {url}")
            else:
                print(f"{key.title().replace('_', ' ')}: {value}")

        print()
    else:
        print("No data found for the given username.")


if __name__ == "__main__":
    main()
