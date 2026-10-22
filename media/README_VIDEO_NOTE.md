# OptoTACH Media Assets & Video Guide

This directory contains visual and interactive demonstration assets for the OptoTACH project:

| File | Description | Purpose |
|------|-------------|---------|
| `optotach_demo.gif` | 6-second high-framerate looping demo animation | Embedded directly in the root `README.md` for instant playback |
| `optotach_demo.mp4` | Full 2m 50s bench demo video (H.264 / AAC, 1080p) | Complete operational demonstration with audio, optimized for web & GitHub (<50 MB) |
| `optotach_live_validation.jpg` | Side-by-side test capture vs calibrated Lutron DT-2236 tachometer | Visual proof of accuracy (2267 RPM vs 2280 RPM, <0.6% deviation) |
| `optotach_prototype.jpeg` | High-resolution photograph of the assembled physical board | Board layout and component fitment inspection |
| `optotach_display_powered.jpeg` | Photograph of illuminated 7-segment display digits | Visual inspection of LED display drive and clarity |
| `optotach_3d_render.png` | KiCad raytraced 3D render of the PCB | Top-down visual model comparison |
| `optotach_3d_angle.png` | Isometric perspective 3D render | Angled component profile view |
| `optotach_3d_top.png` | Top orthogonal 3D render | Silkscreen and pad alignment inspection |
| `optotach_3d_back.png` | Bottom copper & silkscreen 3D render | Power rails and ground pour inspection |
| `optotach_3d_model.glb` | 3D GLTF / GLB binary mesh model | Interactive 3D viewing in GitHub 3D viewer or CAD software |


### Note on GitHub File Size Limits & Raw Video

- GitHub imposes a **100 MB hard limit** on individual files tracked via standard Git, and recommends keeping files below **50 MB** to avoid warnings.
- The included `optotach_demo.mp4` has been encoded using H.264/AAC with fast-start flags to ensure it sits safely below GitHub's limits and can stream smoothly directly in web browsers.
- If you wish to host the original raw uncompressed iPhone video (`IMG_7708.MOV`, 243.6 MB), you can attach it to a **GitHub Release** tag or track it using **Git LFS** (`git lfs track "*.MOV"`).
