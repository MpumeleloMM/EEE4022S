#!/bin/bash
# Prepare DASH files
# Mpumelelo Mthethwa
# 14 September 2018

clear

ffmpeg -i input.avi -s 160x90 -c:v libx264 -b:v 250k -g 90 -an input_video_160x90_250k.mp4
ffmpeg -i input.avi -s 320x180 -c:v libx264 -b:v 500k -g 90 -an input_video_320x180_500k.mp4
ffmpeg -i input.avi -s 640x360 -c:v libx264 -b:v 750k -g 90 -an input_video_640x360_750k.mp4
ffmpeg -i input.avi -s 640x360 -c:v libx264 -b:v 1000k -g 90 -an input_video_640x360_1000k.mp4
ffmpeg -i input.avi -s 1280x720 -c:v libx264 -b:v 1500k -g 90 -an input_video_1280x720_1500k.mp4
ffmpeg -i input.avi -c:a aac -b:a 128k -vn input_audio_128k.mp4

MP4Box -dash 5000 -rap -profile dashavc264:onDemand -mpd-title BBB -out manifest.mpd -frag 2000 input_audio_128k.mp4 input_video_160x90_250k.mp4 input_video_320x180_500k.mp4 input_video_640x360_750k.mp4 input_video_640x360_1000k.mp4 input_video_1280x720_1500k.mp4
