// GLTFLoader로 선수 모델과 애니메이션 클립을 불러옵니다.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/**
 * @returns {Promise<{ model: THREE.Object3D, clips: THREE.AnimationClip[], isPlaceholder: boolean }>}
 */
export async function loadPlayer({ url, scale = 1 }) {
  try {
    // loadAsync는 로딩이 끝나면 gltf를 돌려주는 Promise 버전입니다.
    const gltf = await new GLTFLoader().loadAsync(url);
    const model = gltf.scene;
    model.scale.setScalar(scale);
    model.traverse((obj) => {
      if (obj.isMesh) { obj.castShadow = true; obj.frustumCulled = false; }   // 뼈대 애니메이션 중 사라지는 것 방지
    });
    // gltf.animations 안에 Idle, Run 같은 클립들이 들어 있습니다.
    console.info('불러온 애니메이션 클립:', gltf.animations.map((c) => c.name).join(', ') || '(없음)');
    return { model, clips: gltf.animations, isPlaceholder: false };
  } catch (err) {
    // 모델을 못 불러와도 이동·카메라는 확인할 수 있게 임시 캐릭터를 만듭니다.
    console.warn('모델 로딩 실패, 임시 캐릭터를 사용합니다:', err);
    return { model: makePlaceholder(), clips: [], isPlaceholder: true };
  }
}

function makePlaceholder() {
  const group = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.CapsuleGeometry(0.3, 1.1, 6, 12),
    new THREE.MeshStandardMaterial({ color: 0x2f6bff }),
  );
  body.position.y = 0.85;
  const nose = new THREE.Mesh(                               // 앞(+Z)을 알 수 있게 달아 둔 표시
    new THREE.BoxGeometry(0.15, 0.15, 0.3),
    new THREE.MeshStandardMaterial({ color: 0xffd84a }),
  );
  nose.position.set(0, 1.35, 0.3);
  body.castShadow = nose.castShadow = true;
  group.add(body, nose);
  return group;
}
