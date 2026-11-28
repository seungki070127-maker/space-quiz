// 장면 꾸미기: 조명, 잔디, 경기장 선. (이동·애니메이션과는 무관한 배경입니다)
import * as THREE from 'three';

export function buildWorld(scene) {
  scene.background = new THREE.Color(0x9fd3ff);
  scene.fog = new THREE.Fog(0x9fd3ff, 60, 160);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x3a6b3a, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 2.2);
  sun.position.set(-20, 30, 12);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -15, right: 15, top: 15, bottom: -15, near: 1, far: 80 });
  scene.add(sun, sun.target);

  // 체크무늬 잔디: 작은 캔버스에 그려서 반복 텍스처로 사용
  const cv = document.createElement('canvas');
  cv.width = cv.height = 64;
  const g = cv.getContext('2d');
  g.fillStyle = '#4aa13f'; g.fillRect(0, 0, 64, 64);
  g.fillStyle = '#429638'; g.fillRect(0, 0, 32, 32); g.fillRect(32, 32, 32, 32);
  const tex = new THREE.CanvasTexture(cv);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(7, 5);
  tex.colorSpace = THREE.SRGBColorSpace;

  const grass = new THREE.Mesh(new THREE.PlaneGeometry(120, 84), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
  grass.rotation.x = -Math.PI / 2;
  grass.receiveShadow = true;
  scene.add(grass);

  // 터치라인, 중앙선, 센터서클
  const mat = new THREE.LineBasicMaterial({ color: 0xffffff });
  const line = (pts) => scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts.map(([x, z]) => new THREE.Vector3(x, 0.02, z))), mat));
  line([[-52.5, -34], [52.5, -34], [52.5, 34], [-52.5, 34], [-52.5, -34]]);
  line([[0, -34], [0, 34]]);
  line(Array.from({ length: 49 }, (_, i) => [Math.cos(i / 48 * Math.PI * 2) * 9.15, Math.sin(i / 48 * Math.PI * 2) * 9.15]));

  return { sun };
}
