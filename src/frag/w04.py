T = dict(
id='w04', week=4, tab='Epipolar & RANSAC', title='Epipolar geometry, F, E and RANSAC',
lead='Two views of a static scene constrain each other: a point in one image must lie on a line in the other. That line rejects bad matches (RANSAC) and, with known K, yields rotation and translation direction.',
docs=[dict(path='notes/Week04.pdf', title='Week 4 lecture: Epipolar geometry', pages=90),
      dict(path='notes/papers/VO_Part_I.pdf', title='VO Part I (Scaramuzza & Fraundorfer, 2011)', pages=13)],
prac=('week-4.ipynb', 'matches SIFT/ORB on KITTI, compares RANSAC vs USAC-MAGSAC fundamental matrices, draws epipolar lines, then uses findEssentialMat + recoverPose and chains frame-to-frame motion.'),
eli5=[
 ('The epipolar line', 'You see a firefly in your left eye but not how far away it is: it could be anywhere along a ray. Your right eye sees that ray as a <i>line</i>, and the firefly must be somewhere on it.', 'computeCorrespondEpilines draws exactly these lines on KITTI frames.'),
 ('F and E', 'F is the rulebook connecting pixel positions in two uncalibrated photos. E is the same rulebook once you know each camera’s ruler K, and it contains the rotation and the direction of travel.', None),
 ('RANSAC', 'To find the true trend in a messy crowd, ask small random groups to propose a rule; the rule most people agree with wins. Liars (outliers) rarely all agree.', 'compare how many matches survive cv2.RANSAC vs USAC_MAGSAC.'),
 ('Scale ambiguity', 'A photo of a toy car 1 m away looks identical to a real car 10 m away. From two images alone you know the direction you moved, not how far.', 'in Week 4 the scale is borrowed from ground truth; Week 5 recovers it from stereo.'),
],
svg='''<svg class="dg" viewBox="0 0 520 220" role="img" aria-label="Epipolar geometry: two camera centres, world point X, epipolar plane, epipoles and epipolar line">
<path class="sk" d="M85 175 L435 175 L260 30 Z" style="opacity:.55"/>
<circle class="fi" cx="85" cy="175" r="5"/><circle class="fi" cx="435" cy="175" r="5"/><circle class="fa" cx="260" cy="30" r="6"/>
<text x="62" y="200">C</text><text x="430" y="200">C′</text><text x="270" y="28">X (unknown depth)</text>
<path class="ln" d="M85 175 L435 175"/><text x="225" y="192" class="sm">baseline</text>
<path class="ln" d="M60 120 L170 95 L175 160 L65 185 Z" style="stroke:var(--muted)"/><path class="ln" d="M350 95 L460 120 L455 185 L345 160 Z" style="stroke:var(--muted)"/>
<path class="ac" d="M85 175 L260 30"/><path class="ln dash" d="M85 175 L330 -10" style="stroke:var(--muted)"/>
<circle class="fe" cx="133" cy="135" r="4"/><text x="102" y="128">x</text>
<path class="ev" d="M352 163 L403 103"/><text x="410" y="100">l′ = F x</text>
<circle class="fi" cx="355" cy="170" r="3"/><circle class="fi" cx="165" cy="170" r="3"/><text x="150" y="160" class="sm">e</text><text x="358" y="160" class="sm">e′</text>
<text x="10" y="18" class="sm">x′ must lie on l′, whatever the depth of X:  x′ᵀ F x = 0</text>
</svg>''',
svgcap='The epipolar plane through X, C and C′ cuts each image in an epipolar line. Every epipolar line passes through the epipole (where the baseline pierces the image).',
videos=['auhpPoAqprk', '9D5rrtCC_E0'],
body=r'''
<div class="sub"><h3>1. Epipolar geometry</h3>
<p>Two cameras (or one moving camera) view a static scene, with unknown R, t and even unknown K [[p14]]. A pixel x in image 1 back-projects to a ray. That ray projects into image 2 as a <b>line</b> l′, and the match x′ must lie on it. This holds whatever the point’s depth [[p23]] [[p25]].</p>
<ul><li><b>Epipolar plane</b>: the plane through X, C and C′. <b>Epipolar lines</b>: where that plane cuts the images [[p27]].</li>
<li><b>Epipole</b>: the image of the other camera’s centre, which is where the baseline meets the image plane. All epipolar lines pass through it.</li>
<li>Ideal (rectified) stereo [[p28]]: epipolar lines are horizontal and parallel and the epipoles are at infinity, so the correspondence search is a 1-D search along the row.</li></ul></div>

<div class="sub"><h3>2. The fundamental matrix</h3>
<p>The epipolar line of x is \(l' = Fx\), and x′ on l′ means \(x'^\top l' = 0\), so <b>\(x'^\top F x = 0\)</b> for every correct correspondence [[p32]]. F is 3×3 and rank 2, with 7 degrees of freedom.</p>
<p><b>8-point algorithm</b> [[p33]] [[p34]]: each correspondence gives one linear equation in the 9 entries of F, \(A\mathbf f = 0\). Fix \(\|\mathbf f\|=1\) (scale), take the SVD of A, use the last row of \(V^\top\), reshape it to 3×3, <b>force rank 2</b> with a second SVD (zero the smallest singular value), and denormalise: \(F = T'^\top\tilde F T\) (Hartley normalisation). The OpenCV function is <code>findFundamentalMat</code>; slide p33 says findHomography, which is a slip.</p>
<div class="ex"><b>Worked example.</b> Rectified pair, pure x-translation: \(F = \begin{bmatrix}0&0&0\\0&0&-1\\0&1&0\end{bmatrix}\). For x = (100, 50, 1), \(l' = Fx = (0, -1, 50)\), i.e. the line \(-y + 50 = 0\), so y = 50, the same row. The candidate x′ = (80, 50, 1) gives \(x'^\top l' = -50 + 50 = 0\) ✓.</div>
<p><b>When F fails</b> [[p35]]. True degeneracies: <b>pure rotation</b> (no translation, so no epipoles), a <b>planar scene</b> (a homography explains the data and F is not unique), collinear or clustered points. Near-degenerate (poorly conditioned): very small baseline, distant points (weak parallax), forward motion near the epipole, dynamic scenes, lens distortion or rolling shutter. Practical checks [[p36]]: inlier count, spatial spread, H-vs-F comparison, Sampson error, cheirality, resampling stability, temporal consistency. OpenCV returns a matrix even for degenerate data.</p></div>

<div class="sub"><h3>3. RANSAC</h3>
<p>You need correct matches to estimate F, but you need F to find the correct matches. RANSAC breaks the loop [[p42]] [[p43]]:</p>
<ol><li>fit the model to a random <b>minimal</b> sample (8 pairs for F, 5 for E, 2 points for a line);</li><li>compute every data point’s error against that model;</li><li>points with error &lt; threshold are inliers;</li><li>repeat k times;</li><li>keep the model with the <b>largest inlier set</b> (consensus) [[p54]].</li></ol>
<p>It works because <b>some random minimal samples contain only inliers</b>, and those produce models supported by many points (practice Q12).</p>
<p><b>How many iterations?</b> [[p55]] [[p56]] With inlier ratio w, sample size n and desired success probability p:</p>
\[k = \frac{\log(1-p)}{\log(1-w^n)}\]
<div class="ex"><b>Worked example.</b> w = 0.9, n = 8, p = 0.999 → \(w^8 = 0.430\), k = 12.3 → <b>13</b> (slide p56). w = 0.75 → k = 65.5 (the slide says 65; rounding up gives 66). With w = 0.5, p = 0.99: n = 8 → 1177, n = 5 → 146, n = 3 → 35. The all-inlier probability \(w^n\) shrinks <b>exponentially</b> with n, which is why minimal solvers matter (practice Q21).</div>
<div class="widget" data-w="ransac"></div>
<p><b>The threshold</b> (practice Q13): with the model and residuals fixed, raising the threshold from 2 to 5 px keeps every old inlier and may turn some outliers into inliers. A looser threshold admits more noise, so refinement does not necessarily get better.</p>
<p><b>Variants</b> [[p57]]: PROSAC (sample high-ranked matches first), LO-RANSAC (locally re-fit promising models), preemptive verification, GC-RANSAC (spatially coherent labels), MAGSAC++ (marginalise over noise scales, so it is less threshold-sensitive), USAC (a modular framework).</p></div>

<div class="sub"><h3>4. The essential matrix and motion from 2D–2D</h3>
<p>With K known, normalise the points: \(\hat x = K^{-1}x\). Then <b>\(\hat x'^\top E\,\hat x = 0\)</b> [[p62]], with <b>\(E = K'^\top F K\)</b> [[p64]]. E can be estimated from ≥ <b>5</b> points (<code>findEssentialMat</code>) [[p63]]. For cameras \([I|0]\) and \([R|t]\), <b>\(E = [t]_\times R\)</b>, where \([t]_\times = \begin{bmatrix}0&-t_z&t_y\\t_z&0&-t_x\\-t_y&t_x&0\end{bmatrix}\) [[p66]]. E has 5 DOF: 3 for rotation and 2 for the translation direction.</p>
<p><b>Decomposition gives 4 solutions</b> [[p68]]: \([R_1,t],[R_1,-t],[R_2,t],[R_2,-t]\), where \(R_1, R_2\) differ by a 180° twist about the baseline. Triangulate the points; only one solution puts them <b>in front of both cameras</b> (positive depth, cheirality). <code>recoverPose</code> does this in one go [[p69]].</p>
<p><b>Scale ambiguity</b> [[p72]]: R is correct, but t is known only up to scale (direction, not distance). Scaling the scene and the translation together leaves every image identical (Week 5 shows the algebra).</p>
<p>How 2D–2D is used [[p73]] [[p76]]: to <b>initialise monocular VO</b> (R, t from the first two frames, triangulate a map with arbitrary scale) and then switch to 3D–2D (PnP). AR (PTAM, Oculus) doesn’t need metric scale. With known 3D points (stereo or depth) the scale can be recovered by minimising reprojection error [[p78]]:</p>
\[s^* = \arg\min_s \sum_i \big\|x_i^{obs} - \pi\big(K(R p_i + s\,t)\big)\big\|^2\]
<div class="tw"><table><tr><th>Problem structure</th><th>What we do</th><th>Typical tool</th></tr><tr><td>exact, invertible equations</td><td>solve</td><td>rearrange, linear solve</td></tr><tr><td>noisy linear</td><td>minimise linear residuals</td><td>QR, SVD</td></tr><tr><td>noisy nonlinear</td><td>iteratively minimise residuals</td><td>Gauss–Newton, LM</td></tr><tr><td>outliers present</td><td>limit or reject their influence</td><td>robust loss, RANSAC</td></tr></table></div>
<p class="note">Table from [[p80]].</p>
<div class="exam"><b>Exam angle.</b> Q11 (the match must lie on the epipolar line), Q12 and Q13 (RANSAC logic), Q14 and Q17 (monocular translation needs a metric scale from a known distance or a metric sensor), Q16 (largest consensus). Expect a k-iterations calculation and “why 4 solutions / how to pick one”.</div></div>
''',
paper=dict(title='Visual Odometry, Part I (Scaramuzza & Fraundorfer, IEEE RAM 2011)', sixty=r'''
<p><b>Problem.</b> VO estimates a vehicle’s egomotion from cameras alone, incrementally, like wheel odometry but immune to wheel slip. It needs enough light, a static textured scene and frame overlap. Typical relative position error is 0.1–2% [[P:p1]].</p>
<p><b>Key formulation</b> [[P:p5]]: \(T_k = \begin{bmatrix}R_{k,k-1}&t_{k,k-1}\\0&1\end{bmatrix}\) is the <i>relative</i> motion between frames k−1 and k. \(C_k\) is the <i>pose</i> relative to frame 0, with <b>\(C_n = C_{n-1}T_n\)</b>. Feature-based methods are more accurate and cheaper than appearance-based ones.</p>
<p><b>Algorithm 1 (2D–2D)</b> [[P:p9]]: capture \(I_k\) → extract and match features → compute E → decompose into \(R_k, t_k\) → compute the <b>relative scale</b> and rescale \(t_k\) → \(C_k = C_{k-1}T_k\) → repeat. Relative scale \(r = \frac{\|X_{k-1,i} - X_{k-1,j}\|}{\|X_{k,i} - X_{k,j}\|}\) from triangulated point pairs (median for robustness); it needs features tracked over at least 3 frames.</p>
<p><b>Limitation.</b> Errors in every \(T_k\) are chained, so the path <b>drifts</b>. Windowed bundle adjustment reduced the final error by a factor of 2–5 over 10 km [[P:p4]]. VO keeps only <i>local</i> consistency; SLAM aims for global consistency.</p>''',
),
tut=r'''
<p><b>1. Relative motion vs pose.</b> \(T_k\) is the rigid transform between consecutive frames (k−1 → k); \(C_k\) is the camera pose relative to the first frame, \(C_k = C_{k-1}T_k = C_0T_1T_2\cdots T_k\). Every \(T_k\) carries a small error, and later poses inherit all earlier errors. A small <i>rotation</i> error also rotates every later translation, so position error grows faster than linearly with distance: <b>drift</b>.</p>
<p><b>2. From correspondences to motion.</b> Each calibrated correspondence gives one scalar equation \(\hat x'^\top E\hat x = 0\), linear in E’s entries (5 is the minimum with the nonlinear constraints of E, 8 with the linear method). From E you recover R and the translation <b>direction</b>; the <b>magnitude</b> of t stays unknown.</p>
<p><b>3. RANSAC in Algorithm 1.</b> It wraps step 3 (computing E). <i>Model</i>: E (equivalently R and t̂). <i>Data sampled</i>: minimal sets of 5 (or 8) correspondences. <i>Inlier test</i>: point-to-epipolar-line distance (Sampson error) below a threshold. <i>Why not least squares on all matches?</i> Squared error lets a few gross outliers (wrong matches) pull the solution arbitrarily far; least squares assumes small Gaussian noise.</p>
<p><b>4. Pose ambiguity and scale.</b> E decomposes into 4 (R, t) pairs. Triangulate a point with each; only the physically valid one gives <b>positive depth in both cameras</b>. Even then |t| is unknown, because scaling the scene and t by the same factor gives identical images. Metric scale needs extra information: a stereo baseline, a depth sensor, an IMU, a known object size or camera height, or wheel odometry.</p>''',
quiz=[
 ('Where do all epipolar lines in an image intersect?', ['At the principal point', 'At the epipole', 'At the image centre', 'They never intersect'], 1, 'Every epipolar plane contains the baseline, so every epipolar line passes through the epipole (the baseline’s intersection with the image plane).'),
 ('RANSAC with w = 0.5, p = 0.99. How many iterations for the 8-point F vs a 3-point solver?', ['1177 vs 35', '35 vs 1177', '146 vs 17', '100 vs 30'], 0, 'k = log(0.01)/log(1−0.5ⁿ): n = 8 → 1176.6 → 1177; n = 3 → 34.5 → 35.'),
 ('Decomposing E gives four candidate (R, t). How is the correct one chosen?', ['Pick the one with the smallest rotation', 'Triangulate points and keep the solution with points in front of both cameras', 'Pick the one with a positive t_z', 'All four are equally valid'], 1, 'Cheirality: only one solution gives positive depth in both views [[p68]].'),
],
)
