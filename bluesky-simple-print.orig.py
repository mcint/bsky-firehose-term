import asyncio
import json
import websockets
import random
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class BlueskyFirehosePrinter:
    def __init__(self):
        # Preset list of vibrant colors
        self.colors = [
            Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, 
            Fore.MAGENTA, Fore.CYAN, Fore.WHITE,
            Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, 
            Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX, 
            Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX
        ]
    
    def _get_post_color(self, post_id):
        """Deterministically select a color based on post ID"""
        # Use hash of post ID to consistently select a color
        return self.colors[hash(post_id) % len(self.colors)]
    
    def _extract_post_text(self, post):
        """
        Extract meaningful text from a post.
        Modify this method based on the actual Bluesky post JSON structure.
        """
        # Example of potential extraction, will need to be adapted
        if isinstance(post, dict):
            # Try different possible text fields
            text = post.get('text') or \
                   post.get('content', {}).get('text') or \
                   str(post)
            return text[:200]  # Limit text length
        return str(post)
    
    async def connect_and_print(self, websocket_url):
        """Connect to websocket and print posts"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                print(f"Connected to {websocket_url}")
                while True:
                    try:
                        message = await websocket.recv()
                        
                        # Parse message 
                        try:
                            post = json.loads(message)
                        except json.JSONDecodeError:
                            post = message
                        
                        # Generate a unique post ID
                        post_id = str(hash(json.dumps(post)))
                        
                        # Extract and print text
                        text = self._extract_post_text(post)
                        
                        # Select color based on post ID
                        color = self._get_post_color(post_id)
                        
                        # Print colored post
                        print(f"{color}{text}")
                    
                    except Exception as e:
                        print(f"Error processing message: {e}")
        
        except Exception as e:
            print(f"Websocket connection error: {e}")

async def main():
    # Replace with actual Bluesky firehose websocket URL
    BLUESKY_FIREHOSE_WS = "ws://example.com/bluesky-firehose"
    
    printer = BlueskyFirehosePrinter()
    await printer.connect_and_print(BLUESKY_FIREHOSE_WS)

def cli_main():
    # Run the async main function
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()

# Dependencies:
# pip install websockets colorama
# 
# Notes:
# 1. Replace BLUESKY_FIREHOSE_WS with actual websocket URL
# 2. The post extraction method (_extract_post_text) 
#    will likely need customization based on the 
#    actual Bluesky firehose JSON structure
