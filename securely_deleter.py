#!/usr/bin/env python3
# SCDelete — Securely Deleter (activation-first licensed build)

import os, sys, time, json, hashlib, platform, subprocess, argparse
from pathlib import Path
import psutil

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    import urllib.request, urllib.error
    _HAS_REQUESTS = False

LICENSE_API = "https://scdelete-license.justoce09.workers.dev"
CONF_PATH = Path.home() / ".scdelete_config.json"
DEFAULT_PROCESS = "Classroom.exe"
DEFAULT_INTERVAL = 1.0

# ---------------- utilities ----------------
def _load_conf():
    if CONF_PATH.exists():
        try:
            return json.loads(CONF_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_conf(data: dict):
    try:
        CONF_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

def _http_post_json(url: str, payload: dict, timeout: float = 10.0) -> dict:
    if _HAS_REQUESTS:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    else:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

def device_fingerprint() -> str:
    bits = []
    try:
        if sys.platform.startswith('win'):
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography")
            v, _ = winreg.QueryValueEx(k, "MachineGuid")
            if v: bits.append(f"win_guid:{v}")
    except Exception: pass
    if sys.platform.startswith('linux'):
        for f in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            try:
                v = Path(f).read_text().strip()
                if v: bits.append(f"linux_mid:{v}")
            except: pass
    if sys.platform == "darwin":
        try:
            s = subprocess.check_output(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], text=True)
            for line in s.splitlines():
                if "IOPlatformUUID" in line:
                    bits.append("mac_uuid:" + line.split('"')[-2])
                    break
        except: pass
    try:
        import uuid
        bits.append(f"mac:{uuid.getnode():012x}")
    except: pass
    try:
        bits.append(str(platform.uname()))
    except: pass
    return hashlib.sha256("||".join(bits).encode()).hexdigest()

# ---------------- licensing ----------------
def ensure_license_key(cfg, provided=None):
    if provided:
        cfg["license_key"] = provided.strip(); _save_conf(cfg); return cfg["license_key"]
    if "license_key" in cfg: return cfg["license_key"]
    env_key = os.environ.get("SCDELETE_LICENSE_KEY")
    if env_key: cfg["license_key"] = env_key.strip(); _save_conf(cfg); return cfg["license_key"]
    lk = input("Enter your SCDelete license key: ").strip()
    cfg["license_key"] = lk; _save_conf(cfg); return lk

def license_activate(license_key):
    payload = {"license_key": license_key, "device_id": device_fingerprint(), "app": "securely-deleter"}
    data = _http_post_json(f"{LICENSE_API}/activate", payload)
    if not data.get("ok"):
        raise SystemExit(f"[License] Activation failed: {data.get('error')}")
    if data.get("bound"): print("[License] Activated and bound to this device.")
    else: print("[License] Already bound to this device.")

def license_validate(license_key, quiet=False):
    payload = {"license_key": license_key, "device_id": device_fingerprint(), "app": "securely-deleter", "ts": int(time.time())}
    data = _http_post_json(f"{LICENSE_API}/validate", payload)
    if not (data.get("ok") and data.get("status") == "active"):
        raise SystemExit(f"[License] Validation failed: {data.get('error') or data.get('status') or 'inactive'}")
    if not quiet: print("[License] Validation OK (subscription active, device matched).")

# ---------------- core logic ----------------
def kill_process_by_name(name: str):
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if proc.info.get("name") == name:
            try:
                proc.terminate()
                print(f"Terminated {name} (PID {proc.info['pid']})")
            except Exception as e:
                print(f"Error terminating process: {e}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process-name","-p", default=DEFAULT_PROCESS)
    ap.add_argument("--interval","-i", type=float, default=DEFAULT_INTERVAL)
    ap.add_argument("--license-key", default=None)
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    cfg = _load_conf()
    license_key = ensure_license_key(cfg, args.license_key)

    # 🔑 Always activate first, then validate
    try:
        license_activate(license_key)
    except SystemExit as e:
        # If already bound, activation will just say so — safe to ignore
        print(e)
    license_validate(license_key)

    if args.validate_only:
        print("[License] Validate-only OK."); return

    print(f"[SCDelete] Monitoring {args.process_name!r} every {args.interval}s. Ctrl+C to stop.")
    try:
        while True:
            kill_process_by_name(args.process_name)
            time.sleep(max(0.1, args.interval))
    except KeyboardInterrupt:
        print("\n[SCDelete] Stopped.")

if __name__ == "__main__":
    main()
