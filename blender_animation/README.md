# 5-Second Blender Animation

- `animation.mp4` — rendered video: 5.00 s, 640x360, H.264, 24 fps (120 frames)
- `animation_script.py` — the Python (bpy) script that builds and renders the scene

Scene: bouncing red ball (squash & stretch), tumbling blue cube, spinning gold torus,
hopping green cone, orbiting camera, sun + area light, rendered with EEVEE.

Re-render headless:

    blender -b -noaudio --python animation_script.py

(edit `scene.render.filepath` inside the script to change the output path)
