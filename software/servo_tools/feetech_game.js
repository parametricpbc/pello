// feetech_game.js — arm-tip touch game for feetech_gui.html
// Depends on THREE being loaded globally (via CDN in the parent HTML).

class ArmGame {
  constructor() {
    this.score      = 0;
    this.activeArm  = null;   // 'left' | 'right'
    this.goalMesh   = null;
    this.scenes     = {};     // {left: THREE.Scene, right: THREE.Scene}
    this.getEEPos   = {};     // {left: fn, right: fn}
    this._hitting   = false;  // debounce during flash animation
    this._animId    = null;   // rAF id for goal pulse

    this.HIT_RADIUS  = 0.05;  // 5 cm
    this.GOAL_RADIUS = 0.0125; // visual sphere radius
  }

  // Call once after both arm 3D scenes are ready.
  // arms = { left: {scene, getEEPosition}, right: {scene, getEEPosition} }
  init(arms) {
    this.scenes   = { left: arms.left.scene,          right: arms.right.scene };
    this.getEEPos = { left: arms.left.getEEPosition,  right: arms.right.getEEPosition };
    this._spawnGoal();
  }

  // Called every frame from createArm() after update3D().
  onEEUpdate(armName, eeWorldPos) {
    if (!this.activeArm || armName !== this.activeArm) return;
    if (this._hitting || !this.goalMesh) return;
    if (eeWorldPos.distanceTo(this.goalMesh.position) < this.HIT_RADIUS) {
      this._onHit();
    }
  }

  _onHit() {
    this._hitting = true;
    this.score++;
    this._updateScoreDOM();

    // Flash: scale up goal mesh then remove it.
    if (this.goalMesh) {
      this.goalMesh.scale.setScalar(1.8);
      if (this.goalMesh.material) {
        this.goalMesh.material.emissive.setHex(0xFFFFFF);
        this.goalMesh.material.opacity = 1.0;
      }
    }

    setTimeout(() => {
      this._removeGoal();
      this._hitting = false;
      // Always respawn — catch any error so the loop never silently stops.
      try { this._spawnGoal(); } catch(e) { console.error('[game] spawn error:', e); }
    }, 320);
  }

  _spawnGoal() {
    this._removeGoal();

    // Randomly pick an arm.
    this.activeArm = Math.random() < 0.5 ? 'left' : 'right';

    const pos = this._sampleWorkspace();

    const geo = new THREE.SphereGeometry(this.GOAL_RADIUS, 16, 12);
    const mat = new THREE.MeshPhongMaterial({
      color:       0x4AFFC8,
      emissive:    0x1A8866,
      transparent: true,
      opacity:     0.85,
      shininess:   80,
    });
    this.goalMesh = new THREE.Mesh(geo, mat);
    this.goalMesh.position.copy(pos);
    this.scenes[this.activeArm].add(this.goalMesh);

    this._startPulse();
    this._updateScoreDOM();
  }

  _removeGoal() {
    if (this._animId !== null) {
      cancelAnimationFrame(this._animId);
      this._animId = null;
    }
    if (this.goalMesh) {
      const sc = this.scenes[this.activeArm];
      if (sc) sc.remove(this.goalMesh);
      if (this.goalMesh.geometry) this.goalMesh.geometry.dispose();
      if (this.goalMesh.material) this.goalMesh.material.dispose();
      this.goalMesh = null;
    }
  }

  // Oscillate goal scale ±10 % so it's easy to spot.
  _startPulse() {
    const mesh = this.goalMesh;
    let t = 0;
    const animate = () => {
      if (!this.goalMesh || this.goalMesh !== mesh) return;
      t += 0.04;
      const s = 1.0 + 0.10 * Math.sin(t);
      mesh.scale.setScalar(s);
      this._animId = requestAnimationFrame(animate);
    };
    this._animId = requestAnimationFrame(animate);
  }

  // Sample a random ground-level position in the outer reach zone.
  // Targets sit flat on the grid (y = GOAL_RADIUS) at 22–38 cm horizontal
  // from the arm base, covering most of the arm's practical ground reach.
  _sampleWorkspace() {
    const azim = (-70 + Math.random() * 140) * Math.PI / 180;  // ±70° pan
    const r    = 0.22 + Math.random() * 0.13;                  // 22–35 cm
    return new THREE.Vector3(
      r * Math.sin(azim),
      this.GOAL_RADIUS,   // sphere sits on the ground plane
      r * Math.cos(azim)
    );
  }

  _updateScoreDOM() {
    const scoreEl = document.getElementById('game-score');
    const armEl   = document.getElementById('game-arm');
    if (scoreEl) scoreEl.textContent = this.score;
    if (armEl)   armEl.textContent   = this.activeArm ? this.activeArm.toUpperCase() : '—';
  }
}

// Global singleton — referenced by feetech_gui.html inline script.
const game = new ArmGame();
