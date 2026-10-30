T = dict(
id='w01', week=1, tab='Intro & images', title='What robotic vision is, and images as arrays',
lead='The unit’s framing (pixels → information → actions) plus the first image operations: indexing, thresholding, convolution and image derivatives.',
docs=[dict(path='notes/Week01.pdf', title='Week 1 lecture: Introduction', pages=88)],
prac=('week-1-Introduction.ipynb', 'loads, inspects, crops, thresholds and filters images with OpenCV and scikit-image ("show, then do" exercises with TODO cells).'),
eli5=[
 ('Robotic vision', 'A camera gives the robot a photo, not the answers. Like a detective, it must <i>infer</i> where it is, what is around it and what to do from clues in the pixels.', None),
 ('An image is a spreadsheet', 'A greyscale image is a grid of numbers (0 = black, 255 = white for uint8). Colour is three stacked grids: red, green, blue.', 'you index pixels as <code>img[v, u]</code>: row first, then column.'),
 ('Convolution', 'A small stencil slides over the grid; at each spot you multiply-and-add. Different stencils blur, sharpen or find edges. CNNs learn the stencils.', 'the filtering cells apply blur and edge kernels.'),
 ('Edges are slopes', 'An edge is where brightness changes fast, like a cliff on a hill map. The derivative measures the slope, and the gradient arrow points uphill.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 170" role="img" aria-label="Convolution: a 3 by 3 kernel slides over the image and writes one output pixel">
<g>
<rect class="bx" x="10" y="20" width="150" height="130"/>
<path class="ln" d="M40 20v130M70 20v130M100 20v130M130 20v130M10 46h150M10 72h150M10 98h150M10 124h150" style="stroke:var(--line)"/>
<rect class="sk" x="40" y="46" width="90" height="78"/>
<text x="12" y="14">image I</text>
<rect class="bx" x="210" y="50" width="90" height="78"/><path class="ln" d="M240 50v78M270 50v78M210 76h90M210 102h90" style="stroke:var(--line)"/>
<text x="219" y="68">−½</text><text x="250" y="68">0</text><text x="278" y="68">½</text>
<text x="219" y="94">−½</text><text x="250" y="94">0</text><text x="278" y="94">½</text>
<text x="219" y="120">−½</text><text x="250" y="120">0</text><text x="278" y="120">½</text>
<text x="210" y="44">kernel (x-derivative)</text>
<path class="ac" d="M135 85 C170 85 175 89 205 89"/><path class="ac" d="M305 89 C340 89 350 85 380 85"/>
<rect class="bx" x="385" y="20" width="125" height="130"/><rect class="sk" x="425" y="72" width="30" height="26"/>
<text x="387" y="14">output = Σ kernel × patch</text>
<text x="390" y="140" class="sm">one value per position</text>
</g></svg>''',
svgcap='Convolution: multiply the 3×3 patch by the kernel, add up, write one output pixel, slide on. This kernel is a smoothed central difference, so the output is large where brightness rises left→right.',
videos=['yb2tPt0QVPY', 'uihBwtPIBxM'],
body=r'''
<div class="sub"><h3>1. What robotic vision is</h3>
<p>Definition [[p10]]: <b>robotic vision is the use of cameras and algorithms to estimate information about the world that a robot needs for actions.</b> The comparison table [[p12]] is worth memorising:</p>
<div class="tw"><table><tr><th>Field</th><th>Input → Output</th><th>Example</th></tr>
<tr><td>Image processing</td><td>image → image</td><td>blur, sharpen</td></tr><tr><td>Computer graphics</td><td>data → image</td><td>rendering</td></tr>
<tr><td>Computer vision</td><td>image → information</td><td>labels, boxes, depth, pose</td></tr><tr><td>Robotic vision</td><td>image → action-relevant information</td><td>where to move, where to grasp</td></tr>
<tr><td>Robot learning</td><td>image + actions + data → behaviours</td><td>RL, imitation learning</td></tr></table></div>
<p>The three big questions [[p13]]: <b>Where am I?</b> (geometry, features, VO, SLAM: Weeks 2–7), <b>What is around me?</b> (detection, segmentation, representations: Weeks 8–12), <b>When does vision fail?</b> (occlusion, lighting, ambiguity, uncertainty, distribution shift: Week 13).</p>
<p>All examples share three things [[p30]] [[p31]] [[p33]]: they start from <i>images, not the true state</i> (motion, location, 3D, identity, grasp and action must be inferred); they output a <i>task-specific representation</i> (trajectory, map, boxes, grasp, policy); and they face <i>ambiguity</i>. VO can be fooled by a moving object, SLAM by two similar-looking places, a detector by a novel object, a grasp planner by occlusion, a policy by out-of-distribution situations.</p>
<div class="exam"><b>Exam angle.</b> Scenario questions often begin “what must the robot infer, and what could make it confidently wrong?”. Answer with the p33 failure list. The lecturer’s advice [[p37]]: for any method ask what problem it solves, what it estimates, why the robot needs it, what assumptions make it work and when it fails.</div></div>

<div class="sub"><h3>2. Images are arrays</h3>
<p>Colour images have three channels (R, G, B); greyscale has one [[p51]]. Datatype matters [[p53]]: <code>uint8</code> holds 0–255 and wraps around on overflow; <code>float32</code> is usually 0–1. Pixel access is <code>img[v, u]</code>, i.e. <b>[row, column]</b>, with the origin at the top-left, u to the right and v downwards [[p59]]. u, v are used because x, y, z already name 3D coordinates.</p>
<div class="ex"><b>Worked example.</b> An image is 480 rows × 640 columns. The pixel at u = 100, v = 20 is <code>img[20, 100]</code>. <code>img[100, 20]</code> would be row 100, column 20, a different pixel.</div></div>

<div class="sub"><h3>3. Thresholding and chromaticity</h3>
<p>Thresholding keeps pixels brighter or darker than a value [[p62]]. Testing “very red” with R &gt; 150 also fires on <b>white</b> pixels, because white has a high R too [[p65]]. The fix is <b>chromaticity</b>: \(r = R/(R+G+B)\), which measures the <i>proportion</i> of red independent of brightness [[p66]].</p>
<div class="ex"><b>Worked example.</b> Red pixel (200, 50, 50): \(r = 200/300 = 0.667\). White pixel (250, 250, 250): \(r = 250/750 = 0.333\). The threshold \(r &gt; 0.5\) keeps the red pixel and rejects the white one, which a raw R &gt; 150 test cannot do.</div>
<div class="widget" data-w="chroma"></div></div>

<div class="sub"><h3>4. Neighbourhood operations and convolution</h3>
<p>Replace each pixel by a value computed from its neighbours [[p67]]. Convolution slides a kernel over the image and sums kernel × patch [[p69]]. Traditional kernels are hand-designed (blur, sharpen, edge); in a CNN the kernels are <b>learned from data</b> [[p72]]. This is the same operation, which is why Week 1 links to Week 8.</p></div>

<div class="sub"><h3>5. Edges and image derivatives</h3>
<p>An edge is where intensity changes rapidly [[p73]]. For a 1-D function the central finite difference is \(\dfrac{\partial f}{\partial x} \approx \dfrac{f(x+\epsilon) - f(x-\epsilon)}{2\epsilon}\) [[p76]]. With \(f(x)=x^2\), \(x=2\), \(\epsilon=1\): \((9-1)/2 = 4\), matching the true derivative \(2x = 4\).</p>
<p>Images have <b>two</b> partial derivatives [[p78]]: \(I_x \approx \tfrac{I(x+1,y) - I(x-1,y)}{2}\), \(I_y \approx \tfrac{I(x,y+1) - I(x,y-1)}{2}\). Each is a convolution with \([-\tfrac12, 0, \tfrac12]\) [[p79]].</p>
<p>The gradient \(\nabla I = (I_x, I_y)\) points in the direction of steepest ascent. Its direction \(\theta = \operatorname{atan2}(I_y, I_x)\) is <b>perpendicular to the edge</b>, and its magnitude \(\|\nabla I\| = \sqrt{I_x^2 + I_y^2}\) is the edge strength [[p80]].</p>
<div class="ex"><b>Worked example.</b> Row of pixels [10, 20, 60, 100, 110]. At the third pixel (value 60): \(I_x = (100-20)/2 = 40\). At the fourth: \((110-60)/2 = 25\). The edge is strongest around the third pixel. If somewhere \(I_x = 30, I_y = 40\), then \(\|\nabla I\| = 50\) and \(\theta = 53.1^\circ\).</div>
<p><b>Noise</b> makes raw derivatives spiky [[p81]], so <b>smooth first</b> and look for peaks of \(\tfrac{\partial}{\partial x}(I * H)\) [[p82]]. Because differentiation commutes with convolution, \(\tfrac{\partial}{\partial x}(I*H) = I * \tfrac{\partial H}{\partial x}\): convolve once with a derivative-of-Gaussian kernel [[p83]].</p>
<div class="widget" data-w="grad"></div>
<div class="exam"><b>Exam angle.</b> Expect a two-line central-difference calculation, “which direction does the gradient point?” (across the edge), or “why smooth before differentiating?” (noise amplification).</div></div>
''',
quiz=[
 (r'In OpenCV/NumPy, which expression reads the pixel in column u = 50, row v = 10?', ['<code>img[50, 10]</code>', '<code>img[10, 50]</code>', '<code>img[u+v]</code>', '<code>img[10][50][3]</code>'], 1, 'Images are indexed [row, column] = [v, u].'),
 (r'A detector flags “red” pixels with R &gt; 150 and also flags white walls. What fixes this most directly?', ['A larger threshold on R', 'Converting to greyscale', 'Thresholding the chromaticity \(r = R/(R+G+B)\)', 'Blurring the image'], 2, 'Chromaticity measures the proportion of red and ignores overall brightness, so white (r ≈ 0.33) is rejected.'),
 (r'Why do edge detectors smooth the image before taking derivatives?', ['To make the image smaller', 'Derivatives amplify pixel noise; smoothing suppresses it so true edges give clear peaks', 'Smoothing turns edges into corners', 'Derivatives only work on blurred images'], 1, 'Noise creates many small spikes in the raw derivative [[p81]]; smoothing first leaves peaks at real edges.'),
],
)
