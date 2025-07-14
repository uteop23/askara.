import os
import shutil
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from yt_dlp import YoutubeDL

# Setup Flask App
app = Flask(__name__)
CORS(app)

# Folder untuk menyimpan video sementara di lingkungan hosting
TEMP_DIR = "/tmp/askara_clips"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.route('/')
def index():
    return "Server Askara Clipper sedang berjalan!"

@app.route('/process-video', methods=['POST'])
def process_video():
    data = request.get_json()
    yt_url = data.get('url')

    if not yt_url:
        return jsonify({"error": "URL tidak ditemukan"}), 400

    try:
        ydl_opts = {
            'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
            'outtmpl': os.path.join(TEMP_DIR, '%(id)s.%(ext)s'),
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(yt_url, download=True)
            video_id = info_dict.get("id", "default_id")
            video_title = info_dict.get('title', 'Judul Tidak Ditemukan')
            original_filepath = os.path.join(TEMP_DIR, f"{video_id}.mp4")

        if not os.path.exists(original_filepath):
             return jsonify({"error": "Gagal mengunduh video dari YouTube."}), 500

        generated_clips = []
        clip_titles = [
            "Momen Motivasi Terbaik", "Poin Kunci yang Mengubah Hidup",
            "Penjelasan Mendalam (Singkat)", "Saat Paling Lucu"
        ]
        
        for i, title in enumerate(clip_titles):
            clip_filename = f"{video_id}_clip_{i+1}.mp4"
            clip_path = os.path.join(TEMP_DIR, clip_filename)
            shutil.copy(original_filepath, clip_path)
            
            generated_clips.append({
                "title": title,
                "filename": clip_filename
            })

        return jsonify({
            "original_title": video_title,
            "clips": generated_clips
        })

    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/clips/<filename>')
def get_clip(filename):
    return send_from_directory(TEMP_DIR, filename)
