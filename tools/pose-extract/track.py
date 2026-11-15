import json, numpy as np
D = {int(k): v for k, v in json.load(open("det_1_136.json")).items()}
tracks = []  # each: list of (frame, det)
for f in sorted(D):
    used = set()
    for tr in tracks:
        lf, ld = tr[-1]
        if f - lf > 2: continue
        best, bd = None, 70
        for i, d in enumerate(D[f]):
            if i in used: continue
            dist = np.hypot(d["cx"]-ld["cx"], d["cy"]-ld["cy"])
            if dist < bd: bd, best = dist, i
        if best is not None: used.add(best); tr.append((f, D[f][best]))
    for i, d in enumerate(D[f]):
        if i not in used: tracks.append([(f, d)])
tracks = [t for t in tracks if len(t) >= 12]
tracks.sort(key=lambda t: -len(t))
for n, t in enumerate(tracks[:14]):
    fs = [f for f, _ in t]; vis = np.mean([d["vis"] for _, d in t]); h = np.mean([d["h"] for _, d in t])
    mv = np.hypot(t[-1][1]["cx"]-t[0][1]["cx"], t[-1][1]["cy"]-t[0][1]["cy"])
    # 다리 벌림(양 발목 사이 world 거리)의 변동 = 달리는지 여부
    sep = [np.linalg.norm(np.array(d["world"][27])-np.array(d["world"][28])) for _, d in t]
    print(n, "frames", fs[0], "-", fs[-1], "n", len(t), "vis %.2f h %.0f move %.0f ankleSep mean %.2f std %.2f" % (vis, h, mv, np.mean(sep), np.std(sep)), "start (%.0f,%.0f)" % (t[0][1]["cx"], t[0][1]["cy"]))
json.dump([[(f, d) for f, d in t] for t in tracks[:14]], open("tracks.json", "w"))
