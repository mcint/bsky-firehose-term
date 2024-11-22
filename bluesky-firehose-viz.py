import asyncio
import json
import websockets
import curses
import random
import colorsys
import time
from collections import deque
import logging
FORMAT = '%(asctime)s:%(loglevel)s:%(name)s %(message)s'
#'%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
logging.basicConfig(level=logging.DEBUG, filename="bviz.log", format=FORMAT)
logger = logging.getLogger("bviz")

class BlueskyFirehoseVisualizer:
    def __init__(self, stdscr, websocket_url):
        logger.info("init-start")
        self.stdscr = stdscr
        self.websocket_url = websocket_url
        
        # Initialize color pairs
        curses.start_color()
        curses.use_default_colors()
        
        # Set up screen
        curses.curs_set(0)
        #self.stdscr.clear()
        
        # Track posts with their display details
        self.posts = {}
        self.max_posts = 1000  # Limit to prevent memory growth
        
        # Generate color palette
        self.color_palette = self._generate_color_palette()
        logger.info("init-end")
        
    def _generate_color_palette(self, num_colors=256):
        """Generate a diverse color palette."""
        colors = []
        for i in range(num_colors):
            # Use HSV color space to generate visually distinct colors
            hue = (i / num_colors) % 1.0
            saturation = 0.7 + (random.random() * 0.3)  # 70-100% saturation
            value = 0.7 + (random.random() * 0.3)      # 70-100% brightness
            
            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            
            # Scale RGB to curses color range (0-1000)
            r, g, b = [int(x * 1000) for x in rgb]
            
            # Initialize color pair
            try:
                color_index = len(colors) + 1  # Start from 1
                curses.init_color(color_index, r, g, b)
                curses.init_pair(color_index, color_index, -1)
                colors.append(color_index)
            except Exception:
                # If we run out of color pairs, wrap around
                color_index = (len(colors) % 256) + 1
                colors.append(color_index)
        
        return colors
    
    def _display_post(self, post_id, text):
        """Display a post with a unique color, fading out over time."""
        # Assign a unique color
        color_index = self.color_palette[hash(post_id) % len(self.color_palette)]
        
        # Get screen dimensions
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Trim text to fit screen width
        text = text[:max_x-1]
        
        # Track post details
        if post_id not in self.posts:
            # Remove oldest post if we've reached max
            if len(self.posts) >= self.max_posts:
                oldest_id = min(self.posts, key=lambda k: self.posts[k]['timestamp'])
                del self.posts[oldest_id]
            
            # Find a free vertical position
            used_y = set(post['y'] for post in self.posts.values())
            y = next(i for i in range(max_y) if i not in used_y)
            
            self.posts[post_id] = {
                'text': text,
                'color': color_index,
                'y': y,
                'timestamp': time.time(),
                'fade_count': 0
            }
        
        # Render posts
        for pid, post_info in list(self.posts.items()):
            # Calculate fade effect
            age = time.time() - post_info['timestamp']
            fade_speed = 0.5  # Adjust for desired fade speed
            
            if age > fade_speed * post_info['fade_count']:
                try:
                    # Gradually reduce text intensity
                    intensity = max(0, 1 - (post_info['fade_count'] / 10))
                    color = curses.color_pair(post_info['color'])
                    
                    # Render text at constant horizontal position
                    self.stdscr.addstr(
                        post_info['y'], 
                        post_info['fade_count'], 
                        post_info['text'][:max_x-1], 
                        color
                    )
                    
                    post_info['fade_count'] += 1
                except curses.error:
                    # If we can't write (e.g., screen boundaries), remove post
                    del self.posts[pid]
        
        # Refresh display
        self.stdscr.refresh()
    
    async def connect_and_visualize(self):
        """Connect to Bluesky firehose and visualize posts."""
        logger.info("connect_and_visualize")
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                while True:
                    message = await websocket.recv()
                    post = json.loads(message)
                    
                    # Extract meaningful text (adjust based on actual Bluesky JSON structure)
                    post_id = post.get('did', "r:"+str(random.random()))
                    record = post.get('record', '---(no record in post)---')
                    text = record.get('text', '---(no text in post)---')
                    
                    # Display the post
                    logger.info(f"{post_id=} {text=}")
                    self._display_post(post_id, text)
                    
        except Exception as e:
            self.stdscr.addstr(0, 0, f"Error: {str(e)}")
            self.stdscr.refresh()
    
    def run(self):
        """Run the visualizer."""
        asyncio.run(self.connect_and_visualize())

def main(stdscr):
    logger.info("main()")
    # Replace with actual Bluesky firehose websocket URL
    BLUESKY_FIREHOSE_WS = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
    
    visualizer = BlueskyFirehoseVisualizer(stdscr, BLUESKY_FIREHOSE_WS)
    visualizer.run()

if __name__ == "__main__":
    # Wrap main in curses wrapper to handle terminal setup/teardown
    try: 
        curses.wrapper(main)
    except Exception as e:
        logger.error(e)

# Dependencies (install with pip):
# websockets
# 
# Note: You'll need to replace the websocket URL with the actual 
# Bluesky firehose websocket endpoint when available.
