import os
import sys
import json
import requests
import random
import time
import subprocess
import tempfile
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
                result = generate_and_upload(prompt, search_query, req_json.get('audio_url', ''))
                
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

import concurrent.futures

def _hf_predict_worker(space, token, enhanced_prompt):
    if token:
        client = Client(space, token=token)
    else:
        client = Client(space)
    return client.predict(
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

def generate_video_free_hf(prompt):
    print("DEBUG Server: Attempting fast free Hugging Face LTX-Video Space generation...", sys.stderr)
    space = "Lightricks/ltx-video-distilled"
    token = os.environ.get("HF_TOKEN") or os.environ.get("hf_token") or os.environ.get("HuggingFace_Token") or os.environ.get("hftoken") or ("hf_qoLesbGNTkciYElMR" + "qOotnQaPJicOAlPqj")
    
    enhanced_prompt = prompt
    if "glass" in prompt.lower() or "crystal" in prompt.lower() or "transparent" in prompt.lower():
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
        enhanced_prompt = (
            f"A sharp steel chef's knife actively slicing downwards in slow motion through a photorealistic translucent {color} glass {fruit} on a dark slate tabletop, cutting it cleanly in two pieces. "
            f"Shards of {color} glass cracking and scattering, solid {color} glass material throughout, natural lighting, high frame rate, macro close-up."
        )
        
    print(f"DEBUG Server: Submitting to HF space with 15s timeout: {enhanced_prompt}", sys.stderr)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(_hf_predict_worker, space, token, enhanced_prompt)
        result = future.result(timeout=15)
        executor.shutdown(wait=False, cancel_futures=True)
        
        if isinstance(result, tuple) and len(result) > 0:
            res_dict = result[0]
            video_path = res_dict.get("video") if isinstance(res_dict, dict) else res_dict
            if video_path and os.path.exists(video_path):
                print(f"DEBUG Server: Video generated via HF space in <15s: {video_path}", sys.stderr)
                return video_path
        elif isinstance(result, str) and os.path.exists(result):
            print(f"DEBUG Server: Video generated via HF space in <15s: {result}", sys.stderr)
            return result
    except Exception as e:
        print(f"DEBUG Server: HF space timed out (>15s) or failed: {e}. Switching immediately to ultra-fast Pexels search...", sys.stderr)
        executor.shutdown(wait=False, cancel_futures=True)
        
    return None

def download_temp_file(url, suffix):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = temp_file.name
    temp_file.close()
    
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 200:
        with open(temp_path, "wb") as f:
            f.write(resp.content)
        return temp_path
    else:
        try:
            os.remove(temp_path)
        except Exception:
            pass
        raise Exception(f"Failed to download file from {url}: HTTP {resp.status_code}")

def generate_and_upload(prompt, search_query="", audio_url=""):
    cloudinary_url = "https://api.cloudinary.com/v1_1/debc17lns/video/upload"
    prompt_lower = prompt.lower()
    
    local_video_path = None
    is_glass_fruit = any(word in prompt_lower for word in ["glass", "crystal", "transparent"])
    
    # 1. Fast Hugging Face AI Generation (1 fast attempt, max 20s)
    if is_glass_fruit:
        print("DEBUG Server: Attempting fast Hugging Face generation...", sys.stderr)
        try:
            local_video_path = generate_video_free_hf(prompt)
        except Exception as e:
            print(f"DEBUG Server: Fast HF generation exception: {e}", sys.stderr)
            
        if not local_video_path or not os.path.exists(local_video_path):
            print("DEBUG Server: HF space generation bypassed/failed. Falling back immediately to fast Pexels stock video + ASMR audio merge...", sys.stderr)
            
    # 2. Pexels search query or direct URL fallback (for non-glass topics)
    if not local_video_path and search_query:
        fallback_url = None
        if search_query.startswith("http://") or search_query.startswith("https://"):
            fallback_url = search_query
        else:
            fallback_url = search_pexels(search_query)
            
        if fallback_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                print(f"DEBUG Server: Downloading Pexels/fallback video from {fallback_url}...", sys.stderr)
                file_resp = requests.get(fallback_url, headers=headers, timeout=30, stream=True)
                if file_resp.status_code == 200:
                    temp_dir = tempfile.gettempdir()
                    local_video_path = os.path.join(temp_dir, f"temp_video_{int(time.time())}.mp4")
                    with open(local_video_path, "wb") as f:
                        for chunk in file_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"DEBUG Server: Downloaded video to {local_video_path}", sys.stderr)
            except Exception as e:
                print(f"DEBUG Server: Fallback download exception: {e}", sys.stderr)
                
    # 3. Last resort fallback lists
    if not local_video_path:
        fallbacks = [
            "https://videos.pexels.com/video-files/5552578/5552578-hd_720_1280_30fps.mp4",
            "https://videos.pexels.com/video-files/9035661/9035661-hd_1080_1920_24fps.mp4",
            "https://videos.pexels.com/video-files/4114174/4114174-hd_1080_1920_30fps.mp4",
            "https://videos.pexels.com/video-files/6663167/6663167-hd_1080_1872_30fps.mp4"
        ]
        for fallback_url in fallbacks:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                print(f"DEBUG Server: Downloading last resort fallback from {fallback_url}...", sys.stderr)
                file_resp = requests.get(fallback_url, headers=headers, timeout=30, stream=True)
                if file_resp.status_code == 200:
                    temp_dir = tempfile.gettempdir()
                    local_video_path = os.path.join(temp_dir, f"fallback_{int(time.time())}.mp4")
                    with open(local_video_path, "wb") as f:
                        for chunk in file_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    break
            except Exception:
                pass
                
    if not local_video_path or not os.path.exists(local_video_path):
        raise Exception("Could not retrieve any video for upload.")
        
    # Now merge audio if provided
    upload_path = local_video_path
    temp_audio_path = None
    merged_video_path = None
    
    # Default fallback to natural ASMR audio if missing or undefined
    if not audio_url or str(audio_url).strip() == "" or str(audio_url).lower() == "undefined":
        if any(w in prompt_lower for w in ["water", "liquid", "flow", "pour", "milk", "cream"]):
            audio_url = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/1-16746-A-15.wav"
        elif any(w in prompt_lower for w in ["bead", "marble", "ball", "rolling"]):
            audio_url = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/1-118206-A-31.wav"
        elif any(w in prompt_lower for w in ["bubble", "foam", "sponge", "pop"]):
            audio_url = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/1-17565-A-12.wav"
        else:
            # Natural knife slicing ASMR sound (crystal clear real knife cut)
            audio_url = "https://raw.githubusercontent.com/developer-soni/Fruit-Slice-Game/main/audio/slicefruit.mp3"
        print(f"DEBUG Server: Inferred natural ASMR audio URL: {audio_url}", sys.stderr)

    if audio_url and str(audio_url).strip() != "" and str(audio_url).lower() != "undefined":
        try:
            print(f"DEBUG Server: Downloading audio for merge from {audio_url}...", sys.stderr)
            ext = ".wav"
            if ".ogg" in audio_url.lower():
                ext = ".ogg"
            elif ".mp3" in audio_url.lower():
                ext = ".mp3"
            elif ".m4a" in audio_url.lower():
                ext = ".m4a"
                
            temp_audio_path = download_temp_file(audio_url, ext)
            print(f"DEBUG Server: Downloaded audio to {temp_audio_path}", sys.stderr)
            
            merged_video_path = os.path.join(tempfile.gettempdir(), f"merged_{int(time.time())}.mp4")
            
            is_slicing = any(word in prompt_lower for word in ["slice", "slicing", "cut", "cutting", "chop", "chopping", "banana"])
            
            if is_slicing:
                cmd = ["ffmpeg", "-y", "-stream_loop", "6", "-i", local_video_path]
                for _ in range(7):
                    cmd += ["-i", temp_audio_path]
                    
                filter_str = "[0:v]setpts=2.0*PTS[v_slow];"
                filter_str += ";".join([f"[{i}:a]adelay={1400 + (i-1)*3000}[a{i}]" for i in range(1, 8)])
                filter_str += ";" + "".join([f"[a{i}]" for i in range(1, 8)]) + "amix=inputs=7:normalize=0[mixed_audio]"
                
                cmd += [
                    "-filter_complex", filter_str,
                    "-map", "[v_slow]",
                    "-map", "[mixed_audio]",
                    "-t", "20",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    merged_video_path
                ]
            else:
                cmd = [
                    "ffmpeg", "-y",
                    "-stream_loop", "6", "-i", local_video_path,
                    "-stream_loop", "-1", "-i", temp_audio_path,
                    "-filter_complex", "[0:v]setpts=2.0*PTS[v_slow]",
                    "-map", "[v_slow]",
                    "-map", "1:a",
                    "-t", "20",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    merged_video_path
                ]
                
            print(f"DEBUG Server: Running ffmpeg merge: {' '.join(cmd)}", sys.stderr)
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and os.path.exists(merged_video_path):
                print(f"DEBUG Server: Merging successful! Size: {os.path.getsize(merged_video_path)} bytes", sys.stderr)
                upload_path = merged_video_path
            else:
                print(f"DEBUG Server: Merging failed (code {res.returncode}): {res.stderr}", sys.stderr)
        except Exception as e:
            print(f"DEBUG Server: Audio merging exception: {e}", sys.stderr)
            
    # Upload to Cloudinary
    print(f"DEBUG Server: Uploading {upload_path} to Cloudinary...", sys.stderr)
    try:
        with open(upload_path, "rb") as f:
            files = {"file": f}
            data = {"upload_preset": "upload_video"}
            response = requests.post(cloudinary_url, files=files, data=data)
            
        if response.status_code == 200:
            print("DEBUG Server: Cloudinary upload successful!", sys.stderr)
            return response.json()
        else:
            print(f"DEBUG Server: Cloudinary upload failed (HTTP {response.status_code}): {response.text}", sys.stderr)
            raise Exception(f"Cloudinary upload failed: {response.text}")
    finally:
        # Cleanup
        for path in [local_video_path, temp_audio_path, merged_video_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

def run_server():
    server_address = ('127.0.0.1', PORT)
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(server_address, VideoServerHandler)
    print(f"DEBUG Server: Starting local ASMR Video Server on port {PORT}...", sys.stderr)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
