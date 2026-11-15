import sys, json, time, cv2, numpy as np, mediapipe as mp
from mediapipe.tasks import python as P
from mediapipe.tasks.python import vision
opt = vision.PoseLandmarkerOptions(base_options=P.BaseOptions(model_asset_path="pose_heavy.task"), running_mode=vision.RunningMode.IMAGE,
    num_poses=5, min_pose_detection_confidence=0.3, min_pose_presence_confidence=0.3)
det = vision.PoseLandmarker.create_from_options(opt)
TILES = [(x, y) for y in (100, 760) for x in (0, 280)]
TS, UP = 800, 2
def run(frame_no):
    img = cv2.imread(f"fr/{frame_no:04d}.png"); out = []
    for (tx, ty) in TILES:
        crop = cv2.resize(img[ty:ty+TS, tx:tx+TS], None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
        res = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
        for lm, wl in zip(res.pose_landmarks, res.pose_world_landmarks):
            px = [(tx + l.x*TS, ty + l.y*TS) for l in lm]
            vis = float(np.mean([l.visibility for l in lm[11:]]))
            ys = [p[1] for p in px]; h = max(ys) - min(ys)
            cx = (px[23][0]+px[24][0])/2; cy = (px[23][1]+px[24][1])/2
            if h < 60 or h > 400: continue
            if any(abs(cx-o["cx"]) < 40 and abs(cy-o["cy"]) < 40 for o in out): continue
            out.append(dict(cx=cx, cy=cy, h=h, vis=vis, px=[[round(a,1), round(b,1)] for a,b in px],
                            world=[[round(l.x,4), round(l.y,4), round(l.z,4)] for l in wl], wvis=[round(l.visibility,2) for l in wl]))
    return out
a, b = int(sys.argv[1]), int(sys.argv[2]); t = time.time(); allf = {}
for f in range(a, b+1):
    allf[f] = run(f)
    if f % 20 == 0: print(f, len(allf[f]), round(time.time()-t,1), flush=True)
json.dump(allf, open(f"det_{a}_{b}.json", "w"))
print("done", sum(len(v) for v in allf.values()), "detections", round(time.time()-t,1), "s")
