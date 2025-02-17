import asyncio
import json
import websockets
import random
from colorama import init, Fore, Style

import munch
import colorsys
import math
import fire

import logging
import os
level = os.environ.get("LOGLEVEL", logging.INFO)
try: level = int(level)
except: level = level.upper()
logging.basicConfig(level=level)
logger = logging.getLogger("bfire")

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
    
    def _get_post_color(self, ts):
        """Deterministically select a color based on post ID^W^W timestamp"""
        # Use hash of post ID to consistently select a color
        #return self.colors[hash(post_id) % len(self.colors)]
        return self.colors[int(ts) % len(self.colors)]

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

    def _hsv_termcolor(h, s, v):
        """[0,1] h, s, v -> 256 color terminal codes"""
        assert (h <= 1 and h >= 0), "h"
        assert (s <= 1 and s >= 0), "s"
        assert (v <= 1 and v >= 0), "v"
        rgb1 = colorsys.hsv_to_rgb(h, s, v) 
        rgb256 = list(int(i*255) for i in rgb1)
        colorstr = "\033[38;2;{};{};{}m".format(*rgb256)
        return colorstr

    
    async def connect_and_print(self, websocket_url, skips=[], onlys=[], count=None, cfilters={}, fkeeps=[], fdrops=[]):
        """Connect to websocket and print posts"""
        n=0
        try:
            async with websockets.connect(websocket_url) as websocket:
                print(f"Connected to {websocket_url}")
                while True:
                    try:
                        eventws = await websocket.recv()
                        
                        # Parse event 
                        try:
                            post = json.loads(eventws)
                            post = munch.munchify(post)
                        except json.JSONDecodeError:
                            post = "err:" + eventws

                        #try: post.type 
                        #except Exception as e:
                        #    logger.debug(f"no type on post object. {e=} {post.toJSON()=}")
                        #    continue
                        #try: post.record["$type"]
                        #except Exception as e:
                        #    logger.debug(f"no post.commit.$type key. {e=} {post.commit.toJSON()=}")
                        #    continue

                        # s/type/kind/g -- com -> commit
                        if onlys and post.kind not in onlys: continue
                        if post.kind in skips: continue
                        # type in ["com", "id", "acc"]  # [com]mit, [id]entity, [acc]ount, ..? [del]ete? or commit type
                        ts = post.time_us//10e3

                        # Select color based on post ID
                        #color = self._get_post_color(post.time_us//10e4)
                        hsv1 = [ (ts/4 % 255)/255, .8, .8]

                        # Generate a unique post ID
                        #post_id = str(hash(json.dumps(post)))
                        post_id = post.get("did", "r:"+str(random.random()))
                        
                        # Extract and print text
                        #text = self._extract_post_text(post)
                        try: 
                            #if post.type in ["com"]:
                            if post.kind in ["commit"]:
                                if cfilters.get("-") and any(map(lambda w: w in post.commit.type, cfilters.get("-"))): continue
                                if cfilters.get("+") and not any(map(lambda w: w in post.commit.type, cfilters.get("+"))): continue
                                if fdrops and any(map(lambda w: w in post.commit.record.text, fdrops)): continue
                                if fkeeps and not any(map(lambda w: w in post.commit.record.text, fkeeps)): continue

                            if post.commit.record.text:
                                text = post.commit.record.text 
                            else:
                                text = f"post.commit.record={post.commit.record.toJSON()}"
                            hsv1[2] = 1-min(1, math.log(len(text))/math.log(256*16))
                        except Exception as e:
                            text = str(post.toJSON())
                            hsv1[1] = .8
                            #hsv1[2] = 1-min(1, math.log(len(text))/math.log(256*16))  ## ~ 80
                            hsv1[2] = 60/255
                            hsv1[2] = 120/255
                            #color = "\033[38;2;%s;%s;%sm" % (64,64,64) # /255 ea
                                # Red\033[0m
                            #Fore.LIGHTWHITE_EX
                        if count is not None:
                            n+=1
                            if n > count: 
                                return
                        
                        
                        # 0 - 500    5 vs 30  vs 90
                        # [h,s,v]
                        #int(255 * math.log(len(text)))   
                        #rgb256[2] = min(255, len(text))
                        #rgb256[1] = max(8, 255-len(text))

                        #hsv1[1] = max(8, 255-len(text))/256
                        #hsv1[2] = (max(0, 255-len(text)))/256
                        ### hsv1[2] = 1-min(1, math.log(len(text))/math.log(256*16))
                        #(max(0, 255-len(text)))/256
                        

                        rgb1 = colorsys.hsv_to_rgb(*hsv1) 
                        rgb256 = list(int(i*255) for i in rgb1)
                        #logger.info(f"{rgb256=}")

                        color = "\033[38;2;{};{};{}m".format(*rgb256)
                        hsv1s = ":".join(f"{x:.1}" for x in hsv1)

                        ihsv1 = list(hsv1)
                        #ihsv1[1], ihsv1[2] *= .1, .4

                        ihsv1[2] *= .4  # v -- non- dark/black -ness
                        ihsv1[1] *= .1  # s -- color sat
                        ihsv1[2] = max(.3, ihsv1[2])
                        irgb1 = colorsys.hsv_to_rgb(*ihsv1) 
                        irgb256 = list(int(i*255) for i in irgb1)
                        infocolor = "\033[38;2;{};{};{}m".format(*irgb256)

                        # Print colored post
                        try: 
                            if post.type == "com":
                                print(f'{infocolor}{int(ts)}|type:{getattr(post,"type",None)}|{color}{text}{infocolor}|hsv:{hsv1s} type:{getattr(post,"type",None)} kind:{getattr(post,"kind",None)} {post.commit.type=} {post.commit.operation=}')
                            else:
                                ihsv1[1] *= .3
                                ihsv1[2] = 1
                                infocolor=_hsv_termcolor(*ihsv1)
                                print(f'{infocolor}{int(ts)}|type:{getattr(post,"type",None)}|{color}{text}{infocolor}|hsv:{hsv1s} type:{getattr(post,"type",None)} kind:{getattr(post,"kind",None)}')
                        except Exception as e:
                            print(f'{infocolor}{int(ts)}|{color}{text}{infocolor}|hsv:{hsv1s} type:{getattr(post,"type",None)} kind:{getattr(post,"kind",None)} -- no post commit')
                    
                    except Exception as e:
                        print(f"Error processing event: {e}")
                        raise e
        
        except Exception as e:
            print(f"Websocket connection error: {e}")

async def main(skips=[], onlys=[], count=None, cfilters={}, fkeeps=[], fdrops=[]):
    # Replace with actual Bluesky firehose websocket URL
    BLUESKY_FIREHOSE_WS = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
    
    printer = BlueskyFirehosePrinter()
    await printer.connect_and_print(BLUESKY_FIREHOSE_WS, skips=skips, onlys=onlys, count=count, cfilters=cfilters, fkeeps=fkeeps, fdrops=fdrops)

def cli_main(skips="", only="", cfilters="", filters="", count=None):
    """
    run the async func.
      --skip=[value][,value]*
      --only=[value][,value]*
      --filters=+include,-skip,+more,-nope
      --cfilters=  -- commit types:  delete, create, (reply?), (post?)
      --count=[n]  -- stop after
    """
    # Run the async main function
    skips = skips.split(",")
    onlys = only # onlys = list(only)# onlys = only.split(",")
    cfs = cfilters.split(",")
    cfilters = {"+": [f[1:] for f in cfs if f[:1] == "+"],
                "-": [f[1:] for f in cfs if f[:1] == "-"] }
    fs = filters.split(",")
    fkeeps = [f[1:] for f in fs if f[:1] == "+"]
    fdrops = [f[1:] for f in fs if f[:1] == "-"]
    try:
        asyncio.run(main(skips=skips, onlys=onlys, count=count, cfilters=cfilters, fkeeps=fkeeps, fdrops=fdrops))
    except KeyboardInterrupt as kb:
        print("done")

if __name__ == "__main__":
    fire.Fire(cli_main)

# Dependencies:
# pip install websockets colorama
# 
# Notes:
# 1. Replace BLUESKY_FIREHOSE_WS with actual websocket URL
# 2. The post extraction method (_extract_post_text) 
#    will likely need customization based on the 
#    actual Bluesky firehose JSON structure
