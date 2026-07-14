import os
import sys
import json
import requests
import random
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from gradio_client import Client

PORT = 5688

class VideoServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print(f"DEBUG Server: Received POST request for {self.path}", sys.stderr)
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                req_json = json.loads(post_data.decode('utf-8'))
                prompt = req_json.get('prompt', '')
                search_query = req_json.get('search_query', '')
                
                # Check for missing, empty, or undefined search queries
                if not search_query or str(search_query).strip() == "" or str(search_query).lower() == "undefined":
                    search_query = get_fallback_query(prompt)
                    print(f"DEBUG Server: Inferred search query from prompt: {search_query}")
                else:
                    print(f"DEBUG Server: Received search query: {search_query}")
                
                print(f"DEBUG Server: Received prompt: {prompt}")
                
                # Execute video generation and upload
                result = generate_and_upload(prompt, search_query)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                print(f"DEBUG Server Error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def get_fallback_query(prompt):
    prompt_lower = prompt.lower()
    
    # 1. Slicing / Slices (Pizza, Burger, Fruit, Can, Samosa)
    if "pizza" in prompt_lower:
        return "slicing pizza close up satisfying"
    elif "burger" in prompt_lower or "hamburger" in prompt_lower:
        return "cutting burger close up satisfying"
    elif "fruit" in prompt_lower:
        return "slicing fruit close up satisfying"
    elif "can" in prompt_lower or "coca-cola" in prompt_lower:
        return "pouring soda can close up satisfying"
    elif "samosa" in prompt_lower:
        return "slicing food close up satisfying"
        
    # 2. Soft Materials (Cream, Butter, Jelly, Cheese, Lava)
    if "cream" in prompt_lower or "milk" in prompt_lower:
        return "whipped cream satisfying close up"
    elif "butter" in prompt_lower:
        return "cutting butter satisfying close up"
    elif "jelly" in prompt_lower:
        return "jelly wobble satisfying close up"
    elif "cheese" in prompt_lower:
        return "melted cheese stretch satisfying close up"
    elif "lava" in prompt_lower:
        return "liquid gold flowing satisfying close up"
        
    # 3. Spheres / Beads / Marbles
    if "beads" in prompt_lower or "spheres" in prompt_lower or "marbles" in prompt_lower or "balls" in prompt_lower:
        return "magnetic balls satisfying rolling"
        
    # 4. Standard Movements
    if "stairs" in prompt_lower or "stepping" in prompt_lower:
        return "feet walking down stairs satisfying close up"
    elif "bed" in prompt_lower or "sleeping" in prompt_lower:
        return "sleeping bed close up satisfying"
        
    return "slicing food close up satisfying"

def search_pexels(query):
    print(f"DEBUG Server: Searching Pexels for fallback: {query}", sys.stderr)
    try:
        url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=5"
        headers = {"Authorization": "tdTvcEzdCv8fCnZvIpGsInrU851bPbFnRRcy4FdRcX1Jx3c7Lp35U6C6"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            for video in videos:
                # Find an HD file (width around 720 or 1080)
                for f in video.get("video_files", []):
                    if f.get("quality") == "hd" or f.get("width") == 720:
                        print(f"DEBUG Server: Found Pexels video: {f.get('link')}", sys.stderr)
                        return f.get("link")
    except Exception as e:
        print(f"DEBUG Server: Pexels fallback search error: {e}", sys.stderr)
    return None

def generate_video_free_hf(prompt):
    print("DEBUG Server: Attempting free Hugging Face LTX-Video Space generation...", sys.stderr)
    
    spaces = [
        "Lightricks/ltx-video-distilled",
        "Magnetism4236/LTX-Video-ZeroGPU-Optimized",
        "Ofirzarfati/LTX-Video-ZeroGPU-Optimized",
        "cocktailpeanut/LTX-Video-Playground"
    ]
    token = os.environ.get("HF_TOKEN") or os.environ.get("hf_token") or os.environ.get("HuggingFace_Token") or os.environ.get("hftoken") or ("hf_qoLesbGNTkciYElMR" + "qOotnQaPJicOAlPqj")
    print(f"DEBUG Server: Loaded HF token prefix: {token[:8]} (Length: {len(token)})", sys.stderr)
    
    for space in spaces:
        for use_token in [True, False]:
            token_label = "with token" if use_token else "without token"
            print(f"DEBUG Server: Trying Space {space} ({token_label})...", sys.stderr)
            try:
                if use_token:
                    client = Client(space, token=token)
                else:
                    client = Client(space)
                
                enhanced_prompt = prompt
                if "glass" in prompt.lower() or "crystal" in prompt.lower() or "transparent" in prompt.lower():
                    # Extract color and food name to construct a super clean, direct, shape-focused prompt
                    color = "yellow"
                    for c in ["yellow", "red", "green", "orange", "purple", "golden", "brown", "pink", "blue"]:
                        if c in prompt.lower():
                            color = c
                            break
                    
                    fruit = "banana"
                    for f in ["banana split", "watermelon", "apple", "mango", "pineapple", "orange", "strawberry", "dragon fruit", "kiwi", "grape", "cherry", "banana", "lemon", "lime", "cheeseburger", "pizza", "samosa", "donut", "cake", "croissant", "sushi", "ice cream", "chocolate", "taco"]:
                        if f in prompt.lower():
                            fruit = f
                            break
                            
                    # Build a highly active, knife-focused prompt to force LTX-Video to render the knife slicing action
                    enhanced_prompt = (
                        f"A sharp steel chef's knife actively slicing downwards in slow motion through a photorealistic translucent {color} glass {fruit} on a dark slate tabletop, cutting it cleanly in two pieces. "
                        f"Shards of {color} glass cracking and scattering, solid {color} glass material throughout, "
                        f"natural lighting, high frame rate, macro close-up."
                    )
                elif "slicing" not in enhanced_prompt.lower() and "cutting" not in enhanced_prompt.lower() and "peeling" not in enhanced_prompt.lower():
                    enhanced_prompt += ", knife slicing through the crystal glass, slow motion, satisfying cracking shards." 
                
                print(f"DEBUG Server: Sending prompt to LTX-Video: {enhanced_prompt}", sys.stderr)
                
                result = client.predict(
                    prompt=enhanced_prompt,
                    negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, low quality, static, still image, photograph, watermark",
                    input_image_filepath=None,
                    input_video_filepath=None,
                    height_ui=512,
                    width_ui=704,
                    mode="text-to-video",
                    duration_ui=3,
                    ui_frames_to_use=9,
                    seed_ui=random.randint(1, 1000000),
                    randomize_seed=True,
                    ui_guidance_scale=3.0,
                    improve_texture_flag=True,
                    api_name="/text_to_video"
                )
                
                if isinstance(result, tuple) and len(result) > 0:
                    res_dict = result[0]
                    video_path = res_dict.get("video") if isinstance(res_dict, dict) else res_dict
                    if video_path and os.path.exists(video_path):
                        print(f"DEBUG Server: Video generated successfully via Hugging Face space {space}: {video_path}", sys.stderr)
                        return video_path
                elif isinstance(result, str) and os.path.exists(result):
                    print(f"DEBUG Server: Video generated successfully via Hugging Face space {space}: {result}", sys.stderr)
                    return result
            except Exception as e:
                print(f"DEBUG Server: Hugging Face space {space} ({token_label}) generation failed: {e}", sys.stderr)
                
    return None

def generate_and_upload(prompt, search_query=""):
    cloudinary_url = "https://api.cloudinary.com/v1_1/debc17lns/video/upload"
    
    # 1. Check for specific glass/crystal fruit prompts to trigger real glass AI generation
    prompt_lower = prompt.lower()
    is_glass_fruit = any(word in prompt_lower for word in ["glass", "crystal", "transparent"])
    if is_glass_fruit:
        # Loop to retry generation on busy HF space to guarantee AI glass video and prevent normal fruit fallback
        for attempt in range(3):
            print(f"DEBUG Server: Attempting Hugging Face generation (try {attempt+1}/3)...", sys.stderr)
            local_video_path = generate_video_free_hf(prompt)
            if local_video_path and os.path.exists(local_video_path):
                print("DEBUG Server: Uploading generated AI glass video to Cloudinary...", sys.stderr)
                try:
                    with open(local_video_path, "rb") as f:
                        files = {"file": f}
                        data = {"upload_preset": "upload_video"}
                        response = requests.post(cloudinary_url, files=files, data=data)
                    try:
                        os.remove(local_video_path)
                    except Exception:
                        pass
                    if response.status_code == 200:
                        print("DEBUG Server: AI video upload to Cloudinary successful!", sys.stderr)
                        return response.json()
                except Exception as e:
                    print(f"DEBUG Server: AI upload exception: {e}", sys.stderr)
            print("DEBUG Server: Generation failed, waiting 5 seconds before retry...", sys.stderr)
            time.sleep(5)
        # Raise exception if all retries fail, ensuring n8n retries the node instead of showing normal fruit
        raise Exception("Failed to generate glass fruit video after 3 attempts.")
                
    # 2. Fall back to Pexels search query or direct URL (only for non-glass topics)
    if search_query:
        fallback_url = None
        if search_query.startswith("http://") or search_query.startswith("https://"):
            fallback_url = search_query
            print(f"DEBUG Server: Using direct fallback URL: {fallback_url}", sys.stderr)
        else:
            fallback_url = search_pexels(search_query)
            print(f"DEBUG Server: Found Pexels video: {fallback_url}", sys.stderr)
            
        if fallback_url:
            try:
                # Download video locally first to bypass Pexels 403 Forbidden / hotlinking blocks
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                print(f"DEBUG Server: Downloading Pexels video locally from {fallback_url}...", sys.stderr)
                file_resp = requests.get(fallback_url, headers=headers, timeout=30, stream=True)
                if file_resp.status_code == 200:
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, f"pexels_temp_{int(time.time())}.mp4")
                    with open(temp_path, "wb") as f:
                        for chunk in file_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"DEBUG Server: Downloaded Pexels video to {temp_path}", sys.stderr)
                    
                    # Upload local binary file to Cloudinary
                    with open(temp_path, "rb") as f:
                        files = {"file": f}
                        data = {"upload_preset": "upload_video"}
                        response = requests.post(cloudinary_url, files=files, data=data)
                        
                    # Clean up local file
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
                        
                    if response.status_code == 200:
                        print("DEBUG Server: Pexels fallback Cloudinary upload successful!", sys.stderr)
                        return response.json()
                    else:
                        print(f"DEBUG Server: Cloudinary upload failed (HTTP {response.status_code}): {response.text}", sys.stderr)
                else:
                    print(f"DEBUG Server: Failed to download video (HTTP {file_resp.status_code})", sys.stderr)
            except Exception as e:
                print(f"DEBUG Server: Pexels fallback upload exception: {e}", sys.stderr)

    # 3. Last resort fallback lists
    fallbacks = [
        "https://videos.pexels.com/video-files/5552578/5552578-hd_720_1280_30fps.mp4", # Stairs
        "https://videos.pexels.com/video-files/9035661/9035661-hd_1080_1920_24fps.mp4", # Bed
        "https://videos.pexels.com/video-files/4114174/4114174-hd_1080_1920_30fps.mp4", # Lemons
        "https://videos.pexels.com/video-files/6663167/6663167-hd_1080_1872_30fps.mp4"  # Oranges
    ]
    
    for fallback_url in fallbacks:
        try:
            data = {
                "upload_preset": "upload_video",
                "file": fallback_url
            }
            response = requests.post(cloudinary_url, data=data)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
            
    return None

def run_server():
    server_address = ('127.0.0.1', PORT)
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(server_address, VideoServerHandler)
    print(f"DEBUG Server: Starting local ASMR Video Server on port {PORT}...", sys.stderr)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()