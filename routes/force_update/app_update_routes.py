import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter()

APK_DIR = os.path.join(os.getcwd(), "apk-builds")
def get_apk_versions():
    files = []
    if os.path.isdir(APK_DIR):
        files = [f for f in os.listdir(APK_DIR) if f.endswith(".apk")]
    # Extract version number and sort numerically
    def extract_version(filename):
        # Expected format: atx_app_ver_101.apk
        try:
            base = os.path.splitext(filename)[0]
            parts = base.split('_')
            version = int(parts[-1])
            return version
        except Exception:
            return -1  # Put malformed files at the start
    return sorted(files, key=extract_version)

@router.get("/get-all/versions")
def get_all_versions():
    versions = get_apk_versions()
    return {"versions": versions}

@router.get("/download/{filename}")
def download_specific_apk(filename: str):
    file_path = os.path.join(APK_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/vnd.android.package-archive", filename=filename)

@router.get("/download-latest")
def download_latest_apk():
    versions = get_apk_versions()
    if not versions:
        raise HTTPException(status_code=404, detail="No APK files found")
    latest = versions[-1]
    file_path = os.path.join(APK_DIR, latest)
    return FileResponse(file_path, media_type="application/vnd.android.package-archive", filename=latest)

@router.get("/latest-version")
def get_latest_version():
    versions = get_apk_versions()
    if not versions:
        return JSONResponse({"version": None, "apk_file": None, "apk_url": None})
    latest = versions[-1]
    # Extract version number for response
    try:
        version_num = int(os.path.splitext(latest)[0].split('_')[-1])
    except Exception:
        version_num = None
    return {
        "version": version_num,
        "apk_file": latest,
        "apk_url": f"/mr-app-updates/download/{latest}"
    }