/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import * as THREE from "three";
import { FBXLoader } from "three/examples/jsm/loaders/FBXLoader";
import { PointerLockControls } from "three/examples/jsm/controls/PointerLockControls";

import React from "react";

const SPEED_SCALE = 4;

class Scene extends React.Component {
  constructor(props) {
    super(props);
    this.props = props;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xa0a0a0);
    this.camera = new THREE.PerspectiveCamera(
      45,
      this.props.width / this.props.height,
      1,
      2000
    );
    this.ref = React.createRef();
    this.scene = scene;
  }
  componentDidMount() {
    const { scene } = this;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(this.props.width, this.props.height);
    renderer.shadowMap.enabled = true; // ?
    this.renderer = renderer;

    this.ref.current.appendChild(renderer.domElement);

    const mesh = new THREE.Mesh(
      new THREE.PlaneBufferGeometry(2000, 2000),
      new THREE.MeshPhongMaterial({ color: 0x999999, depthWrite: false })
    );
    mesh.rotation.x = -Math.PI / 2;
    mesh.receiveShadow = true;
    // scene.add(mesh);

    const grid = new THREE.GridHelper(2000, 20, 0x000000, 0x000000);
    grid.material.opacity = 0.2;
    grid.material.transparent = true;
    // scene.add(grid);

    this.updateCamera();
    this.loadScene();
    this.animate();
  }

  updateCamera(
    posX = -774,
    posY = 2.77,
    posZ = -222.6,
    lookX = -774.89,
    lookY = 2.6457,
    lookZ = -223.0287
  ) {
    const { camera, renderer, scene } = this;

    camera.position.set(posX, posY, posZ);
    camera.lookAt(lookX, lookY, lookZ);
    camera.updateMatrixWorld();

    renderer.render(scene, camera);
  }

  onKeyDown(event) {
    const { controls, camera } = this;

    switch (event.keyCode) {
      case 87: // w
        controls.moveForward(2 * SPEED_SCALE);
        break;
      case 65: // a
        controls.moveRight(-1 * SPEED_SCALE);
        break;
      case 83: // s
        controls.moveForward(-2 * SPEED_SCALE);
        break;
      case 68: // d
        controls.moveRight(1 * SPEED_SCALE);
        break;
      default:
        return;
    }

    const v = new THREE.Vector3(0, 0, -1)
      .applyQuaternion(camera.quaternion)
      .add(camera.position);
    this.props.onPositionUpdate(
      camera.position.x,
      camera.position.y,
      camera.position.z,
      v.x,
      v.y,
      v.z
    );
  }

  animate() {
    const { renderer, scene, camera } = this;

    this.cancelId = requestAnimationFrame(this.animate.bind(this));
    renderer.render(scene, camera);
  }

  componentWillUnmount() {
    cancelAnimationFrame(this.cancelId);
  }

  loadScene() {
    const { scene, renderer, camera } = this;
    const loader = new FBXLoader();
    const modelUrl = "/clothing_store/Assets/clothing_store.fbx";

    loader.load(modelUrl, function (object) {
      object.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        } else if (child.isCamera) {
        }
      });
      scene.add(object);
      renderer.render(scene, camera);
    });

    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444);
    hemiLight.position.set(0, 200, 0);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xffffff);
    dirLight.position.set(0, 200, 100);
    dirLight.castShadow = true;
    dirLight.shadow.camera.top = 180;
    dirLight.shadow.camera.bottom = -100;
    dirLight.shadow.camera.left = -120;
    dirLight.shadow.camera.right = 120;
    scene.add(dirLight);

    scene.add(new THREE.CameraHelper(dirLight.shadow.camera));

    let controls = new PointerLockControls(camera, renderer.domElement);
    document.addEventListener("keydown", this.onKeyDown.bind(this), false);

    controls.addEventListener("change", () => {
      const v = new THREE.Vector3(0, 0, -1)
        .applyQuaternion(camera.quaternion)
        .add(camera.position);

      this.props.onPositionUpdate(
        camera.position.x,
        camera.position.y,
        camera.position.z,
        v.x,
        v.y,
        v.z
      );
    });
    this.controls = controls;

    if (this.props.disableControls) {
      this.controls.enabled = false;
    }
  }

  componentDidUpdate(prevProps) {
    if (
      this.props.disableControls !== prevProps.disableControls &&
      this.controls
    ) {
      if (this.props.disableControls) {
        this.controls.enabled = false;
      } else {
        this.controls.enabled = true;
      }
    }
  }

  handleClick() {
    this.controls.lock();
  }

  render() {
    return (
      <div
        height={this.props.height}
        width={this.props.width}
        ref={this.ref}
        onClick={this.handleClick.bind(this)}
      ></div>
    );
  }
}

// Returns a function, that, when invoked, will only be triggered at most once
// during a given window of time. Normally, the throttled function will run
// as much as it can, without ever going more than once per `wait` duration;
// but if you'd like to disable the execution on the leading edge, pass
// `{leading: false}`. To disable execution on the trailing edge, ditto.
function throttle(func, wait, options) {
  var context, args, result;
  var timeout = null;
  var previous = 0;
  if (!options) options = {};
  var later = function () {
    previous = options.leading === false ? 0 : Date.now();
    timeout = null;
    result = func.apply(context, args);
    if (!timeout) context = args = null;
  };
  return function () {
    var now = Date.now();
    if (!previous && options.leading === false) previous = now;
    var remaining = wait - (now - previous);
    context = this;
    args = arguments;
    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      previous = now;
      result = func.apply(context, args);
      if (!timeout) context = args = null;
    } else if (!timeout && options.trailing !== false) {
      timeout = setTimeout(later, remaining);
    }
    return result;
  };
}

export default Scene;
