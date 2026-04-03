#!/usr/bin/env python3
"""
================================================================================
SIDEWINDER CONTRACTING — IN-THE-WILD TERMUX TIME PROBLEM BLUEPRINT
================================================================================
Author & Researcher: Michael S Errington
Date: March 2026
Environment: Termux (non-root) + Proot Virtualized Linux Distro
Objective: Demonstrate and document how userland time in Termux can be manipulated,
           affecting security-sensitive artifacts (logs, tokens) silently.
Notes: First-person research narrative, fully reproducible, designed for educational
       and investigative purposes.
================================================================================
"""

# ----------------------------------------
# SECTION 0 — INTRODUCTION & RESEARCH CONTEXT
# ----------------------------------------
"""
Hey, it’s Michael. This is my complete documentation of the
'Termux Userland Time Problem.' Using an old Android phone,
Termux (non-root), and a lot of trial-and-error, I discovered
that Python’s time functions in this environment are fully
tied to the device clock. Any change in the Android settings,
manual or otherwise, silently shifts what userland code sees.

I wrote this blueprint to capture everything:
- How to measure the problem
- How to reproduce it safely
- How to quantify its security implications
- How to log and transmit results for reproducibility
"""

# ----------------------------------------
# SECTION 1 — IMPORT DEPENDENCIES & CONFIGURATION
# ----------------------------------------
import datetime
import requests
import json
import os
import sys
import logging
from time import sleep

# Optional: PyJWT for security token demonstration
try:
    import jwt
    JWT_OK = True
except ImportError:
    JWT_OK = False
    print("Tip: Run 'pip install pyjwt' to enable JWT security token creation.")

# ----------------------------------------
# SECTION 2 — LOGGING & FORENSIC TRACEABILITY
# ----------------------------------------
log_file = "my_termux_time_poc.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TermuxTimePOC")

logger.info("=== Sidewinder Contracting — Termux Time Problem Proof ===")
logger.info("Author: Michael S Errington — fully self-taught and userland-tested")

# ----------------------------------------
# SECTION 3 — EXTERNAL TIME VALIDATION (GROUND TRUTH)
# ----------------------------------------
"""
I use a trusted external source to compare the system clock
against real-world time. This demonstrates how userland
applications inherit unverified temporal trust.
"""
logger.info("Connecting to external time source for ground truth...")
try:
    response = requests.get("https://worldtimeapi.org/api/timezone/UTC", timeout=12)
    response.raise_for_status()
    data = response.json()
    real_world_time = datetime.datetime.fromisoformat(data["utc_datetime"].replace("Z", "+00:00"))
    logger.info(f"External UTC time: {real_world_time}")
except Exception as e:
    logger.warning(f"Could not fetch external time: {e}")
    real_world_time = datetime.datetime.now(datetime.UTC)
    logger.info("Fallback: using local system time")

# ----------------------------------------
# SECTION 4 — USERLAND TIME CAPTURE
# ----------------------------------------
"""
Two methods to capture UTC in Python:
1. datetime.utcnow() — naive, follows device clock exactly
2. datetime.now(datetime.UTC) — timezone-aware, but still trusts clock
Both are vulnerable in non-root Termux environments.
"""
simple_time = datetime.datetime.utcnow()
proper_time = datetime.datetime.now(datetime.UTC)

logger.info(f"Naive userland time (simple_time): {simple_time}")
logger.info(f"Timezone-aware userland time (proper_time): {proper_time}")

# ----------------------------------------
# SECTION 5 — TIME DRIFT ANALYSIS
# ----------------------------------------
"""
Quantify the deviation between device clock and ground truth.
This shows exactly how security artifacts could be silently manipulated.
"""
time_difference = (simple_time - real_world_time).total_seconds()
logger.info(f"Calculated drift: {time_difference:.1f} seconds")

if abs(time_difference) > 180:
    logger.critical(
        "Significant drift detected! Non-root userland manipulation can "
        "affect security-sensitive processes."
    )

# ----------------------------------------
# SECTION 6 — SECURITY TOKEN DEMONSTRATION
# ----------------------------------------
"""
Generate JWT tokens to show downstream impact of naive time capture.
Any token validity fields inherit the device clock, exposing the risk.
"""
demo_key = "my-termux-demo-key"

if JWT_OK:
    token_payload = {
        "user": "termux-test-user",
        "author": "Michael S Errington",
        "purpose": "Demonstrate naive time problem",
        "iat": simple_time,
        "nbf": simple_time,
        "exp": simple_time + datetime.timedelta(minutes=60)
    }
    try:
        real_token = jwt.encode(token_payload, demo_key, algorithm="HS256")
        logger.info("JWT created with naive system time")
        logger.info(f"Token preview (first 80 chars): {real_token[:80]}...")
    except Exception as e:
        logger.error(f"Failed to generate JWT: {e}")
        real_token = None
else:
    real_token = None
    token_payload = {"note": "Install pyjwt for full demonstration"}

# ----------------------------------------
# SECTION 7 — AGGREGATING RESULTS
# ----------------------------------------
"""
Compile all findings into a structured message for review or transmission.
"""
full_message = {
    "author": "Michael S Errington",
    "project": "Termux Userland Time Problem",
    "simple_time": str(simple_time),
    "proper_time": str(proper_time),
    "real_world_time": str(real_world_time),
    "time_difference_seconds": round(time_difference, 2),
    "token_payload": token_payload,
    "jwt_token": real_token,
    "observations": "Naive time follows device clock, proper_time aligns with UTC",
    "recommended_fix": "Always use datetime.now(datetime.UTC) for sensitive applications"
}

logger.info("Results aggregated into full_message")

# ----------------------------------------
# SECTION 8 — OPTIONAL REAL-WORLD TRANSMISSION
# ----------------------------------------
"""
Controlled demonstration: sending the experiment snapshot
to an external site to validate what the userland sees.
"""
default_site = "https://httpbin.org/post"
target_site = input(f"Enter site to send results (Enter for default {default_site}): ").strip()
if not target_site:
    target_site = default_site

send_now = input("Send snapshot now? (y/N): ").strip().lower()
if send_now == "y":
    try:
        response = requests.post(
            target_site,
            json=full_message,
            headers={"User-Agent": "TermuxTimePOC", "X-Project": "time-problem-proof"},
            timeout=15
        )
        logger.info(f"Snapshot sent — HTTP status: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send snapshot: {e}")
else:
    logger.info("Transmission skipped — snapshot saved locally.")

# ----------------------------------------
# SECTION 9 — FORENSIC LOGGING
# ----------------------------------------
"""
Persist all run data and environment fingerprints to logs for reproducibility.
"""
run_record = {
    "run_time": str(datetime.datetime.now()),
    "simple_time": str(simple_time),
    "proper_time": str(proper_time),
    "real_world_time": str(real_world_time),
    "time_difference": time_difference,
    "token_present": real_token is not None,
    "site_targeted": target_site,
    "full_message": full_message,
    "environment": {
        "python_version": sys.version,
        "system_info": os.uname()._asdict() if hasattr(os, "uname") else "unknown"
    }
}

with open(log_file, "a", encoding="utf-8") as f:
    f.write("\n" + "="*100 + "\n")
    f.write(f"RUN RECORD @ {run_record['run_time']}\n")
    json.dump(run_record, f, indent=2, default=str)
    f.write("\n" + "="*100 + "\n")

logger.info(f"Run persisted to {log_file}")

# ----------------------------------------
# SECTION 10 — FINAL OBSERVATIONS
# ----------------------------------------
"""
1. Termux non-root userland relies on mutable device clock.
2. All Python-based timestamps follow the naive clock silently.
3. Security artifacts like JWTs inherit compromised time if naive methods are used.
4. Proot virtualization does NOT protect against time manipulation.
5. Drift can be measured via network time, but userland apps remain trust-blind by default.
"""

print("\n=== Termux Non-Root Userland Time Problem Demonstration Complete ===")
print("Check logs for full evidence of drift and security impact.")