T = dict(
id='w03', week=3, tab='Cameras & stereo', title='Cameras: pinhole model, calibration and stereo',
lead='How a 3D point becomes a pixel, the intrinsic and extrinsic parameters, lenses, shutters, and how two cameras recover depth through disparity.',
docs=[dict(path='notes/Week03.pdf', title='Week 3 lecture: Cameras and how they see the world', pages=107)],
prac=('week-3.ipynb', 'explores KITTI’s P and K matrices, then computes disparity maps with OpenCV StereoBM and StereoSGBM and turns them into depth.'),
eli5=[
 ('The pinhole', 'A dark box with a tiny hole draws an upside-down picture of the world on the back wall. Far things look small because their rays come in at a shallow angle: x = f·X/Z.', None),
 ('Intrinsics K', 'K is the camera’s personal ruler: focal length in pixels and where the optical axis hits the sensor. It converts metres on the image plane into pixel numbers.', 'you print KITTI’s K and see f ≈ 7×10² px with the principal point near the image centre.'),
 ('Extrinsics R, t', 'Where the camera stands and which way it faces. Same camera, different pose, different photo.', None),
 ('Stereo = your two eyes', 'Close one eye, then the other: near things jump more than far things. That jump is disparity; depth = f·baseline / disparity.', 'StereoSGBM computes this jump for every pixel along each row.'),
 ('Baseline trade-off', 'Eyes further apart judge far distances better but struggle with things right in front of the nose.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 210" role="img" aria-label="Rectified stereo: point P seen by left and right cameras separated by baseline b; disparity uL minus uR gives depth Z equals f b over d">
<path class="ln" d="M60 170 H460" style="stroke:var(--line)"/>
<circle class="fi" cx="150" cy="170" r="5"/><circle class="fi" cx="330" cy="170" r="5"/>
<text x="118" y="195">C_L (left)</text><text x="300" y="195">C_R (right)</text>
<path class="ln" d="M110 140 H190 M290 140 H370"/><text x="196" y="144" class="sm">image planes (f)</text>
<circle class="fa" cx="250" cy="30" r="6"/><text x="262" y="30">P = (X, Y, Z)</text>
<path class="ac" d="M250 30 L150 170"/><path class="ac" d="M250 30 L330 170"/>
<circle class="fe" cx="171.4" cy="140" r="4"/><circle class="fe" cx="308.6" cy="140" r="4"/>
<text x="140" y="132" class="sm">u_L</text><text x="312" y="132" class="sm">u_R</text>
<path class="ev dash" d="M150 182 H330"/><text x="232" y="207" class="sm">baseline b</text>
<path class="ln dash" d="M250 30 V170" style="stroke:var(--muted)"/><text x="256" y="110" class="sm">Z</text>
<text x="380" y="70">d = u_L − u_R</text><text x="380" y="92">Z = f·b / d</text><text x="380" y="114" class="sm">X = Z·u_L / f</text><text x="380" y="132" class="sm">Y = Z·v_L / f</text>
</svg>''',
svgcap='Rectified stereo: similar triangles give Z = f·b/d (u measured from the principal point, f in pixels). A closer P makes a larger disparity d.',
videos=['ND2fa08vxkY', 'O7B2vCsTpC0'],
body=r'''
<div class="sub"><h3>1. The pinhole camera and central projection</h3>
<p>Similar triangles give \(x/f = X/Z\), so \(x = fX/Z,\ y = fY/Z\) [[p17]]. In homogeneous coordinates [[p21]] [[p22]]:</p>
\[\begin{bmatrix}\tilde x\\ \tilde y\\ \tilde z\end{bmatrix} = \begin{bmatrix} f&0&0&0\\0&f&0&0\\0&0&1&0\end{bmatrix}\begin{bmatrix}X\\Y\\Z\\1\end{bmatrix} = \begin{bmatrix}fX\\fY\\Z\end{bmatrix} \Rightarrow (x,y) = (fX/Z,\ fY/Z)\]
<p>To get a Cartesian point, <b>divide by the third element</b>.</p>
<p><b>Pixels</b> [[p25]]: \(u = x/\rho_u + u_0\), \(v = y/\rho_v + v_0\), where ρ is the pixel size and \((u_0,v_0)\) the principal point, with the origin at the top-left. Together these give the <b>intrinsic matrix</b> \(K = \begin{bmatrix} f/\rho_u & 0 & u_0\\ 0 & f/\rho_v & v_0 \\ 0&0&1\end{bmatrix}\) (focal length in pixels).</p>
<p><b>Complete model</b> [[p27]]: \(\tilde{\mathbf p} = K\,[\,\text{projection}\,]\,\begin{bmatrix}R&t\\0&1\end{bmatrix}^{-1}\mathbf P\). The inverse appears because \((R,t)\) is the camera’s <i>pose</i> in the world and we need world → camera. The 3×4 camera matrix \(C\) is intrinsics × extrinsics [[p28]]. Scaling \(C\) by any λ gives the same pixel (scale invariance), so \(C_{34}\) can be fixed to 1, leaving <b>11 unknowns</b> [[p29]] [[p30]].</p>
<div class="ex"><b>Worked example.</b> f = 5 mm, ρ = 20 µm → f = 250 px; principal point (320, 240). The camera-frame point (0.4, −0.2, 2.0) m projects to \(u = 320 + 250\cdot0.4/2 = 370\), \(v = 240 + 250\cdot(-0.2)/2 = 215\).</div>
<div class="widget" data-w="pinhole"></div>
<p>Practice Q10 runs the other way (back-projection): \(X = (u - c_u)Z/f = (270-320)\cdot4/500 = -0.40\) m.</p></div>

<div class="sub"><h3>2. What projection does to the scene</h3>
<ul><li><b>No unique inverse</b>: depth is lost, and infinitely many 3D worlds give the same image [[p32]].</li>
<li>Lengths and angles are not preserved; parallelism and perpendicularity are lost; <b>straight lines stay straight</b> [[p33]].</li>
<li>Parallel lines meet at a <b>vanishing point</b> (possibly outside the image); parallel planes meet in a <b>vanishing line</b> [[p34]].</li></ul></div>

<div class="sub"><h3>3. Sensor and lens details</h3>
<p><b>Bayer pattern</b> [[p35]]: RGGB filters with twice as many green, because luminance depends mostly on green and human vision is more sensitive to luminance detail. Missing colours are interpolated (demosaicing).</p>
<p><b>Global vs rolling shutter</b> [[p36]]: global exposes all pixels at once (no distortion of moving objects, more costly); rolling reads rows one after another (cheap, but skews moving objects, which breaks the pinhole two-view model in Week 4).</p>
<p><b>Aperture</b> [[p40]]: a large aperture gives blur; a pinhole lets in little light, which needs long exposure and causes motion blur; too small an aperture causes diffraction. Hence <b>lenses</b>. Thin lens equation: \(\frac1f = \frac1Z + \frac1e\) [[p45]]. Points not in focus spread into a blur circle \(R = L\delta/(2e)\) [[p47]] (keep R &lt; 1 pixel). When \(Z \gg f\) and \(Z \gg L\), \(e \approx f\): the <b>pinhole approximation</b> [[p50]] [[p51]].</p>
<div class="ex"><b>Worked example.</b> f = 50 mm, object at Z = 2 m: \(e = 1/(1/50 - 1/2000) = 51.28\) mm. The image plane sits only 1.3 mm behind the focal point, which is why the pinhole model works.</div></div>

<div class="sub"><h3>4. Stereo: disparity, triangulation and baseline</h3>
<p>With two identical, aligned cameras, points in the right image shift left relative to the left image, and <b>distant points shift less</b> [[p57]]. Disparity \(d = u_L - u_R \propto fb/Z\) [[p58]]. It is found by <b>block matching along the same row</b> [[p60]]. Triangulation [[p63]]:</p>
\[Z = \frac{f\,b}{u_L - u_R},\qquad X = \frac{Z\,u_L}{f},\qquad Y = \frac{Z\,v_L}{f}\quad(u,v\text{ relative to the principal point, }f\text{ in pixels})\]
<p><b>Depth error</b> grows with the square of depth: \(\delta Z \approx \frac{Z^2}{fb}\,\delta d\). Example: f = 700 px, b = 0.12 m, Z = 5 m, δd = 0.5 px gives δZ ≈ 0.149 m.</p>
<p><b>Baseline trade-off</b> [[p64]]:</p>
<div class="tw"><table><tr><th>Large baseline</th><th>Small baseline</th></tr><tr><td>small depth error</td><td>large depth error</td></tr><tr><td>larger minimum measurable depth</td><td>smaller minimum depth</td></tr><tr><td>harder search for close objects</td><td>easier search for close objects</td></tr></table></div>
<div class="widget" data-w="stereo"></div>
<p><b>Rectification</b> [[p96]] [[p101]] [[p103]] warps both images with homographies \(H_L, H_R\) so the image planes become coplanar and parallel to the baseline, with a common \(\hat K\) (often the average of \(K_L\) and \(K_R\)) and a common \(\hat R\) (\(\hat r_1\) along the baseline, \(\hat r_2 = r_{3L}\times\hat r_1\), \(\hat r_3 = \hat r_1\times\hat r_2\)). Undistort the lenses first, then warp with bilinear interpolation [[p99]]. Result: epipolar lines become image rows, so <b>search only along the same row</b> (practice Q9).</p>
<div class="exam"><b>Exam angle.</b> Q8 (a larger baseline gives lower depth error but a larger minimum depth and harder close-range matching), Q9 (search the same row after rectification), Q10 (back-projection with sign) and Q7 (K maps camera-frame coordinates to pixels). Depth and back-projection are the most likely calculations.</div></div>

<div class="sub"><h3>5. Calibration and homographies</h3>
<p>For points on a plane (Z = 0), the 3×4 camera matrix collapses to a 3×3 <b>homography</b> H with 8 unknowns (scale is arbitrary). Each point gives 2 equations, so <b>4 points</b> determine H [[p72]]. The <b>DLT</b> stacks the equations as \(Q\mathbf h = 0\) and solves with SVD [[p89]]. Zhang’s method uses several views of a checkerboard to get K through \(B = K^{-\top}K^{-1}\) and a Cholesky decomposition; the lecturer marks those details as <b>not examined</b> [[p92]]. Lens distortion is radial: barrel, pincushion or fisheye [[p94]].</p></div>
''',
tut=r'''
<p>The Week 3 tutorial is calculation and scenario work, the style of the real exam’s scenario questions. Try each one before opening the solution.</p>
<div class="q" data-qid="w03-t1"><div class="hd"><b>Q1</b><span class="chip">calculation</span></div><div>A 640×480 camera with principal point (320, 240) sits at the world origin, aligned with the world frame and facing +X. Where does the world point p = (10, 0, 0) project?</div>
<details class="sol"><summary>Show worked answer</summary><div class="in"><p>The point lies on the optical axis (it is straight ahead), so its lateral offsets are 0 and it projects to the <b>principal point (320, 240)</b>, whatever the focal length.</p></div></details></div>
<div class="q" data-qid="w03-t2"><div class="hd"><b>Q2</b><span class="chip">calculation</span></div><div>Same camera, f = 5 mm, square pixels of 20 µm. (a) K? (b) the full camera matrix? (c) the image of p = (10, 0, 1)? (d) what happens to u, v if f increases?</div>
<details class="sol"><summary>Show worked answer</summary><div class="in">
<p>(a) \(f/\rho = 5\times10^{-3}/20\times10^{-6} = 250\) px → \(K = \begin{bmatrix}250&0&320\\0&250&240\\0&0&1\end{bmatrix}\).</p>
<p>(b) The camera looks along world +X, so the camera’s \(z_c\) = world X. With the usual camera convention (x right, y <b>down</b>) and world Z up: \(x_c = -Y_w\), \(y_c = -Z_w\), \(z_c = X_w\), so \(R = \begin{bmatrix}0&-1&0\\0&0&-1\\1&0&0\end{bmatrix}\) and t = 0. Then \(P = K[R\,|\,0] = \begin{bmatrix}320&-250&0&0\\240&0&-250&0\\1&0&0&0\end{bmatrix}\).</p>
<p>(c) \(P(10,0,1,1)^\top = (3200, 2150, 10)\) → <b>(320, 215)</b>: the point is 1 m up, so it appears 25 px above the centre.</p>
<p><i>Alternative reading.</i> If you take “aligned with the world frame” to mean the camera’s y axis also points along world +Z (y up), you get v = 265. Say which convention you use. In the exam, state the axis convention explicitly.</p>
<p>(d) Larger f magnifies: the projection moves <b>away</b> from the principal point. Here u stays 320 (X offset 0) and |v − 240| grows.</p></div></details></div>
<div class="q" data-qid="w03-t3"><div class="hd"><b>Q3</b><span class="chip">calculation</span></div><div>Rectified stereo, 300×150 px sensor, f = 5 mm, 20 µm pixels, baseline 20 cm. p_left = (160, 50), p_right = (120, 50). (a) depth? (b) P in the left camera frame? (c) closest observable depth? (d) which parameters could change to measure closer points?</div>
<details class="sol"><summary>Show worked answer</summary><div class="in">
<p>f = 250 px, d = 160 − 120 = 40 px. (a) \(Z = 250\cdot0.2/40 =\) <b>1.25 m</b>.</p>
<p>(b) Principal point (150, 75). \(X = Z(u_L-150)/f = 1.25\cdot10/250 =\) <b>0.05 m</b>; \(Y = 1.25\cdot(50-75)/250 =\) <b>−0.125 m</b> (y points down, so the point is 12.5 cm above the axis). P ≈ (0.05, −0.125, 1.25) m.</p>
<p>(c) The largest possible disparity is about the image width, 300 px (or 299 if you count pixel indices): \(Z_{min} = 250\cdot0.2/300 \approx\) <b>0.167 m</b>.</p>
<p>(d) \(Z_{min} = f b / d_{max} = f_{mm}\,b / (\text{sensor width})\). Changed one at a time: a <b>smaller baseline</b>, a <b>shorter focal length</b> (wider FOV), or a <b>wider sensor</b> (more pixels, or larger pixels at the same f). Each trades away depth accuracy at range.</p></div></details></div>
<div class="q" data-qid="w03-t4"><div class="hd"><b>Q4</b><span class="chip">scenario</span></div><div>A camera 2 m above the centre of a 2 × 2 m workspace looks straight down. The proposed camera is a FLIR Blackfly BFLY-PGE-09S2C-CS with the zoom lens at its wide end (2.8 mm). Is the whole workspace visible? Where do the four corners project?</div>
<details class="sol"><summary>Show worked answer</summary><div class="in">
<p><b>Camera data</b> (Teledyne FLIR product page for BFLY-PGE-09S2C-CS): 1288 × 728 px, pixel size 4.08 µm, Sony ICX692, 1/3″ sensor, CS-mount. Assume the principal point is at the centre, (644, 364).</p>
<p>\(f = 2.8\,\text{mm}/4.08\,\mu\text{m} = 686.3\) px. Each corner is ±1 m from the axis at Z = 2 m, so it is offset by \(686.3\cdot1/2 = 343.1\) px.</p>
<p>Corners: u ∈ {300.9, 987.1}, v ∈ {20.9, 707.1}. All lie inside 0…1287 × 0…727 → <b>the workspace is fully visible</b>, but with only about 21 px of margin at the top and bottom.</p>
<p>FOV check: the sensor is 5.26 × 2.97 mm, so at 2 m the ground footprint is ±1.88 m × ±1.06 m. The short (vertical) side barely covers ±1 m. Orient the camera so the image height spans the workspace and do not zoom in. Small mounting errors or lens distortion could crop the edges, so a slightly wider lens adds safety.</p></div></details></div>''',
quiz=[
 ('Stereo camera: f = 700 px, b = 0.5 m, disparity 35 px. Depth?', ['1 m', '10 m', '24.5 m', '0.1 m'], 1, 'Z = f·b/d = 700·0.5/35 = 10 m.'),
 ('Which statement about perspective projection is true?', ['Parallel lines stay parallel', 'Angles are preserved', 'Straight lines stay straight', 'Distances are preserved up to scale'], 2, 'Projection preserves straightness only; parallelism, angles and lengths are lost [[p33]].'),
 ('A robot’s stereo rig must measure objects 0.3 m away, but they fall outside the search range. Which single change helps?', ['Increase the baseline', 'Increase the focal length', 'Decrease the baseline', 'Use a rolling-shutter camera'], 2, 'Zmin = f·b/dmax, so a smaller baseline (or smaller f) lowers the minimum depth, at the cost of larger depth error at range.'),
],
)
