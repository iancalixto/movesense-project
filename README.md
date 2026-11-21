# MoveSense

Pedestrian behavior analysis from video using detection, tracking, and trajectory classification.

**Course:** Integrated Application Project WS 2026 — FH Kufstein, Topic 06

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/11lxMp9CyB44uPqqXapZDF2UeYs6PLxsP)
[![CI/CD Pipeline](https://img.shields.io/badge/GitLab%20CI-Passed-success)](https://gitlab.web.hok.ac.at/konraddaniel/movesense)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-310%20MB%20(multi--stage)-blue)](Dockerfile)

## 🚀 Cloud GPU Benchmark & Live Interactive Demos

Run the official Stanford JackRabbot (JRDB) & MOT20 extreme crowd benchmark with hardware acceleration (NVIDIA T4 GPU) directly in Google Colab:

👉 **[Click here to open the Interactive Notebook](https://colab.research.google.com/drive/11lxMp9CyB44uPqqXapZDF2UeYs6PLxsP)**

* **Stanford JRDB Evaluation:** Real-world cafe, pedestrian walkway, and street crossing benchmarks.
* **MOT20 Crowd Tracking:** Extreme density pedestrian tracking with live Heads-Up Display (HUD).
* **Kinematic Posture Verification:** Instantaneous fall/laydown posture ($w/h \ge 1.05$) and scale-normalized kinematics ($bl/s$).

## Quick Start
```bash
uv venv --python 3.11
source .venv/bin/activate
make install
make test
```
