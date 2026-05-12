from image_gen import ImageGenerator
from content_gen import ContentGenerator
from social_manager import SocialManager
from dotenv import load_dotenv
import os

def run_automation(prompt, provider="free"):
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    # Initialize components
    image_gen = ImageGenerator(api_key=api_key, provider=provider)
    content_gen = ContentGenerator(api_key=api_key, provider=provider)
    social_mgr = SocialManager()

    print(f"--- Starting Automation for prompt: {prompt} (Mode: {provider}) ---")

    # 1. Generate Image
    print("Generating image...")
    image_url = image_gen.generate_image(prompt)
    print(f"Image URL: {image_url}")

    # 2. Generate Content
    print("Generating caption...")
    caption = content_gen.generate_caption(prompt)
    print(f"Caption: {caption}")

    # 3. Social Media Posting (Simulation)
    print("Posting to social media...")
    ig_status = social_mgr.post_to_instagram(image_url, caption)
    tw_status = social_mgr.post_to_twitter(image_url, caption)

    return {
        "image_url": image_url,
        "caption": caption,
        "instagram": ig_status,
        "twitter": tw_status
    }

if __name__ == "__main__":
    test_prompt = "An AI influencer drinking coffee in a futuristic cafe"
    # Default to free for CLI test too
    results = run_automation(test_prompt, provider="free")
    print("\nFinal Results:")
    for key, value in results.items():
        print(f"{key}: {value}")
