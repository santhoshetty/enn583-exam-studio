T = dict(
id='w07', week=7, tab='SLAM, VIO & evaluation', title='Direct methods, visual–inertial odometry, evaluation and visual SLAM',
lead='Alternatives to feature matching (direct photometric methods), adding an IMU, measuring VO quality with ATE and RPE, and what SLAM adds on top of VO.',
docs=[dict(path='notes/Week07.pdf', title='Week 7 lecture: Visual SLAM, evaluation, VIO, dense and direct methods', pages=75),
      dict(path='notes/papers/ORB-SLAM3.pdf', title='ORB-SLAM3 paper (Campos et al., T-RO 2021)', pages=18)],
prac=None,
eli5=[
 ('Direct vs feature-based', 'Feature-based: pick landmarks, match them, measure how far they moved. Direct: slide one whole photo over the other until the brightness lines up, with no matching step.', None),
 ('Camera + IMU', 'The IMU is an inner ear: very fast, and it never gets blinded by darkness or blur, but it drifts. The camera is slower but anchored to the world. Together they keep each other honest.', None),
 ('ATE vs RPE', 'ATE: how far from the true route are you overall? RPE: how good is each step? One wrong turn early on ruins ATE even if every later step is perfect.', None),
 ('SLAM vs VO', 'VO is walking with a pedometer. SLAM also keeps a map, recognises “I’ve been here before” and corrects the whole path when the loop closes.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 180" role="img" aria-label="Loop closure: an odometry path drifts so its end misses the start; a loop-closure constraint pulls the path back into a consistent loop">
<path class="ln dash" d="M60 140 C40 60 120 25 220 30 C330 35 420 50 440 110 C455 150 360 170 300 160" style="stroke:var(--muted)"/>
<path class="ac" d="M60 140 C40 70 120 35 220 40 C320 45 400 60 410 110 C420 150 150 170 70 145"/>
<circle class="fi" cx="60" cy="140" r="5"/><text x="20" y="165" class="sm">start</text>
<circle class="fe" cx="300" cy="160" r="5"/><text x="286" y="152" class="sm">drifted end</text>
<path class="ev" d="M300 160 C220 175 120 170 64 144"/><text x="160" y="178" class="sm">loop-closure constraint</text>
<text x="300" y="22" class="sm">dashed: VO only · solid: after loop closure + pose graph</text>
</svg>''',
svgcap='VO alone drifts, so the end of a loop doesn’t meet the start. Place recognition detects the revisit and adds a loop constraint, and pose-graph optimisation spreads the correction along the whole path.',
videos=['BuRCJ2fegcc', 'lIdmbrRahk8'],
body=r'''
<div class="sub"><h3>1. Direct vs indirect (feature-based) methods</h3>
<p>All VO so far is <b>indirect</b>: extract features, match them, then minimise geometric <b>reprojection</b> error [[p19]]. <b>Direct</b> methods skip matching and minimise <b>photometric error</b> on pixel intensities [[p22]]:</p>
\[R^*, t^* = \arg\min_{R,t}\sum_i \big(\mathcal I_{k-1}(x^i_{k-1}) - \mathcal I_k(\pi(K(Rp_i + t)))\big)^2\]
<p>Optimising the points \(p_i\) as well gives a dense BA-style objective [[p23]], as in DTAM (dense tracking and mapping) [[p24]].</p>
<div class="tw"><table><tr><th>Direct</th><th>Feature-based</th></tr>
<tr><td>minimise photometric error</td><td>minimise geometric reprojection error</td></tr>
<tr><td>use pixel intensities</td><td>use extracted feature locations</td></tr>
<tr><td>correspondence implicit through projection</td><td>correspondence from descriptor matching</td></tr>
<tr><td>semi-dense or dense maps</td><td>usually sparse landmark maps</td></tr>
<tr><td>high sub-pixel precision</td><td>larger convergence basin</td></tr>
<tr><td>sensitive to illumination and camera modelling</td><td>more tolerant of photometric changes</td></tr>
<tr><td>needs a good initial guess</td><td>better for large motions and relocalisation</td></tr></table></div>
<p class="note">Comparison from [[p25]]. Grid [[p36]]: indirect + sparse = PTAM, ORB-SLAM, libviso; indirect + dense = dense optical flow; direct + sparse = <b>DSO</b>; direct + dense = <b>DTAM</b>. LSD-SLAM is semi-dense and direct [[p38]].</p></div>

<div class="sub"><h3>2. Visual–inertial odometry</h3>
<p>An IMU combines a gyroscope (angular velocity) and an accelerometer (linear acceleration); in robots they are usually MEMS [[p27]] [[p28]]. <b>Why add an IMU?</b> Monocular scale is ambiguous, and vision fails in low texture, under- or over-exposure and motion blur [[p29]]. <b>Why not the IMU alone?</b> Double-integrating noisy acceleration drifts fast, and a constant bias makes the position error grow <b>quadratically</b>, ½·b·t² [[p30]].</p>
<div class="ex"><b>Worked example.</b> Accelerometer bias 0.05 m/s²: after 10 s the position error is ½·0.05·10² = <b>2.5 m</b>; after 60 s it is <b>90 m</b>.</div>
<div class="widget" data-w="imu"></div>
<div class="tw"><table><tr><th>Camera</th><th>IMU</th></tr>
<tr><td>exteroceptive (measures the world)</td><td>proprioceptive (measures itself)</td></tr>
<tr><td>sensitive to blur, HDR, texture</td><td>insensitive to blur, HDR, texture</td></tr>
<tr><td>drift bounded when re-observing the same scene</td><td>drift unbounded regardless of environment</td></tr>
<tr><td>precise in slow motion</td><td>less precise in slow motion (low SNR)</td></tr>
<tr><td>~100 Hz</td><td>1,000–10,000 Hz; predicts where features will move</td></tr>
<tr><td>mono: scale ambiguous</td><td>gives metric scale (gravity, acceleration)</td></tr></table></div>
<p class="note">Comparison from [[p31]].</p>
<p>Measurement model [[p32]]: \(\tilde a_B = R_{BW}(a_W - g) + b_A + n_A\), \(\tilde\omega_B = \omega_B + b_G + n_G\). The noise is white Gaussian; the biases drift slowly as a random walk, change with temperature and pressure, differ at each power-on and <b>can be estimated</b> [[p33]]. VIO is nonlinear least squares over states (position, velocity, orientation), landmarks <b>and biases</b> [[p34]] [[p35]]:</p>
\[\sum_k\|f(x_{k-1},u) - x_k\|^2_{\Lambda_k} + \sum_k\sum_i\|\pi(x_k, L_i) - z_k^i\|^2_{\Sigma_k^i}\]
<p>That is IMU residuals plus reprojection (BA) residuals.</p></div>

<div class="sub"><h3>3. Evaluating VO: ATE and RPE</h3>
<p><b>Absolute Trajectory Error</b> [[p40]] [[p41]]: align the estimate to ground truth with a similarity transform \((R, T, s)\) (least squares over positions), then \(\text{RMSE} = \sqrt{\tfrac1n\sum_k\|\hat C_k - sRC_k - T\|^2}\). Pros: one intuitive number in metres that captures accumulated drift and global accuracy. Cons: it needs spatial and temporal alignment; one RMSE hides <i>where and when</i> errors happened; it is sensitive to outliers; it mixes translation drift with rotation-induced error; and it can mislead for monocular VO when the scale is fitted over the whole trajectory. <b>A single early rotation error gives a huge ATE</b> even if everything after is perfect [[p42]].</p>
<p><b>Relative Pose Error</b> [[p43]] compares frame-to-frame motion: \(E_i = (\hat T_{i-1}^{-1}\hat T_i)^{-1}(T_{i-1}^{-1}T_i)\), \(\text{RPE}_{trans} = \sqrt{\tfrac{1}{N-1}\sum_i\|\text{trans}(E_i)\|^2}\) (and similarly for rotation). It measures local accuracy and drift rate.</p>
<p><b>Mean or median?</b> [[p44]] Averages are skewed by outliers, so report the median too, or a boxplot (median, 25th/75th percentiles, whiskers at 5th/95th, dots for outliers).</p>
<div class="ex"><b>Worked example.</b> Aligned position errors 0.3, 0.4, 0.0, 1.2 m. RMSE = √((0.09+0.16+0+1.44)/4) = √0.4225 = <b>0.65 m</b>; mean 0.475 m; median 0.35 m. The single 1.2 m error dominates the RMSE.</div>
<div class="widget" data-w="ate"></div></div>

<div class="sub"><h3>4. From VO to visual SLAM</h3>
<p>VO is incremental and locally consistent; SLAM keeps a map so that it can recognise revisits and enforce <b>global</b> consistency through <b>loop closure</b> [[p48]]. The history [[p52]]–[[p63]] runs as follows:</p>
<ul><li>Sonar/lidar SLAM built 2-D occupancy grids or landmark maps. Cameras are rich (geometry, texture, semantics), cheap, compact and passive; depth cameras (Kinect) added RGB-D SLAM.</li>
<li><b>MonoSLAM</b> (Davison 2007): the first real-time monocular SLAM, a very sparse map, EKF-based.</li>
<li><b>KinectFusion</b> (2011): dense RGB-D SLAM with a TSDF map.</li>
<li>Event-camera SLAM for HDR and high speed.</li>
<li><b>Semantic SLAM</b>: SemanticFusion (CNN labels fused into a dense map), SLAM++ (objects as landmarks), QuadricSLAM (dual quadrics from detections), 3D scene graphs for large scale.</li></ul>
<p>For more depth, see the TartanSLAM series (<a href="https://theairlab.org/tartanslamseries/" target="_blank" rel="noopener">1</a>, <a href="https://theairlab.org/tartanslamseries2/" target="_blank" rel="noopener">2</a>) listed in the lecture folder. It is optional.</p>
<div class="exam"><b>Exam angle.</b> No practice-exam question used this week, but scenario questions may. “A drone in a dark tunnel: which sensor and why?” (VIO: IMU through blur and darkness, camera bounds drift.) “Which metric shows local drift vs global error?” (RPE vs ATE.) “Direct or feature-based for large, fast motions?” (Feature-based: larger convergence basin.)</div></div>
''',
paper=dict(title='ORB-SLAM3 (Campos et al., IEEE T-RO 2021)', sixty=r'''
<p><b>Problem.</b> One system for visual, visual–inertial and <b>multi-map</b> SLAM with monocular, stereo and RGB-D cameras (pinhole or fisheye). VO uses only the last few seconds; ORB-SLAM3 <b>reuses all previous information</b>, including co-visible keyframes far apart in time or from earlier sessions [[P:p2]].</p>
<p><b>Components</b> (Fig. 1). The <b>Atlas</b> holds an active map plus non-active maps and one DBoW2 keyframe database. <b>Tracking</b> computes each frame’s pose against the active map by minimising reprojection error, decides keyframes, and relocalises in all maps when lost. <b>Local mapping</b> adds or culls keyframes and points and runs local (visual–inertial) BA; it also initialises the IMU by MAP estimation. <b>Loop & map merging</b> runs place recognition at keyframe rate: a match in the same map triggers loop correction (pose-graph / essential-graph optimisation, then full BA); a match in another map merges the two.</p>
<p><b>Headline numbers.</b> 2–10× more accurate than previous VI systems. Stereo-inertial: <b>3.5 cm</b> average on EuRoC (drone) and <b>9 mm</b> in TUM-VI room sequences. Raw DBoW2 place recognition has 50–80% precision/recall; with consistency checks it reaches 100% precision at 30–40% recall, which motivated the new, higher-recall method.</p>
<p><b>How to read it.</b> Accuracy is reported as ATE RMSE after alignment (Fig. 4 colours RMS ATE over 10 runs per EuRoC sequence). Lower is better; the spread across runs shows robustness.</p>''',
),
tut=r'''
<p><b>1. Main components.</b> Tracking (real-time pose per frame, keyframe decisions, relocalisation), local mapping (insert or cull keyframes and points, local BA, IMU initialisation and refinement), loop closing and map merging (place recognition with DBoW2, loop correction, merging, full BA in a separate thread), and the Atlas (multi-map store with a shared keyframe database).</p>
<p><b>2. Why keyframes?</b> Consecutive frames are highly redundant. Optimising every frame wastes compute and adds little parallax. Keyframes give well-spread, informative views, bounded map size and real-time BA. Trade-off: too sparse loses tracking and coverage; too dense costs compute. ORB-SLAM inserts generously and culls redundant keyframes later.</p>
<p><b>3. Where optimisation is used.</b> Tracking optimises the current pose only (motion-only BA). <b>Local BA</b> optimises the keyframes near the current one plus their points, for accuracy at real-time cost. <b>Pose-graph (essential-graph) optimisation</b> spreads a loop correction cheaply over the whole map. <b>Global (full) BA</b> refines all keyframes and points after a loop for the final MAP estimate (in VI mode only if the number of keyframes is below a threshold).</p>
<p><b>4. Relocalisation vs loop closure vs map merging.</b> Relocalisation: tracking is lost, so find the current frame’s pose in an existing map with no prior pose; this resumes tracking. Loop closure: place recognition matches a keyframe in the <b>same</b> active map; this corrects accumulated drift. Map merging: the match is in a <b>different</b> (non-active) map, e.g. after a new map was started when tracking failed; the maps are fused so information is reused across sessions.</p>''',
quiz=[
 ('An estimator makes one wrong rotation early in a long run but is otherwise perfect. Which metric exaggerates this most?', ['RPE (translation)', 'ATE', 'Median RPE', 'Frame rate'], 1, 'ATE compares absolute positions, so an early rotation error displaces every later pose [[p42]].'),
 ('Why can VIO recover metric scale with a single camera?', ['The IMU measures depth directly', 'The accelerometer measures metric acceleration (including gravity), which fixes the scale', 'IMUs have no drift', 'Because the camera runs at 100 Hz'], 1, 'Accelerations are in m/s², so integrating them ties the visual trajectory to metres.'),
 ('Which statement about direct methods is correct?', ['They need descriptor matching', 'They minimise photometric error and need a good initial guess', 'They are insensitive to illumination changes', 'They always produce sparse maps'], 1, 'From the comparison on [[p25]].'),
],
)
