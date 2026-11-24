# Kinetic Silhouette, line by line

Kinetic Silhouette uses a MediaPipe model to estimate which pixels belong to a person. OpenCV then compares the brightness of consecutive frames to see where those pixels changed. Blue and violet dots represent your silhouette and gold dots mark movement. The model supplies person segmentation and classical frame differencing supplies the motion. The browser and desktop app both use the same Python session to generate each image. Use the browser's mask control or press **M** in the desktop app to inspect the masks. [MediaPipe Selfie Segmenter](https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter#selfie-segmentation-model)

Open [kinetic_silhouette.py](kinetic_silhouette.py) alongside the guide. The line numbers match the file and gaps are blank lines.

## `kinetic_silhouette.py`

### Imports and settings

- **1** Imports OpenCV for drawing, resizing, blurring, and filtering images.
- **2** Imports MediaPipe for the trained selfie segmentation model.
- **3** Imports NumPy for images stored as arrays and for operations that apply to entire arrays at once.
- **5** Imports the shared camera loop, command-line helpers, display panel, model path resolver, exit handler, and MediaPipe image converter.
- **8** Gives the native desktop window a title.
- **9** Sets the canvas to 960 pixels wide and 540 pixels tall.
- **10** Defines the main still-body color. OpenCV uses blue, green, red channel order.
- **11** Defines the complementary color used in a portion of still-body particles.
- **12** Defines the gold color used to highlight detected motion.
- **13** Makes a 3×3 square of ones for the motion cleanup filter. `uint8` is an integer type that stores values from 0 through 255.

### Paint the landscape once

- **16** Defines the function that builds the background image.
- **17** Interpolates between two dark BGR colors, giving each row its own sky color.
- **18** Adds a column axis, then repeats each row color across the width to make a full color image.
- **19** Starts a pseudo-random number generator with seed `18`. Every launch generates the same landscape.
- **20** Creates 110 star positions between rows 55 and 354, below the space reserved for the heading.
- **21** Draws one tiny antialiased circle per star. A thickness of `-1` fills the circle.
- **23** Creates an empty single-channel image to use as a stencil for the moon.
- **24** Fills a 29-pixel-radius disc in the stencil with white.
- **25** Cuts another, offset disc from the white shape by painting it black. The white pixels left behind form a crescent.
- **26** Colors the landscape only where the moon stencil is nonzero.
- **28** Places points every 24 pixels across the canvas to form the hills.
- **29** Loops through two layers with different elevations, offsets, amplitudes, and colors.
- **30** Computes a smooth sine wave for each hill's top edge.
- **31** Pairs each x-coordinate with its ridge y-coordinate and makes integer positions for OpenCV.
- **32** Appends the two bottom corners, so the points enclose a filled hill shape.
- **33** Paints the polygon with soft edges. The second hill sits over the first one.
- **35** Draws random positions for blades of grass close to the ground. Positions can start slightly below the canvas so some blades grow in from the lower edge.
- **36** Chooses the length of one blade between 4 and 13 pixels.
- **37** Draws a slender line upward and a little to the right.
- **38** Returns the complete backdrop so the video loop can reuse it.
- **41** Define the frame resizer shared by the desktop and browser session.

### Prepare the webcam image

- **42** Extracts the original height and width. The last axis of the image holds its BGR channels.
- **43** Bounds the working image to 320×180 while preserving the aspect ratio and leaving small images at their original scale.
- **44** Converts the scaled dimensions to whole pixels, with at least one pixel for each axis. OpenCV takes width before height.
- **45** Resize the camera image for analysis in its original orientation.

### Find the person with MediaPipe

- **48** Defines the person-mask function with the current frame, the time in milliseconds, and the previous mask as inputs.
- **49** Converts the frame from BGR to MediaPipe's RGB input and runs the video-mode segmentation model.
- **50** Takes the last map, which is the person confidence for this model. `numpy_view` exposes the values as an array. `reshape` keeps only the height and width because each pixel has a single confidence value.
- **51** Marks pixels with confidence of at least `0.65` as foreground.
- **52** Checks that a previous mask exists and has matching dimensions before comparing pixels.
- **53** Keeps an already marked pixel while its confidence stays at or above `0.52`. These two cutoffs help prevent the silhouette from flickering around its edges.
- **54** Returns the boolean mask. Every position is either foreground (`True`) or background (`False`).

### Find movement within the person

- **57** Defines the motion calculation using two grayscale images and their corresponding person masks.
- **58** Checks whether there is a previous frame with matching dimensions.
- **59** Starts with an all-false motion mask when there is nothing valid to compare yet.
- **61** Subtracts the previous brightness from the current brightness at each pixel. A signed type is necessary because darkening makes negative differences.
- **62** Counts pixels that became more than eight brightness levels brighter.
- **63** Counts pixels that became more than eight levels darker.
- **64** Takes a change in the same direction across over 75% of pixels as evidence of a general exposure shift.
- **65** Subtracts the median difference to compensate for that broad change. Strong local differences can still remain.
- **67** Finds pixels that changed by at least 20 levels, in either direction, and positions that were absent from the previous person mask.
- **68** Intersects those candidates with the current person mask and converts the result to an integer image for OpenCV.
- **69** Uses morphological opening, erosion followed by dilation, to remove tiny specks and converts the cleaned result back to a boolean mask. [OpenCV morphological transformations](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html)

### Turn masks into art and diagnostic views

- **72** Defines the function that renders the particle landscape for the current masks.
- **73** Copies the background so drawing a frame leaves the reusable original intact.
- **74** Reads the dimensions of the person mask.
- **75** Samples every other row and column and gets the coordinates where the sampled person mask is true.
- **76** Maps those coordinates back to the full mask by doubling each index.
- **77** Picks the scale that fits the mask within the canvas margins while preserving aspect ratio.
- **78** Enlarges and centers the particle positions horizontally, then rounds them to pixel coordinates.
- **79** Enlarges and positions the particles vertically, with a margin for the panel above and the foreground below.
- **80** Makes one blue color row for each particle.
- **81** Alternates some blue particles with violet to add texture to still regions.
- **82** Colors particles gold wherever the aligned motion mask is true.
- **83** Paints the main pixel of each particle using the matching color row.
- **84** Paints a second pixel directly to the right of each original pixel.
- **85** Paints a third pixel directly below each original pixel. The three pixels make the tiny dots easier to see.
- **86** Returns the completed canvas.
- **89** Defines an alternate view that displays solid mask regions.
- **90** Allocates a black color image the same size as the masks.
- **91** Paints person pixels in blue.
- **92** Overwrites motion pixels in gold.
- **93** Gets the height and width of the person mask.
- **94** Uses the same scaling bounds as the particle view.
- **95** Rounds the enlarged width and height to pixel counts.
- **96** Enlarges the color mask using nearest-neighbor interpolation. Each new pixel takes the color of its nearest old pixel, preserving the hard boundaries and exact colors.
- **97** Creates a dark 960×540 canvas for the mask view.
- **98** Finds the left edge of the centered mask and places the bottom just above the canvas edge.
- **99** Pastes the enlarged image into the selected region using NumPy slices.
- **100** Returns the diagnostic canvas.

### Process frames in a shared session

- **103** Defines the session class used by both the web service and the desktop app.
- **104** Initializes each session with its own motion history and display setting.
- **105** Builds the landscape once so each processed frame can reuse it.
- **106** Starts without a previous grayscale frame.
- **107** Starts without a previous person mask.
- **108** Initializes the last model timestamp to `-1`, allowing the first timestamp to be zero.
- **109** Starts in particle view.
- **110** Default the drawn subject to selfie-style reflection.
- **112** Runs this method when a caller opens the session with `with`.
- **113** Resolves the downloaded segmentation model path and converts it to the string MediaPipe expects.
- **114** Starts configuring the image segmenter.
- **115** Points the segmenter at the local model file.
- **116** Chooses video mode, which requires increasing timestamps.
- **117** Requests confidence maps so the app can apply and stabilize its person threshold.
- **118** Completes the options object.
- **119** Creates one segmenter for this session.
- **120** Returns the session to the caller.
- **122** Accepts a color frame and its timestamp in seconds. Both interfaces call this function.
- **123** Resize the input while keeping the analysis coordinates stable.
- **124** Converts to grayscale and applies a 5×5 blur to soften noise before comparing brightness.
- **125** Converts seconds to milliseconds and forces time to advance at least one millisecond per call.
- **126** Uses the segmenter and the previous mask to estimate a stable person mask.
- **127** Compares grayscale frames and restricts detected movement to the person.
- **128** Stores this frame's grayscale image and person mask for the next comparison.
- **130** Check whether the person should appear in the mirrored preview orientation.
- **131** Reflect both Boolean masks by reversing their columns after saving the unreflected history. The camera toggle leaves the background and motion calculation intact.
- **132** Renders either the solid mask or the particle view, according to the session setting.
- **133** Counts the pixels in the person mask and converts the count to a Python integer so the presence flag can travel in JSON.
- **134** Divides Python integer pixel counts to get the movement percentage, using zero for an empty person mask.
- **135** Returns the rendered image, percentage, and flag indicating whether the model detects a person.
- **137** Runs when the caller leaves the session, including when processing raises an error.
- **138** Closes the MediaPipe model and releases its native resources.

### Display the result in the desktop app

- **141** Defines the entry point for running the native app.
- **142** Creates the command-line parser with the common device and video file arguments.
- **143** Reads and validates the entered arguments.
- **144** Opens the shared session and the selected camera or video file together.
- **145** Loops over frames from the selected source.
- **146** Passes the frame and its source timestamp to the shared Python processor.
- **147** Takes the rendered image from the results.
- **148** Reads the percentage of moving person pixels.
- **149** Formats a status message using the percentage or asks the visitor to step into view.
- **150** Picks a heading that matches the active view.
- **151** Draws the measurement, color legend, and keyboard controls on the native preview.
- **152** Shows the image and reads the latest keyboard event.
- **153** Checks whether the shared display helper requested that the app close.
- **154** Leaves the loop so the camera and session can close.
- **155** Checks for the letter `m`.
- **156** Switches the shared session's view for the next frame.
- **159** Runs the program when the file is used as a script. Importing it leaves the camera closed.
- **160** Passes `main` through the shared error and interrupt handler and returns the exit code to the shell.

## `test_kinetic_silhouette.py`

- **1** Imports Python's built-in unit test framework.
- **2** Imports tools for replacing the model in tests with a predictable stand-in.
- **4** Imports NumPy to create repeatable images and masks.
- **6** Imports the shared session, motion function, renderers, and colors the application uses.
- **9** Defines a test case class that gives each test access to the standard assertion methods.
- **10** Begins a test with a uniform change and two local changes.
- **11** Builds a 40×60 grayscale frame with brightness `75` everywhere.
- **12** Makes an initially empty person mask with the same dimensions as the images.
- **13** Marks a rectangular area to play the role of the person.
- **14** Adds 30 brightness levels across the whole scene to simulate exposure adjustment.
- **15** Adds a strong change partly overlapping the person rectangle.
- **16** Adds a local change completely outside the person rectangle.
- **18** Runs the app's motion calculation on the test images.
- **19** Checks that a background pixel stays outside the returned motion mask.
- **20** Checks that a person pixel affected only by the uniform shift remains still.
- **21** Checks that strong changes outside the person are excluded.
- **22** Checks that the strong change inside the person counts as movement.
- **23** Checks that first-frame startup returns only false values.
- **25** Begins a test for mask expansion and for the rendered output in both views.
- **26** Builds a constant grayscale frame, so movement can be measured separately from brightness changes.
- **27** Starts with an empty previous person mask.
- **28** Fills a rectangle in that mask.
- **29** Copies the rectangle into the current mask.
- **30** Extends the rectangle sideways to simulate a newly occupied region.
- **32** Runs the motion calculation with identical brightness values but two different person masks.
- **33** Checks that a newly occupied position counts as motion.
- **34** Checks that an unchanged position remains still.
- **35** Renders the same person and motion arrays through both modes.
- **36** Confirms that each rendered image contains at least one exact blue pixel for a still body region.
- **37** Confirms that each rendered image contains at least one exact gold pixel for movement.
- **39** Begins a test for session isolation, view switching, and model cleanup.
- **40** Creates a small color frame with every channel set to the same brightness.
- **41** Copies the frame so one region can change while the first frame stays intact.
- **42** Paints a brighter rectangle in the changed frame.
- **43** Creates a stand-in for the model's confidence image.
- **44** Makes the confidence image treat every pixel as part of the person.
- **45** Creates a stand-in for the native segmenter.
- **46** Configures the segmenter to return the prebuilt confidence image.
- **48** Supplies a placeholder model path and starts replacing the model factory.
- **49** Configures the factory to return the stand-in.
- **50** Begins the block in which those replacements apply.
- **51** Opens a session using the same lifecycle as the web and desktop callers.
- **52** Processes the initial frame at zero seconds.
- **53** Selects the diagnostic mask view for the next frame.
- **54** Processes the changed frame with a repeated source timestamp to exercise the timestamp adjustment.
- **55** Opens a separate session with no earlier frame.
- **56** Processes the same changed image as that new session's first frame.
- **58** Checks that the first frame includes detected person pixels.
- **59** Checks that the first frame reports no motion.
- **60** Checks that the changed frame reports motion against the first frame.
- **61** Checks that the rendered mask shows the moving region in gold.
- **62** Checks that the fresh session treats its first frame as still.
- **63** Reads the timestamp MediaPipe received on each call.
- **64** Checks that timestamps increase within one session and restart in a new session.
- **65** Checks that leaving each context closes its model.
- **67** Define a regression test for mirror changes on a stationary subject.
- **68** Supply a small constant camera frame.
- **69** Create a Boolean mask aligned with the source frame.
- **70** Put the test subject on the left so reflection is detectable.
- **71** Construct a silhouette session with the default mirrored orientation.
- **72** Supply a placeholder model because this case controls the person mask directly.
- **73** Force both frames to return exactly the same person mask.
- **74** Render the subject with the default mirror setting.
- **75** Turn off mirroring without changing the camera image.
- **76** Render the same source again in its original orientation.
- **78** Find the horizontal positions of the blue pixels in the reflected result.
- **79** Find the corresponding positions in the original result.
- **80** Use the image width to locate the visual center.
- **81** Check that the flipped subject appears on the right.
- **82** Check that the unflipped subject appears on the left.
- **83** Confirm that the toggle does not create a motion event.
- **84** Check that the background where the subject never appears stays unchanged.

## Try it yourself

1. Hold still and watch the body motion percentage. Move one arm and see where gold appears. The measurement describes visible moving pixels in the person mask.
2. Switch to the mask view to inspect the same data as solid colors. Movement in the background should stay outside the masked shape.
3. Lower or raise the brightness threshold on line 68, then repeat the same movement in the same lighting. Lower numbers respond to smaller brightness changes and often surface more noise.
4. Run `.venv/bin/python -m unittest -v test_kinetic_silhouette` to replay the array and color tests without opening the camera.
