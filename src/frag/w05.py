T = dict(
id='w05', week=5, tab='Visual odometry', title='Visual odometry: scale, PnP, 3D–3D and keyframes',
lead='Turning correspondences into metric camera motion: recovering scale from stereo, solving Perspective-n-Point inside RANSAC, aligning 3D point sets, chaining transforms, and choosing keyframes.',
docs=[dict(path='notes/Week05.pdf', title='Week 5 lecture: Visual odometry', pages=98),
      dict(path='notes/papers/VO_Part_I.pdf', title='VO Part I (Scaramuzza & Fraundorfer, 2011)', pages=13),
      dict(path='notes/papers/VO_Part_II.pdf', title='VO Part II (Fraundorfer & Scaramuzza, 2012)', pages=13)],
prac=('week-5-2d2d.ipynb + week-5-pnp.ipynb', '2D–2D: E + recoverPose, then scipy <code>least_squares</code> finds the scale s from stereo 3D points. PnP: stereo SGBM depth → 3D points → <code>solvePnPRansac</code> (AP3P) → <code>solvePnPRefineLM</code>.'),
eli5=[
 ('Scale from stereo', 'One eye tells you which way you walked; two eyes a known distance apart tell you how far. Once a few 3D points are known in metres, the walk gets metres too.', 'least_squares tunes a single number s until the stereo points reproject onto the next image.'),
 ('PnP', 'You know where three or more landmarks are on a map and see them in your photo. Where were you standing? Three landmarks give at most 4 answers; a fourth picks one.', 'solvePnPRansac with SOLVEPNP_AP3P proposes poses; solvePnPRefineLM polishes the winner on its inliers.'),
 ('Minimal solver vs refinement', 'A quick sketch from 3 points finds the right neighbourhood despite liars in the crowd; then everyone who agrees helps sharpen the final drawing.', None),
 ('Keyframes', 'If you stand still and measure your step 30 times a second, tiny errors add up into a wander. Measure only against a reference snapshot, and take a new snapshot after you have really moved.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 150" role="img" aria-label="Typical pipeline: observations with outliers, minimal solver plus RANSAC, inliers and initial guess, nonlinear refinement, solution">
<rect class="bx" x="8" y="45" width="100" height="56"/><text x="16" y="68">matches</text><text x="16" y="88" class="sm">many, with outliers</text>
<rect class="sk" x="132" y="45" width="112" height="56"/><text x="140" y="68">minimal solver</text><text x="140" y="88" class="sm">+ RANSAC (P3P: 3)</text>
<rect class="bx" x="268" y="45" width="100" height="56"/><text x="276" y="68">inliers +</text><text x="276" y="88" class="sm">initial guess</text>
<rect class="sk" x="392" y="45" width="120" height="56"/><text x="400" y="68">refinement</text><text x="400" y="88" class="sm">LM / GN on inliers</text>
<path class="ac" d="M108 73 H128 M244 73 H264 M368 73 H388"/>
<text x="132" y="122" class="sm">robust, rough</text><text x="392" y="122" class="sm">accurate, needs a good start,</text><text x="392" y="138" class="sm">fragile to outliers</text>
<text x="8" y="28">The pattern recurs: F (8 pts), E (5), P3P (3), line (2)</text>
</svg>''',
svgcap='The pattern behind almost every geometric estimator in the unit [[p31]]: a robust minimal solver inside RANSAC, then nonlinear least squares over the inliers.',
videos=['xdlLXEyCoJY', 'H_1OtbMD-sE'],
body=r'''
<div class="sub"><h3>1. Why scale is ambiguous, and how to recover it</h3>
<p>From E we get R and a <b>unit</b> translation direction \(\hat t\); the true \(t = s\hat t\) has unknown \(s&gt;0\) [[p12]]. Proof [[p14]]: project a point, \(\lambda x = K(RX + t)\). Scale both the world and the translation by s: \(K(R\,sX + s\,t) = s\,K(RX+t)\). Dividing by the third coordinate cancels s, so <b>the pixels don’t change</b>.</p>
<p><b>Fix it with known 3D points</b> (stereo or depth) [[p15]] [[p17]]: \(s^* = \arg\min_s\sum_i \|x_i^{obs} - \pi(K(Rp_i + s t))\|^2\), a 1-parameter nonlinear least-squares problem (reprojection error).</p>
<div class="tw"><table><tr><th>Template</th><th>Scale recovery</th><th>PnP</th><th>3D–3D</th></tr>
<tr><td>Parameters</td><td>s</td><td>R, t</td><td>R, t</td></tr>
<tr><td>Prediction</td><td>\(\pi(K(Rp_i + st))\)</td><td>\(\pi(K(Rp_i + t))\)</td><td>\(Rx_{t-1}^i + t\)</td></tr>
<tr><td>Residual</td><td>reprojection error</td><td>reprojection error</td><td>3D Euclidean distance</td></tr>
<tr><td>Objective</td><td colspan="3">sum of squared residuals</td></tr></table></div>
<p class="note">This optimisation template comes from [[p19]], and it comes back in Week 6 for pose graphs and bundle adjustment.</p></div>

<div class="sub"><h3>2. 3D–2D: the Perspective-n-Point problem</h3>
<p>The 3D points are known (stereo, or a map); the camera pose [R, t] is unknown [[p22]]. How many points do you need [[p24]] [[p25]] [[p26]]?</p>
<ul><li><b>1 point</b>: infinitely many solutions (the camera can be anywhere on the ray).</li>
<li><b>2 points</b>: still infinite, but constrained (the angle θ between the rays must be kept).</li>
<li><b>3 points</b>: <b>up to 4 solutions</b>, and a 4th point disambiguates. This is <b>P3P</b> (OpenCV <code>SOLVEPNP_AP3P</code>).</li>
<li><b>≥ 4 points</b>: PnP, e.g. EPnP, an O(n) non-iterative method [[p27]].</li></ul>
<p>PnP minimises the reprojection error, \(\arg\min_{R,t}\sum_i\|x_i - \pi(K(Rp_i + t))\|^2\) [[p28]].</p>
<div class="tw"><table><tr><th>Method</th><th>Role</th><th>Minimises reprojection error directly?</th><th>Outliers</th></tr>
<tr><td>P3P / AP3P</td><td>minimal hypothesis generator inside RANSAC (3 points mathematically; OpenCV uses 4)</td><td>no: solves exact constraints; reprojection error only <i>scores</i> hypotheses</td><td>fragile alone, robust inside RANSAC</td></tr>
<tr><td>EPnP</td><td>fast all-point initial estimate (&gt;4)</td><td>no (algebraic)</td><td>fragile: treats wrong matches as valid</td></tr>
<tr><td>Iterative LM / GN</td><td>refines an initial pose with many points</td><td><b>yes</b></td><td>fragile with plain least squares; feed it RANSAC inliers, optionally a robust loss</td></tr></table></div>
<p class="note">Comparison from [[p32]]. OpenCV functions [[p33]]: <code>solvePnP</code>, <code>solvePnPRansac</code>, <code>solvePnPRefineLM</code>, <code>solvePnPRefineVVS</code>.</p>
<p><b>Practical pipeline</b> [[p34]]: RANSAC with P3P to reject outliers and get an initial guess, then iterative refinement on the inliers only. A minimal-set pose is noisy because three noisy points fix it exactly; refinement averages the noise over all inliers (practice Q18, Q20).</p>
<div class="ex"><b>Worked example (practice Q19).</b> Predicted pixel (100, 80), observed (97, 84). Residual = observed − predicted = <b>(−3, 4)</b>, norm \(\sqrt{9+16} = 5\) px &lt; 6 px → <b>inlier</b>. Watch the sign convention, and remember the error is the norm, not the squared norm (25).</div>
<div class="widget" data-w="reproj"></div></div>

<div class="sub"><h3>3. 3D–3D: aligning point clouds (Arun et al. 1987)</h3>
<p>With 3D points in both frames (stereo or RGB-D) [[p39]], \(x_t^i = R x_{t-1}^i + t\). Minimise \(\sum_i\|x_t^i - (Rx_{t-1}^i + t)\|^2\) [[p53]]; with noise the sum is never exactly 0. Decouple rotation from translation [[p54]]:</p>
<ol><li>compute the centroids \(\bar x_t, \bar x_{t-1}\) [[p55]];</li><li>subtract them from each set [[p56]];</li>
<li>\(H = \sum_i \bar x_{t-1}^i\,\bar x_t^{i\top}\) (cross-covariance, a sum of outer products), \(USV^\top = \mathrm{svd}(H)\), <b>\(R = VU^\top\)</b> (if det R = −1 you have a reflection, a degenerate case) [[p62]];</li>
<li><b>\(t = \bar x_t - R\,\bar x_{t-1}\)</b> [[p67]].</li></ol>
<p>The camera motion is the <b>inverse</b> of this point-alignment transform [[p69]]. Accuracy is limited because stereo depth error is large and anisotropic (a diamond-shaped uncertainty region), so it is better to minimise image-level quantities (reprojection error) as 2D–2D and 3D–2D methods do [[p70]]. VO Part I says the same: 3D–2D beats 3D–3D.</p>
<p class="note">The check script confirms this recipe recovers a 0.7 rad rotation and t = (1, 2, 3) exactly on noise-free points.</p></div>

<div class="sub"><h3>4. Chaining transforms (frame conventions)</h3>
<p>Write \({}^{A}T_{B}\) for the transform that maps coordinates in frame B into frame A. Then \({}^{A}T_{C} = {}^{A}T_{B}\,{}^{B}T_{C}\): the inner indices cancel (practice Q15). Also \({}^{B}T_{A} = ({}^{A}T_{B})^{-1}\). A VO trajectory is a chain: \(C_k = C_{k-1}T_k\).</p>
<div class="ex"><b>Worked example (2-D).</b> \({}^{A}T_{B}\) = rotate 90°, then translate (2, 0). \({}^{B}T_{C}\) = translate (1, 0). The origin of C is at (1, 0) in B; rotating by 90° gives (0, 1), and translating gives <b>(2, 1)</b> in A.</div></div>

<div class="sub"><h3>5. Keyframes</h3>
<p>Frame-to-frame estimates are never exact. A static camera tracked frame to frame drifts like a random walk [[p75]] [[p76]]. So estimate motion relative to the last <b>keyframe</b>, \({}^{K_i}T_{C_k}\) [[p77]]. Add a new keyframe [[p78]] when the camera has moved or rotated enough, when too many features are lost, or every N frames. Too few keyframes give a poor map; too many waste computation.</p>
<p>Monocular rule of thumb [[p80]]: add a keyframe when <b>keyframe distance / average depth &gt; 10–20%</b>. A small baseline relative to scene depth gives large triangulation uncertainty. Pure rotation has no baseline, so nothing can be triangulated.</p>
<p><b>PTAM case study</b> [[p87]] runs tracking and mapping in separate threads. Map initialisation: 1000 points, 5-point E + RANSAC, triangulate, BA, assume 10 cm of motion for scale, align the dominant plane to z = 0. Tracking: 3D–2D pose updates with a robust Tukey loss (Week 6). Mapping: triangulate new points from keyframes.</p>
<div class="exam"><b>Exam angle.</b> Five practice questions: Q15 (composition order), Q18 and Q20 (roles of the minimal solver, RANSAC and refinement), Q19 (residual arithmetic), Q21 (\(w^s\) falls exponentially). Scenario questions may ask you to design a stereo VO pipeline: features → stereo depth → PnP + RANSAC → LM refinement → keyframes → (Week 6) pose graph.</div></div>
''',
paper=dict(title='VO Part I §3D–2D and Part II (robustness, error propagation)', sixty=r'''
<p><b>3D–2D</b> (Part I, p.10 [[P:p10]]): more accurate than 3D–3D because it minimises image reprojection error rather than 3D position error. Minimal case P3P: <b>4 solutions</b>, disambiguated with extra points; it is the standard robust estimator with outliers. DLT works for n ≥ 6.</p>
<p><b>Outliers</b> (Part II, p.6 [[P2:p6]]): outlier removal is “the most delicate task in VO”. RANSAC iterations \(N = \frac{\log(1-p)}{\log(1-(1-\varepsilon)^s)}\) (ε = outlier fraction), often multiplied by 10 in practice. The final step re-estimates the model with <b>all inliers</b>.</p>
<p><b>Minimal or not?</b> (p.8 [[P2:p8]]) For speed, use the minimal set. With very noisy points, a non-minimal set averages the noise, finds more inliers and is more accurate.</p>
<p><b>Error propagation</b>: \(\Sigma_k = J_{C}\Sigma_{k-1}J_C^\top + J_T\Sigma_{k,k-1}J_T^\top\). Pose uncertainty <b>always grows</b> when concatenating, so keep each relative estimate’s uncertainty small.</p>''',
),
tut=r'''
<p><b>Minimal solvers and refinement.</b> RANSAC iterations grow exponentially with sample size, so the 3-point P3P keeps iterations low and gives many cheap hypotheses. But a pose fitted exactly to 3 noisy points absorbs all of their noise; refining with all inliers (iterative PnP, LM) averages that noise. In the practical, AP3P inside <code>solvePnPRansac</code> generates and scores hypotheses, and <code>solvePnPRefineLM</code> refines the best one.</p>
<p><b>Defining an inlier (PnP).</b> Model: the camera pose (R, t). Hypothesis data: 3 (or 4) 3D–2D correspondences. Inlier error: the reprojection distance in pixels between the observed feature and the projected 3D point. A larger threshold keeps more matches, including wrong ones and points with bad depth; a smaller one rejects good but noisy points. For E, the test is a point-to-<b>epipolar-line</b> distance (1-D: it tests consistency with a line); PnP tests the distance to a predicted <b>point</b> (2-D).</p>
<p><b>Reprojection error.</b> It is measured where the sensor actually measures (pixels), so it matches the noise model. In the 2D–2D practical only s is optimised (R and t̂ are fixed from E); iterative PnP refines all 6 DOF of the pose.</p>
<p><b>Stereo depth sensitivity.</b> \(\delta Z \approx Z^2\delta d/(fb)\): nearby points are accurate and distant points very uncertain. PnP uses the 3D points directly as fixed “truth”, so depth errors bias the pose. E uses only 2D image coordinates, so stereo depth enters only through the scale.</p>
<p><b>Outlier rejection.</b> Squared error gives an outlier influence that grows without bound, so a few wrong matches can drag the pose far away. RANSAC removes most of them first. It does <b>not</b> guarantee every retained match is correct: an outlier that happens to lie within the threshold survives, and the inlier set depends on the threshold and on luck.</p>
<p><b>Drift.</b> A small rotation error rotates every later step; translation-direction and scale errors accumulate along the path. Contributors: feature localisation noise, mismatches that survive, stereo depth error (PnP), the scale estimate (2D–2D) and degenerate geometry (low parallax).</p>''',
quiz=[
 ('Using the convention ᴬT_B maps B → A, which expression gives ᶜT_A?', ['ᴬT_B ᴮT_C', '(ᴬT_B ᴮT_C)⁻¹', 'ᴮT_C ᴬT_B', 'ᴬT_B + ᴮT_C'], 1, 'ᴬT_C = ᴬT_B ᴮT_C, and ᶜT_A is its inverse.'),
 ('Predicted (250, 120), observed (256, 112), threshold 8 px. Classification?', ['Residual (6, −8), 10 px, outlier', 'Residual (−6, 8), 100 px, outlier', 'Residual (6, −8), 10 px, inlier', 'Residual (6, −8), 2 px, inlier'], 0, '‖(6, −8)‖ = 10 px &gt; 8, so it is an outlier.'),
 ('Why is 3D–3D motion estimation from stereo usually less accurate than PnP?', ['It needs more points', 'Stereo 3D points have large, anisotropic depth errors, and 3D–3D minimises 3D distances instead of image errors', 'It cannot estimate rotation', 'It has no closed-form solution'], 1, 'Minimising image-level reprojection error matches the measurement noise better [[p70]].'),
],
)
