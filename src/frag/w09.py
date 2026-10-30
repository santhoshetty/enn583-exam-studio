T = dict(
id='w09', week=9, tab='Learned geometry & 3D', title='Learned geometry and 3D scene representations',
lead='Depth from one image, pointmaps from image pairs (DUSt3R), and the menu of ways to store a 3D scene: point clouds, voxels, occupancy networks, SDFs, NeRFs and Gaussian splats.',
docs=[dict(path='notes/Week09.pdf', title='Week 9 lecture: Learned geometry and 3D representations', pages=80),
      dict(path='notes/papers/DUSt3R.pdf', title='DUSt3R paper (Wang et al., CVPR 2024)', pages=13)],
prac=('week-9-learned-3d-representations.ipynb', 'compares classical stereo depth (SGBM) with Depth Anything V2 monocular depth on KITTI, then builds point clouds and voxels from the recovered geometry.'),
eli5=[
 ('Depth from one eye', 'Close one eye and you still guess distances from experience: rooms, cars and people have typical sizes. But a doll’s house and a real room can look identical, so the absolute scale is a guess.', 'Depth Anything V2 produces a dense depth map from a single KITTI frame; compare it with stereo depth.'),
 ('Depth map vs pointmap', 'A depth map stores one number per pixel (how far). A pointmap stores three (where, as x, y, z), so it already knows the 3D shape without being told the camera’s lens.', None),
 ('NeRF', 'A neural network that you ask “at this spot, looking this way, how dense and what colour?” and it answers. Shine rays through it and you can photograph the scene from new angles.', None),
 ('Gaussian splats', 'Instead of a network, millions of soft coloured blobs floating in space. Rendering is just splatting them onto the screen, which is very fast. Pretty pictures don’t prove solid walls, though.', 'the notebook builds explicit point clouds and voxels, the classical cousins of splats.'),
],
svg='''<svg class="dg" viewBox="0 0 520 170" role="img" aria-label="Spectrum of 3D representations from explicit to implicit">
<path class="ln" d="M20 85 H500"/><path class="ac" d="M490 79 L500 85 L490 91"/>
''' + ''.join(f'<circle class="{c}" cx="{x}" cy="85" r="7"/><text x="{x-30}" y="{y}" class="{s}">{t}</text>' for x,t,y,c,s in [
 (40,'point cloud',65,'fi',''),(115,'voxels',112,'fi',''),(180,'mesh',65,'fi',''),(250,'3D Gaussians',112,'fa',''),(330,'Occ-Net / SDF',65,'fe',''),(405,'NeRF',112,'fe',''),(470,'LERF',65,'fe','')]) + '''
<text x="20" y="150" class="sm">explicit: stored primitives, easy to query for occupancy</text>
<text x="300" y="150" class="sm">implicit: stored in network weights</text>
<text x="190" y="28" class="sm">accent = learned explicit (3DGS); violet = learned implicit</text>
</svg>''',
svgcap='Representations range from explicit (points, voxels, meshes, Gaussians) to implicit (networks you query). The best one depends on the task: planning needs free/occupied space, rendering needs appearance [[p79]].',
videos=['JuH79E8rdKc', 'sQcrZHvrEnU'],
body=r'''
<div class="sub"><h3>1. Monocular depth prediction</h3>
<p>A <b>depth map</b> gives, for each pixel, the Z coordinate of its 3D point in the camera frame (H×W×1) [[p5]]. Training signals [[p6]]:</p>
<ul><li><b>Direct supervision</b>: GT depth from LiDAR, RGB-D, structured light, stereo or synthetic rendering. It can learn metric depth, but dense accurate GT is expensive at scale [[p8]].</li>
<li><b>Self-supervision from geometry</b>: stereo pairs or video with known motion. Predict depth, warp one view into the other and minimise photometric error.</li>
<li><b>Pseudo-labels</b>: a strong teacher labels a large unlabelled set and a student learns from it.</li></ul>
<p>Monocular depth is <b>ill-posed</b>: infinitely many scenes give the same image, and the <b>global scale</b> stays ambiguous (room vs doll’s house). Hence scale-invariant losses and the trend towards relative depth [[p10]].</p>
<p><b>Stereo self-supervision</b> [[p12]] [[p13]]: the network predicts disparity from the left image. Pixel (u, v) with disparity d corresponds to (u − d, v) in the right image. The photometric loss compares \(I_{left}(u,v)\) with \(I_{right}(u-d, v)\), so no depth labels are needed.</p>
<div class="ex"><b>Worked example.</b> Predicted disparity 12 px at (200, 80) → compare with the right image at (188, 80). If the network had predicted 10 px, it would sample (190, 80), probably a different intensity, and the loss pushes the disparity towards the value that makes the pixels agree.</div>
<p><b>Depth Anything</b> [[p18]] [[p19]] [[p22]]: a supervised teacher (DINOv2 encoder) pseudo-labels unlabelled images and a student learns from them. Naive self-training gave no gain, because teacher and student share pre-training and make the same mistakes. Strong perturbations (colour jitter, blur, spatial distortion) on the student’s inputs force it to learn more. V2 trains the teacher on <b>synthetic</b> depth (clean, dense, fine detail), uses a larger teacher (DINOv2-Giant) and trains students on 62M+ pseudo-labelled real images.</p></div>

<div class="sub"><h3>2. From depth to learned multi-view geometry: pointmaps</h3>
<p>A <b>pointmap</b> gives a 3D coordinate (x, y, z) per pixel (H×W×3) [[p26]]. Turning a depth map into points needs the intrinsics (\(X = (u-u_0)Z/f\)); a pointmap already contains them.</p>
<p><b>DUSt3R</b> [[p27]]–[[p35]] takes images with <b>unknown poses and intrinsics</b> and outputs pointmaps, from which camera parameters, correspondences, depth and a consistent 3D reconstruction follow (even from one image). The predictions are consistent but <b>up to scale</b> [[p28]]. The key shift [[p29]]: no explicit matching, E estimation or triangulation; predict dense pointmaps directly and recover the rest. Training: initialise from <b>cross-view completion</b> (CroCo) pre-training, then supervise directly with GT pointmaps built from depth, synthetic geometry or known poses [[p34]]. More than two views: pairwise predictions plus a <b>global alignment</b> optimisation [[p35]]. <b>MASt3R</b> adds a per-pixel descriptor head for precise matching and predicts metric pointmaps [[p36]].</p>
<p>Summary [[p39]]: learned multi-view models can replace parts of the classical pipeline <i>features → matches → pose → triangulation</i>. The geometry hasn’t gone away; it now lives inside the representation and the training objective [[p77]].</p></div>

<div class="sub"><h3>3. How to represent the 3D world</h3>
<p>Classical representations [[p41]]–[[p45]]: occupancy grid maps, point clouds, voxels, meshes, octrees.</p>
<p><b>Occupancy Networks</b> [[p48]] [[p49]]: \(f_\theta(\mathbf x, \mathbf h) \to p_{occupied}\), with a latent code h from an encoder so one network serves many objects. The surface is the decision boundary (p = 0.5). The representation is continuous and can be queried at any resolution; it is trained on sampled points with inside/outside labels.</p>
<p><b>DeepSDF</b> [[p53]]: \(f_\theta(\mathbf x, \mathbf h)\to s\), the signed distance (s &lt; 0 inside, 0 on the surface, &gt; 0 outside). It is richer than occupancy because it says <i>how far</i> from the surface.</p>
<p><b>NeRF</b> [[p57]]–[[p63]]: \(f_\theta(x,y,z,\theta,\phi)\to(\sigma, R, G, B)\). Density σ says where content is (geometry is implicit in the density field); colour depends on viewing direction. Training: posed images; for each pixel cast a ray, sample points, query the network, combine with <b>differentiable volume rendering</b>, and compare with the true pixel colour. <b>No ground-truth 3D geometry is needed</b>: geometry emerges because the field must explain every view [[p68]]. LERF adds CLIP language features [[p67]].</p>
<p><b>3D Gaussian Splatting</b> [[p70]]–[[p73]] is <b>explicit</b>. Each Gaussian has a mean and covariance (centre, shape), an opacity, and view-dependent colour via spherical harmonics. Rendering projects each Gaussian to a 2-D ellipse and blends them by depth and opacity, which is fast. Like NeRF it is trained by comparing renders with photos, without GT geometry. LangSplat adds CLIP features [[p75]].</p>
<div class="tw"><table><tr><th>Representation</th><th>Stores</th><th>Good for</th></tr>
<tr><td>point cloud</td><td>explicit surface samples</td><td>geometry, registration</td></tr>
<tr><td>voxels / occupancy grid</td><td>discrete free / occupied space</td><td>planning, collision checks</td></tr>
<tr><td>mesh</td><td>connected surfaces</td><td>graphics, simulation</td></tr>
<tr><td>Occ-Net / DeepSDF</td><td>continuous learned geometry</td><td>shape completion</td></tr>
<tr><td>NeRF</td><td>implicit geometry + appearance</td><td>novel views</td></tr>
<tr><td>3DGS</td><td>explicit learnable primitives</td><td>fast rendering</td></tr>
<tr><td>LERF / LangSplat</td><td>+ semantic / language features</td><td>“find the mug” queries</td></tr></table></div>
<p class="note">Table from [[p78]]. The best representation depends on the task [[p79]]: VO/SLAM → geometry and consistency; planning → free/occupied space; rendering → appearance; semantic robotics → language-aligned 3D.</p>
<div class="exam"><b>Exam angle.</b> Q29: photoreal novel views show good <i>appearance</i> modelling, but <b>physical occupancy still needs validation</b> (a Gaussian isn’t a solid; empty space isn’t guaranteed free). Q30: metric depth fixes <i>scale</i>, but transparent or reflective surfaces and coordinate alignment still need validation before collision avoidance. Expect “which representation for a planner?” scenarios.</div></div>
''',
paper=dict(title='DUSt3R: Geometric 3D Vision Made Easy (Wang et al., CVPR 2024)', sixty=r'''
<p><b>Problem.</b> Classical multi-view reconstruction chains calibration → matching → pose → triangulation, and each stage can fail. DUSt3R regresses 3D directly from an image pair with <b>no known intrinsics or poses</b>.</p>
<p><b>Key idea</b> (Sec. 3.1, Fig. 2 [[P:p3]]): a Siamese, weight-sharing ViT encoder, two transformer decoders that exchange information through cross-attention, and regression heads. The output is two pointmaps \(X^{1,1}, X^{2,1}\) <b>both expressed in camera 1’s frame</b>, plus confidence maps. The loss is a 3-D regression normalised by the mean point distance (to handle scale), weighted by confidence C with a −α log C regulariser. Low confidence is learned without supervision, e.g. for sky and translucent surfaces.</p>
<p><b>What falls out</b> (Sec. 3.3): matches = mutual nearest neighbours in 3-D; focal length by fitting \(f\) so that \(f\cdot(X,Y)/Z\) matches pixel offsets (principal point assumed at the centre); relative pose by Procrustes (closed form, noise-sensitive) or more robustly PnP + RANSAC. Global alignment (Sec. 3.4): optimise world pointmaps, a pose \(P_e\) and scale \(\sigma_e\) per pair (with \(\prod\sigma_e = 1\) to avoid the trivial σ = 0), minimising <b>3-D</b> errors by gradient descent. It is fast, unlike 2-D reprojection BA.</p>
<p><b>Headline numbers</b> (Sec. 4.5, DTU, zero-shot, no camera parameters): accuracy 2.7 mm, completeness 0.8 mm, overall 1.7 mm. That is below the best MVS methods, which use GT poses, train on DTU and triangulate with sub-pixel precision; regression is less accurate. The authors argue the plug-and-play convenience is worth it.</p>''',
),
tut=r'''
<p><b>1. Pointmap vs depth map.</b> A depth map stores Z per pixel; turning it into 3D needs the intrinsics K (and the pose, for a world frame). A pointmap stores (X, Y, Z) per pixel directly in a chosen frame.</p>
<p><b>2. Common frame.</b> Expressing both images’ points in camera 1’s frame makes them directly comparable: matching becomes a 3-D nearest-neighbour search and relative pose a point-set alignment. The network must implicitly learn the <b>relative pose and the correspondence</b> between the views (the epipolar relationship).</p>
<p><b>3. What is replaced or relaxed.</b> Feature matching, calibration, pose estimation and triangulation are all replaced by one regression. What remains: the pinhole projection (used to recover focal length and to build GT), multi-view consistency, scale ambiguity (pointmaps are normalised) and global alignment.</p>
<p><b>4. Confidence maps.</b> They weight the loss and signal reliability. Expect low confidence in sky, reflective or transparent surfaces, textureless regions, object boundaries and areas seen in only one view.</p>
<p><b>5. Global alignment.</b> Build a pair graph, predict pointmaps per pair and optimise world pointmaps with one rigid transform and one scale per pair so that all pairs agree (confidence-weighted 3-D error). Scale factors are needed because each pair is predicted up to its own normalised scale.</p>
<p><b>6. Why recover intrinsics, poses and depth?</b> Downstream robotics still needs them: planning in metric space, fusing with other sensors, using the camera in a SLAM or BA pipeline, checking consistency, or re-using classical refinement.</p>
<p><b>7. Recovering quantities (Sec. 3.3).</b> Matching: reciprocal 3-D nearest neighbours. Focal: robust least-squares fit of f to the pointmap’s x/z, y/z against pixel offsets. Relative pose: Procrustes on the two pointmaps of the same image, or PnP-RANSAC. One representation serves all these tasks, hence “a common representation”.</p>
<p><b>8. MVS results (Sec. 4.5).</b> 2.7 mm accuracy, 0.8 mm completeness, 1.7 mm overall on DTU, behind methods with GT cameras. The authors explain this by those methods using known poses, DTU training and sub-pixel triangulation, while regression is less precise. They trade some accuracy for needing no prior camera information.</p>''',
quiz=[
 ('What does NeRF need for training?', ['Ground-truth 3D meshes', 'Posed images only', 'LiDAR point clouds', 'Semantic labels'], 1, 'Geometry emerges from rendering the training views consistently [[p68]].'),
 ('DUSt3R outputs two pointmaps. In which frame are they expressed?', ['Each in its own camera frame', 'Both in camera 1’s frame', 'In a GPS world frame', 'In normalised image coordinates'], 1, 'The common frame of camera 1 is the key design choice (Sec. 3.1).'),
 ('A 3DGS map renders photo-realistic views of a warehouse. What is justified?', ['Every empty volume is collision-free', 'Appearance is modelled well for tested views; physical occupancy still needs validation', 'Each Gaussian is a solid object', 'Glass shelves are reconstructed correctly'], 1, 'Practice-exam Q29 logic.'),
],
)
