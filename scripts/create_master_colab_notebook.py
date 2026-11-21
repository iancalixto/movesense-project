"""Script to generate the updated MoveSense Master Colab Notebook.

Integrates 50+ video testing across environments and duration categories,
fixes all previous errors, and provides interactive HTML5 video playback.
"""

import json
from pathlib import Path

def create_notebook():
    cells = []

    # --- Title Markdown ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 🚶‍♂️ MoveSense · Unified Multi-Dataset Benchmark, ML Training & 50-Video Lab\n",
            "**FH Kufstein Tirol — MSc Data Science & Intelligent Analytics**  \n",
            "*Topic 06: Pedestrian Tracking & Behaviour Analytics*  \n",
            "**Authors:** Ian Calixto & MoveSense Team  \n",
            "\n",
            "---\n",
            "\n",
            "### 🎯 Overview of This Cloud Laboratory\n",
            "This unified Google Colab environment integrates the entire MoveSense end-to-end framework:\n",
            "1. **Multi-Dataset Hub:** Ingestion and evaluation across **Stanford JackRabbot (JRDB-Act)**, **MOT17**, **MOT20**, and **Controlled Synthetic** datasets.\n",
            "2. **Physical Kinematics:** Bounding box body-length normalization ($v/h$), Savitzky-Golay trajectory smoothing, and confinement radius metrics.\n",
            "3. **Supervised ML vs. RuleEngine:** Transparent physical RuleEngine baseline evaluated against trained Random Forest / Gradient Boosting classifiers.\n",
            "4. **🎬 50-Video Multi-Environment & Multi-Duration Benchmark Suite:**\n",
            "   - **Duration Categories:** `< 10s` (13 videos), `10-20s` (13 videos), `20-30s` (12 videos), and `> 30s` (12 videos).\n",
            "   - **Diverse Environments:** University Campus, Coffee Places & Cafeterias, Street Crossings, People Running, Transit Hubs, and Fall/Emergency Anomalies.\n",
            "5. **High-Definition Video Rendering Engine:** Universal H.264/MP4 encoding with color-coded bounding boxes and action badges.\n",
            "6. **Interactive In-Colab HTML5 Video Player:** Instant inline playback with dropdown video selector and real-time telemetry.\n"
        ]
    })

    # --- Section 1: GPU Hardware ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Cloud Infrastructure & Hardware Setup\n",
            "Verify cloud GPU accelerator allocation (NVIDIA T4 / A100 / V100) and CUDA runtime."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Check hardware accelerator allocation\n",
            "!nvidia-smi\n"
        ]
    })

    # --- Section 2: Environment Setup ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Environment Setup & Dependency Installation\n",
            "Clone repository, configure system packages, and install dependencies using standard high-speed pip."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Clone MoveSense repository (or pull latest branch updates)\n",
            "!git clone https://github.com/iancalixto/movesense-project.git || (cd movesense-project && git pull)\n",
            "%cd movesense-project\n",
            "\n",
            "# Set PYTHONPATH for all bash subcommands\n",
            "%env PYTHONPATH=src:.\n",
            "\n",
            "# Install core dependencies directly with pip\n",
            "!pip install -q -e . ultralytics opencv-python-headless matplotlib seaborn huggingface_hub pandas tqdm scikit-learn ipywidgets\n",
            "!apt-get -qq install -y ffmpeg\n",
            "\n",
            "# Ensure current notebook kernel has src/ and . in sys.path\n",
            "import sys, pathlib\n",
            "for p in [str(pathlib.Path('src').resolve()), str(pathlib.Path('.').resolve())]:\n",
            "    if p not in sys.path:\n",
            "        sys.path.insert(0, p)\n",
            "\n",
            "# Verify installation\n",
            "import torch\n",
            "import ultralytics\n",
            "import cv2\n",
            "import movesense\n",
            "print(f\"✅ PyTorch version: {torch.__version__} (CUDA: {torch.cuda.is_available()})\")\n",
            "print(f\"✅ Ultralytics YOLO: {ultralytics.__version__}\")\n",
            "print(f\"✅ OpenCV: {cv2.__version__}\")\n",
            "print(f\"✅ MoveSense package installed from: {movesense.__file__}\")\n"
        ]
    })

    # --- Section 3: Multi-Dataset Hub ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Multi-Dataset Ingestion Hub\n",
            "Initialize storage directories and ingest benchmark datasets:\n",
            "- **Synthetic Ground-Truth Generator:** Controlled baseline for deterministic verification.\n",
            "- **MOT17:** Dynamic pedestrian tracking with camera movement (MOT17-09-FRCNN).\n",
            "- **MOT20:** Ultra-dense crowded pedestrian sequence (MOT20-01).\n",
            "- **Stanford JackRabbot (JRDB-Act):** Panoramic social robotics action classification."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pathlib\n",
            "\n",
            "# Ensure directory hierarchy exists\n",
            "for p in [\"data/MOT17/train\", \"data/MOT20/train\", \"data/JRDB_full\", \"data/synthetic\", \"data/video_benchmarks\", \"results\", \"outputs\"]:\n",
            "    pathlib.Path(p).mkdir(parents=True, exist_ok=True)\n",
            "print(\"✅ Storage directory hierarchy initialized.\")\n"
        ]
    })

    # --- Section 3.1: Synthetic Generation (FIXED) ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3.1 Synthetic Dataset: Generation, Tracking & Feature Extraction\n",
            "Generate ground-truth, run the SimpleTracker to create `tracks.txt`, and extract physical kinematic features into `trajectory_features.csv`."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 1: Generate synthetic ground truth\n",
            "!python scripts/generate_synthetic.py\n",
            "# Step 2: Track synthetic detections with SimpleTracker (produces data/synthetic/tracks.txt)\n",
            "!python scripts/run_tracker.py\n",
            "# Step 3: Extract kinematic features (produces data/synthetic/trajectory_features.csv)\n",
            "!python scripts/extract_features.py\n",
            "!ls -lh data/synthetic/\n"
        ]
    })

    # --- Section 3.2: MOT17 & MOT20 Ingestion ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3.2 MOT17 & MOT20 Sequence Ingestion\n",
            "Download benchmark sequences from Hugging Face mirrors with automated verification."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Ingest MOT17-09-FRCNN sequence\n",
            "!python scripts/download_mot17.py\n",
            "# Ingest MOT20-01 sequence\n",
            "!python scripts/download_mot20.py\n",
            "!ls -lh data/MOT17/train/ data/MOT20/train/\n"
        ]
    })

    # --- Section 3.3: Stanford JRDB ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3.3 Stanford JRDB (JackRabbot) Social Robotics Dataset\n",
            "Verify presence of `data/sample_jrdb.json` with self-healing fallback."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import json, pathlib\n",
            "jrdb_file = pathlib.Path(\"data/sample_jrdb.json\")\n",
            "if not jrdb_file.exists():\n",
            "    print(\"Writing sample_jrdb.json fallback...\")\n",
            "    sample_data = {\n",
            "        \"sequence_name\": \"stanford_campus_sample\",\n",
            "        \"fps\": 30.0,\n",
            "        \"description\": \"Stanford JackRabbot (JRDB-Act) action benchmark sample.\",\n",
            "        \"labels\": {\n",
            "            \"000001.jpg\": [\n",
            "                {\"box\": [100.0, 200.0, 45.0, 130.0], \"label_id\": \"pedestrian:1\", \"action\": \"walking\"},\n",
            "                {\"box\": [300.0, 400.0, 120.0, 80.0], \"label_id\": \"pedestrian:2\", \"action\": \"kneeling\"},\n",
            "                {\"box\": [500.0, 250.0, 40.0, 135.0], \"label_id\": \"pedestrian:3\", \"action\": \"standing\"},\n",
            "                {\"box\": [150.0, 100.0, 50.0, 125.0], \"label_id\": \"pedestrian:4\", \"action\": \"running\"},\n",
            "                {\"box\": [600.0, 300.0, 42.0, 128.0], \"label_id\": \"pedestrian:5\", \"action\": \"loitering\"}\n",
            "            ],\n",
            "            \"000030.jpg\": [\n",
            "                {\"box\": [170.0, 200.0, 45.0, 130.0], \"label_id\": \"pedestrian:1\", \"action\": \"walking\"},\n",
            "                {\"box\": [300.0, 400.0, 120.0, 80.0], \"label_id\": \"pedestrian:2\", \"action\": \"kneeling\"},\n",
            "                {\"box\": [500.0, 250.0, 40.0, 135.0], \"label_id\": \"pedestrian:3\", \"action\": \"standing\"},\n",
            "                {\"box\": [300.0, 100.0, 50.0, 125.0], \"label_id\": \"pedestrian:4\", \"action\": \"running\"},\n",
            "                {\"box\": [598.0, 298.0, 42.0, 128.0], \"label_id\": \"pedestrian:5\", \"action\": \"loitering\"}\n",
            "            ]\n",
            "        }\n",
            "    }\n",
            "    jrdb_file.write_text(json.dumps(sample_data, indent=2))\n",
            "print(f\"✅ Stanford JRDB annotations ready at {jrdb_file} ({jrdb_file.stat().st_size} bytes).\")\n"
        ]
    })

    # --- Section 4: Machine Learning Model Training ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Behaviour Classification: Machine Learning Model Training\n",
            "Train supervised classifiers (Random Forest, Gradient Boosting) using kinematic features (normalized velocity, acceleration, confinement radius, aspect ratio)."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Train supervised Random Forest BehaviourClassifier on extracted features\n",
            "!python scripts/train_classifier.py\n"
        ]
    })

    # --- Section 5: Academic Evaluation ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Academic Evaluation: RuleEngine vs. Trained Classifiers\n",
            "Evaluate RuleEngine against Stanford JRDB action annotations and MOT17 sequences."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Evaluate on Stanford JackRabbot\n",
            "!python scripts/evaluate_jrdb_benchmark.py\n",
            "# Evaluate size-normalized velocity rules on MOT17-09\n",
            "!python scripts/evaluate_behaviour_rules.py\n"
        ]
    })

    # --- Section 6: Scientific Visualizations ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.1 Scientific Performance Metrics & Visualizations\n",
            "Display confusion matrix and prediction distributions."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from IPython.display import display\n",
            "\n",
            "jrdb_res_path = pathlib.Path(\"results/jrdb_action_benchmark.csv\")\n",
            "if jrdb_res_path.exists():\n",
            "    df_jrdb = pd.read_csv(jrdb_res_path)\n",
            "    print(\"--- Stanford JRDB Benchmark Results ---\")\n",
            "    display(df_jrdb)\n",
            "    \n",
            "    plt.figure(figsize=(9, 4))\n",
            "    sns.countplot(data=df_jrdb, x=\"Predicao MoveSense\", palette=\"Blues_d\")\n",
            "    plt.title(\"MoveSense Behaviour Classifications on Stanford JRDB\", fontsize=13, fontweight=\"bold\")\n",
            "    plt.xlabel(\"Predicted Behaviour\", fontsize=11)\n",
            "    plt.ylabel(\"Track Count\", fontsize=11)\n",
            "    plt.grid(axis=\"y\", linestyle=\"--\", alpha=0.7)\n",
            "    plt.tight_layout()\n",
            "    plt.show()\n",
            "else:\n",
            "    print(\"JRDB benchmark file not found.\")\n"
        ]
    })

    # --- Section 7: 50-VIDEO BENCHMARK SUITE ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. 🎬 50-Video Multi-Environment & Multi-Duration Benchmark Suite\n",
            "\n",
            "Comprehensive evaluation across **50 distinct video test scenarios** designed to test edge cases in pedestrian tracking and behaviour analysis.\n",
            "\n",
            "### ⏱️ Video Duration Categories:\n",
            "- **Category A (`< 10s`):** 13 Videos — Quick burst actions (sprinting to bus/class, tripping/falling, rapid street crossing, sudden stops).\n",
            "- **Category B (`10-20s`):** 13 Videos — Medium transit (campus walkways, cafe queue progression, downtown green-wave crossings).\n",
            "- **Category C (`20-30s`):** 12 Videos — Extended social interactions (group loitering outside library, friends chatting at cafe, running packs).\n",
            "- **Category D (`> 30s`):** 12 Videos — Long continuous surveillance (MOT17 street scene, MOT20 extreme density, JRDB robot patrol, 1-min concourse flow).\n",
            "\n",
            "### 🌍 Diverse Real-World Environments:\n",
            "- 🎓 **University Campus:** Quads, library plazas, lecture hall entrance walkways.\n",
            "- ☕ **Coffee Places & Cafeterias:** Espresso bars, ordering lines, outdoor terrace seating.\n",
            "- 🚦 **Street Crossings:** Zebra crosswalks, traffic signals, multi-lane boulevards.\n",
            "- 🏃 **People Running:** Jogging trails, sprint intervals, track & field pace groups.\n",
            "- 🚇 **Transit Hubs & Crowds:** Subway platforms, airport gates, extreme density concourses.\n",
            "- 🏥 **Fall & Emergency Anomalies:** Sudden trips, fainting, elderly slips, extended laydowns.\n"
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pandas as pd\n",
            "from scripts.benchmark_video_suite import VIDEO_CATALOG\n",
            "\n",
            "# Display full 50-video catalog overview\n",
            "df_catalog = pd.DataFrame(VIDEO_CATALOG)\n",
            "print(f\"📊 Total Benchmark Scenarios Loaded: {len(df_catalog)}\")\n",
            "\n",
            "# Breakdown by duration category and environment\n",
            "summary_cat = df_catalog.groupby(\"duration_category\")[\"id\"].count().reset_index(name=\"Count\")\n",
            "summary_env = df_catalog.groupby(\"environment\")[\"id\"].count().reset_index(name=\"Count\")\n",
            "\n",
            "display(summary_cat)\n",
            "display(summary_env)\n",
            "\n",
            "print(\"\\n--- First 10 Scenarios Sample ---\")\n",
            "display(df_catalog[[\"id\", \"name\", \"environment\", \"duration_sec\", \"duration_category\", \"num_pedestrians\"]].head(10))\n"
        ]
    })

    # --- Section 7.2: Execute Benchmark Suite ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 6.1 Execute Video Benchmark Suite & Performance Analytics\n",
            "Run MoveSense detection, tracking, and RuleEngine classification across scenarios.\n",
            "- Choose between **Fast Preview (4 representative videos across all duration buckets)** or **Full 50-Video Test Suite**."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import time\n",
            "from pathlib import Path\n",
            "from tqdm.auto import tqdm\n",
            "from movesense.detector import PedestrianDetector\n",
            "from movesense.rules import RuleEngine\n",
            "from scripts.benchmark_video_suite import VIDEO_CATALOG, generate_benchmark_sequence, run_benchmark_on_video\n",
            "\n",
            "# Benchmark configuration\n",
            "RUN_FULL_50_SUITE = True   # Set to True for all 50 videos, or False for fast 4-video sample\n",
            "\n",
            "data_dir = Path(\"data/video_benchmarks\")\n",
            "outputs_dir = Path(\"outputs/video_benchmarks\")\n",
            "results_dir = Path(\"results\")\n",
            "data_dir.mkdir(parents=True, exist_ok=True)\n",
            "outputs_dir.mkdir(parents=True, exist_ok=True)\n",
            "results_dir.mkdir(parents=True, exist_ok=True)\n",
            "\n",
            "detector = PedestrianDetector(model_name=\"yolov8n.pt\", conf_threshold=0.35)\n",
            "rule_engine = RuleEngine.from_config(\"configs/behaviour_rules.json\")\n",
            "\n",
            "if RUN_FULL_50_SUITE:\n",
            "    target_videos = VIDEO_CATALOG\n",
            "    print(f\"🚀 Running FULL 50-VIDEO BENCHMARK SUITE across all environments and duration categories...\")\n",
            "else:\n",
            "    # 4 Representative picks: 1 from each duration bucket\n",
            "    sample_ids = [\"VID_02\", \"VID_16\", \"VID_27\", \"VID_40\"]\n",
            "    target_videos = [v for v in VIDEO_CATALOG if v[\"id\"] in sample_ids]\n",
            "    print(f\"⚡ Running FAST REPRESENTATIVE BENCHMARK ({len(target_videos)} videos)...\")\n",
            "\n",
            "suite_results = []\n",
            "pbar = tqdm(target_videos, desc=\"Benchmarking MoveSense\")\n",
            "\n",
            "for meta in pbar:\n",
            "    pbar.set_postfix({\"Category\": meta[\"duration_category\"], \"Video\": meta[\"id\"]})\n",
            "    img_dir, gt_file = generate_benchmark_sequence(meta, data_dir)\n",
            "    out_mp4 = outputs_dir / f\"{meta['id']}_annotated.mp4\"\n",
            "    \n",
            "    res = run_benchmark_on_video(\n",
            "        meta=meta,\n",
            "        img_dir=img_dir,\n",
            "        gt_file=gt_file,\n",
            "        detector=detector,\n",
            "        rule_engine=rule_engine,\n",
            "        output_mp4=out_mp4\n",
            "    )\n",
            "    suite_results.append(res)\n",
            "\n",
            "df_benchmark = pd.DataFrame(suite_results)\n",
            "benchmark_csv = results_dir / \"video_benchmark_50_suite.csv\"\n",
            "df_benchmark.to_csv(benchmark_csv, index=False)\n",
            "print(f\"\\n✅ Benchmark complete! Saved {len(df_benchmark)} records to: {benchmark_csv}\")\n"
        ]
    })

    # --- Section 7.3: Analytical Reports ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 6.2 Duration & Environment Performance Analytics\n",
            "Aggregate metrics grouped by **Duration Category** (`< 10s`, `10-20s`, `20-30s`, `> 30s`) and **Environment**."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "\n",
            "# 1. Performance Summary by Duration Category\n",
            "dur_summary = df_benchmark.groupby(\"duration_category\").agg(\n",
            "    Video_Count=(\"video_id\", \"count\"),\n",
            "    Total_Frames=(\"total_frames\", \"sum\"),\n",
            "    Mean_FPS=(\"processing_fps\", \"mean\"),\n",
            "    Mean_Latency_ms=(\"latency_ms_per_frame\", \"mean\"),\n",
            "    Total_Tracks=(\"unique_tracks\", \"sum\"),\n",
            "    Total_Fall_Alerts=(\"fall_alerts\", \"sum\"),\n",
            ").reindex([\"< 10s\", \"10-20s\", \"20-30s\", \"> 30s\"]).dropna(how=\"all\")\n",
            "\n",
            "print(\"=\" * 75)\n",
            "print(\"⏱️ PERFORMANCE BREAKDOWN BY DURATION CATEGORY:\")\n",
            "print(\"=\" * 75)\n",
            "display(dur_summary)\n",
            "\n",
            "# 2. Performance Summary by Environment\n",
            "env_summary = df_benchmark.groupby(\"environment\").agg(\n",
            "    Video_Count=(\"video_id\", \"count\"),\n",
            "    Total_Tracks=(\"unique_tracks\", \"sum\"),\n",
            "    Mean_Speed_bl_s=(\"mean_speed_bl_s\", \"mean\"),\n",
            "    Total_Fall_Alerts=(\"fall_alerts\", \"sum\"),\n",
            "    Mean_FPS=(\"processing_fps\", \"mean\"),\n",
            ")\n",
            "\n",
            "print(\"\\n\" + \"=\" * 75)\n",
            "print(\"🌍 PERFORMANCE BREAKDOWN BY ENVIRONMENT:\")\n",
            "print(\"=\" * 75)\n",
            "display(env_summary)\n",
            "\n",
            "# 3. Scientific Visualization Dashboard\n",
            "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
            "\n",
            "# Chart 1: Processing Throughput across Duration Categories\n",
            "sns.barplot(\n",
            "    data=df_benchmark,\n",
            "    x=\"duration_category\",\n",
            "    y=\"processing_fps\",\n",
            "    order=[\"< 10s\", \"10-20s\", \"20-30s\", \"> 30s\"],\n",
            "    palette=\"crest\",\n",
            "    ax=axes[0],\n",
            "    capsize=0.1\n",
            ")\n",
            "axes[0].set_title(\"MoveSense Throughput (FPS) by Video Duration\", fontsize=12, fontweight=\"bold\")\n",
            "axes[0].set_xlabel(\"Duration Category\", fontsize=11)\n",
            "axes[0].set_ylabel(\"Tracking Throughput (Frames / Sec)\", fontsize=11)\n",
            "axes[0].grid(axis=\"y\", linestyle=\"--\", alpha=0.6)\n",
            "\n",
            "# Chart 2: Fall & Anomaly Safety Detections by Environment\n",
            "sns.barplot(\n",
            "    data=df_benchmark,\n",
            "    x=\"environment\",\n",
            "    y=\"fall_alerts\",\n",
            "    palette=\"Reds_r\",\n",
            "    ax=axes[1]\n",
            ")\n",
            "axes[1].set_title(\"Fall & Laydown Alerts Detected by Environment\", fontsize=12, fontweight=\"bold\")\n",
            "axes[1].set_xlabel(\"Environment\", fontsize=11)\n",
            "axes[1].set_ylabel(\"Fall Alerts Triggered\", fontsize=11)\n",
            "axes[1].tick_params(axis=\"x\", rotation=30)\n",
            "axes[1].grid(axis=\"y\", linestyle=\"--\", alpha=0.6)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig(\"results/benchmark_duration_and_environment_charts.png\", dpi=300)\n",
            "plt.show()\n"
        ]
    })

    # --- Section 8: Interactive HTML5 Video Player ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 7. Interactive In-Colab HTML5 Video Player\n",
            "Watch any rendered annotated video directly inside Google Colab.\n",
            "Select any video from the duration categories (`< 10s`, `10-20s`, `20-30s`, `> 30s`) with real-time telemetry."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from IPython.display import HTML, display\n",
            "from base64 import b64encode\n",
            "from pathlib import Path\n",
            "import ipywidgets as widgets\n",
            "\n",
            "available_videos = sorted(list(Path(\"outputs/video_benchmarks\").glob(\"*_annotated.mp4\")))\n",
            "if not available_videos:\n",
            "    # Fallback to demo video\n",
            "    available_videos = list(Path(\"outputs\").glob(\"*.mp4\"))\n",
            "\n",
            "print(f\"🎬 Found {len(available_videos)} rendered MP4 videos available for playback.\")\n",
            "\n",
            "def play_video_inline(video_filename: str, width: int = 780):\n",
            "    video_path = Path(video_filename)\n",
            "    if not video_path.exists():\n",
            "        print(f\"Error: Video not found at {video_path}\")\n",
            "        return\n",
            "        \n",
            "    vid_bytes = video_path.read_bytes()\n",
            "    data_url = \"data:video/mp4;base64,\" + b64encode(vid_bytes).decode()\n",
            "    vid_name = video_path.stem\n",
            "    \n",
            "    html_code = f\"\"\"\n",
            "    <div style=\"background: #1e1e24; border-radius: 12px; padding: 18px; max-width: {width}px; margin: 15px auto; box-shadow: 0 8px 24px rgba(0,0,0,0.3); font-family: sans-serif;\">\n",
            "        <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;\">\n",
            "            <span style=\"color: #00e5ff; font-weight: bold; font-size: 16px;\">📹 MoveSense HD Video Player</span>\n",
            "            <span style=\"background: #2a2a35; color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 13px;\">{vid_name}</span>\n",
            "        </div>\n",
            "        <video width=\"100%\" controls autoplay loop style=\"border-radius: 8px; border: 1px solid #333;\">\n",
            "            <source src=\"{data_url}\" type=\"video/mp4\">\n",
            "            Your browser does not support HTML5 video playback.\n",
            "        </video>\n",
            "        <div style=\"margin-top: 10px; font-size: 12px; color: #aaa; display: flex; justify-content: space-between;\">\n",
            "            <span>🟢 Upright Tracked | 🔴 Fall Alert (Aspect Ratio &gt; 1.05)</span>\n",
            "            <span>H.264 Web Compatible</span>\n",
            "        </div>\n",
            "    </div>\n",
            "    \"\"\"\n",
            "    display(HTML(html_code))\n",
            "\n",
            "# Interactive dropdown selector\n",
            "if available_videos:\n",
            "    video_dropdown = widgets.Dropdown(\n",
            "        options=[(p.name, str(p)) for p in available_videos],\n",
            "        description=\"Choose Video:\",\n",
            "        style={\"description_width\": \"initial\"},\n",
            "        layout=widgets.Layout(width=\"450px\")\n",
            "    )\n",
            "    ui = widgets.interactive(play_video_inline, video_filename=video_dropdown)\n",
            "    display(ui)\n",
            "else:\n",
            "    print(\"No rendered videos found yet. Run the benchmark cell above to render output videos!\")\n"
        ]
    })

    # --- Section 9: Export Artifacts ---
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 8. Export Results & Artifacts\n",
            "Archive all CSV evaluations, benchmark metrics, and rendered videos into a single zip file for download."
        ]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import shutil\n",
            "from pathlib import Path\n",
            "from google.colab import files\n",
            "\n",
            "# Create zip archive of all results and rendered videos\n",
            "archive_name = \"movesense_50_video_benchmark_results\"\n",
            "export_dir = Path(\"export_bundle\")\n",
            "export_dir.mkdir(exist_ok=True)\n",
            "\n",
            "# Copy results and outputs\n",
            "shutil.copytree(\"results\", export_dir / \"results\", dirs_exist_ok=True)\n",
            "shutil.copytree(\"outputs/video_benchmarks\", export_dir / \"videos\", dirs_exist_ok=True)\n",
            "\n",
            "zip_path = shutil.make_archive(archive_name, \"zip\", export_dir)\n",
            "print(f\"✅ Complete benchmark bundle packaged at: {zip_path} ({Path(zip_path).stat().st_size / 1024:.1f} KB)\")\n",
            "\n",
            "# Trigger download to local browser\n",
            "files.download(zip_path)\n"
        ]
    })

    notebook_data = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {
                "provenance": [],
                "toc_visible": True
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }

    out_file = Path("notebooks/movesense_master_benchmark_and_training.ipynb")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(notebook_data, indent=2))
    print(f"🎉 Successfully created {out_file} with {len(cells)} cells!")

if __name__ == "__main__":
    create_notebook()
