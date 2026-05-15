from image_gen import ImageGenerator
from content_gen import ContentGenerator
from social_manager import SocialManager
from dotenv import load_dotenv
import os

def run_automation(topic, provider="pollinations"):
    load_dotenv()

    # Initialize components
    content_gen = ContentGenerator(provider=provider)
    image_gen = ImageGenerator(provider="free")
    social_mgr = SocialManager()

    print(f"--- Starting Automation for topic: {topic} (Mode: {provider}) ---")

    # 1. Generate Idea & Plan
    print("Generating plan...")
    plan = content_gen.generate_reel_plan(topic)
    print(f"Plan: {plan}")

    # 2. Generate Visuals
    print("Generating visual...")
    image_url = image_gen.generate_image(plan['visual'])
    print(f"Image URL: {image_url}")

    # 3. Social Media Posting (Simulation)
    print("Posting to social media...")
    ig_status = social_mgr.post_to_instagram(image_url, plan['script'])
    tw_status = social_mgr.post_to_twitter(image_url, plan['script'])

    return {
        "image_url": image_url,
        "plan": plan,
        "instagram": ig_status,
        "twitter": tw_status
    }

if __name__ == "__main__":
    test_topic = "Minecraft Parkour Brainrot"
    results = run_automation(test_topic)
    print("\nFinal Results:")
    for key, value in results.items():
        print(f"{key}: {value}")
