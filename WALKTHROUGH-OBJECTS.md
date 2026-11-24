# Object Motion Lab, line by line

Start with [motion_detector.py](motion_detector.py). It runs two independent checks on the same camera frame. OpenCV measures where pixel brightness changed, and EfficientDet-Lite2 predicts which objects appear and where. A stationary cup can keep a named box after its green motion box clears.

## `motion_detector.py`

### Prepare and compare frames

- **1** `cv2` provides OpenCV’s image, text, and display operations.
- **3** Import the shared camera loop, source argument handling, and command-line error handler.
- **4** Import the detection record along with model setup, tracking, prediction, and drawing.
- **7** `PREVIEW` names the main color preview window.
- **8** `MASK_WINDOW` names the optional black-and-white view.
- **9** `BOX_COLOR` stores the green motion outline in blue, green, red order.
- **10** Build a 9×9 elliptical kernel once for the morphology step that fills small gaps.
- **13** `prepare_frame` takes a color image and returns the image format used for motion comparison.
- **14** Convert each pixel from three BGR channels to one grayscale brightness value.
- **15** Smooth brightness using a 5×5 Gaussian neighborhood. The last argument lets OpenCV derive the blur strength from that size.
- **18** `detect_motion` receives two prepared images and two settings. `threshold` applies to individual pixels and `min_area` applies to whole contours.
- **19** `absdiff` measures the size of each brightness change. A jump from 40 to 80 and a drop from 80 to 40 both produce 40.
- **20** Differences greater than the threshold become white (`255`) and the rest become black (`0`). The first return value repeats the threshold and is discarded with `_`.
- **21** Morphological closing expands the white blobs and then shrinks them with the same kernel, filling small gaps and holes.
- **22** Trace the outer contours of white regions. `CHAIN_APPROX_SIMPLE` stores straight stretches using their end points, and `_` discards contour hierarchy.
- **23** Start with an empty list of accepted boxes.
- **24** Inspect each contour separately.
- **25** Measure the area enclosed by the contour and compare it with the minimum.
- **26** Fit an upright rectangle to each accepted contour and add its `(x, y, width, height)` tuple.
- **27** Return the mask for inspection and the filtered boxes for the color feed.

### Desktop motion drawing

- **30** `draw_motion` receives the original color image and edits its pixels in place.
- **31** Unpack each rectangle into its position and size. The origin is at the top left.
- **32** Draw a two-pixel outline. The subtraction places the endpoint on the rectangle’s last pixel.
- **33** Put the label just above the box, or inside its top edge when the box is high in the frame.
- **34** Open the multi-line OpenCV call that writes text onto the image.
- **35** Supply the image, label text, label baseline coordinates, and OpenCV’s built-in font.
- **36** Apply a half-size font, green coloring, two-pixel strokes, and antialiasing for smoother letters.
- **37** End the drawing call.

### Shared vision session

- **40** Define one object and motion processor shared by the browser and Terminal.
- **41** Accept the active mode, the model's score cutoff, motion thresholds, and the mask setting.
- **42** Store the selected mode so the web layer can change it during a session.
- **43** Keep the confidence cutoff for creating the detector when it is first needed.
- **44** Save the difference threshold applied to individual pixels.
- **45** Save the area cutoff applied to contours.
- **46** Choose whether the outgoing result includes the diagnostic mask.
- **47** Leave the object model unloaded until object detection is requested.
- **48** Create a private box tracker for this camera session.
- **49** Make the first frame eligible for inference.
- **50** Keep track of frame dimensions to recognize a source size change.
- **51** Start without a previous grayscale image.
- **53** Define entry to a context manager so either runner can use the processor in a with block.
- **54** Return this processor for the caller to use.
- **56** Define the model cleanup called when the context closes.
- **57** Check whether the detector was actually opened.
- **58** Release the object detector and its native resources.
- **60** Accept an unmarked color image and a timestamp in seconds.
- **61** Read the height and width so predictions always match the live image.
- **62** A frame size change makes old boxes stale. Motion-only mode also clears object history.
- **63** Remove all previous object tracks.
- **64** Allow inference to run immediately when the object view becomes active again.
- **65** Save the new frame shape for the next comparison.
- **67** Start with an empty list of displayable object predictions.
- **68** Run the named-object path for Objects and Both modes.
- **69** Detect the first frame that needs a model.
- **70** Open the pinned detector with the user's minimum confidence.
- **71** Run another expensive prediction only when the clock reaches the scheduled time.
- **72** Pass the fresh detections through the existing tracker.
- **73** Leave at least 170 milliseconds between model calls while continuing to return tracked boxes.
- **74** Build the list of JSON-ready detections returned to the display layer.
- **75** Store category name, confidence, and four box coordinates for one confirmed track.
- **76** Read only the tracks that were confirmed and have not expired.
- **77** Finish the outgoing list.
- **79** Use an empty mask and list before checking whether motion processing is enabled.
- **80** In Objects mode, skip frame differencing.
- **81** Throw away the previous frame so re-enabling motion starts with a clean baseline.
- **82** Run the motion branch for Both and Motion modes.
- **83** Convert the unmarked frame to blurred grayscale.
- **84** Read the previous comparison image from this session.
- **85** Detect a missing frame or a frame with different dimensions.
- **86** Use the current frame as its own baseline in either case.
- **87** Compare the images and keep the binary mask and large contours.
- **88** Save the blurred grayscale frame for the next sample.
- **89** Return the named detections and motion rectangles in frame coordinates.
- **90** Include the mask pixels only when the selected view requests them.

### Read the settings

- **93** `parse_args` collects the settings used only by Object Motion Lab.
- **94** Start with the source selection and help description used by all four apps.
- **95** Offer three display modes and start with both layers enabled.
- **96** Accept a floating-point minimum object score and default it to 0.4.
- **97** Accept an integer pixel-difference threshold and default it to 20.
- **98** Accept an integer minimum contour area and default it to 200 square pixels.
- **99** Turn on the second window only when `--show-mask` is present.
- **100** Parse the command line and validate camera index and video path.
- **101** Check that confidence lies between zero and one, with zero excluded.
- **102** Stop with a clear usage error if the confidence is outside that range.
- **103** Check that the threshold is below 255, the greatest possible brightness difference.
- **104** Report the allowed threshold range.
- **105** Require a contour area of at least one square pixel.
- **106** Report a usage error for a zero or negative area.
- **107** Detect the combination of an object-only view and a request to show the motion mask.
- **108** Explain that a mask requires either motion or both mode.
- **109** Return the validated settings to the caller.

### Run the desktop preview

- **112** Define the native Terminal entry point, which owns input and display.
- **113** Read and validate CLI arguments before opening the camera.
- **114** Combine a desktop camera with the same ObjectMotionSession used by the server.
- **115** Pass the requested mode and tuning options through to the session.
- **116** Enable the optional diagnostic mask if requested.
- **117** Bind the processor to session after both context managers have opened.
- **118** Read color frames until the camera or input file finishes.
- **119** Get predictions and motion regions through the shared processor.
- **120** Draw green motion outlines on the original color image.
- **121** Check whether a mask was requested and produced.
- **122** Show that binary image in its own OpenCV window.
- **123** Convert each outgoing detection record back into the small record accepted by the drawing function.
- **124** Iterate through the named result list to draw all its boxes and confidence labels.
- **125** Update the OpenCV preview and check whether quitting was requested.
- **126** Break out of the loop and close resources on exit from the with block.
- **129** Start the camera only when Python executes this file as a command.
- **130** Use the shared runner to turn the app's status into a shell exit code.

## `object_detection.py`

### Represent detections and compare boxes

- **1** Import `dataclass` to define records with automatic constructors and value comparisons.
- **3** Import OpenCV drawing functions.
- **5** Import the model-file lookup and the BGR-to-RGB conversion used by MediaPipe.
- **8** Set a small palette of label colors in BGR order.
- **9** Set the amount of time a confirmed box can survive a missed result, in seconds.
- **10** EfficientDet-Lite2 accepts a square 448 × 448 image.
- **13** Tell Python to generate a constructor and comparisons for detection records.
- **14** Define the fields for a model prediction.
- **15** Store the category name, such as `cat`.
- **16** Store the model confidence as a fraction between zero and one.
- **17** Store four integers for the top-left position, width, and height.
- **20** Generate the same record methods for track data.
- **21** Define a track, which associates a detection with recent observations across frames.
- **22** Keep the current label, score, and box together.
- **23** Record when the model last saw the match.
- **24** Start at one observation for each newly proposed track.
- **27** Define the intersection-over-union score used to match two boxes.
- **28** Unpack the first rectangle’s position and size.
- **29** Unpack the second rectangle the same way.
- **30** Subtract the larger left edge from the smaller right edge. Disjoint boxes get an overlap width of zero.
- **31** Calculate the shared height using the top and bottom edges.
- **32** Multiply those shared dimensions to get the intersection area.
- **33** Add both rectangle areas and subtract the intersection once so it is counted only once in the union.
- **34** Divide intersection by union. Matching boxes give 1, disjoint boxes give 0, and a zero-size union gives 0.

### Confirm, smooth, and expire boxes

- **37** Define the tracker that owns all active object observations.
- **38** Initialize the tracker for a fresh camera run.
- **39** Keep an empty list until there are predictions.
- **41** `update` receives a new model sample and its time in seconds.
- **42** Keep only previous tracks that were seen within the hold interval.
- **43** Start a separate list for tracks matched or created by the new sample.
- **44** Consider high-confidence detections first so they get first choice of matches.
- **45** Begin an iterator over possible matches in the previous sample.
- **46** Associate each candidate’s geometric overlap score with its list index.
- **47** Enumerate available tracks so the winner can be removed by index.
- **48** Compare boxes only when their category names agree.
- **49** End the candidate iterator.
- **50** Pick the highest overlap score, or a zero score with no valid index when there are no candidates.
- **51** Require at least 0.25 intersection-over-union to keep the same track.
- **52** Give unmatched detections a new track with one observation.
- **53** Skip the matching and smoothing branch for a new track.
- **54** Remove the matched previous track so it cannot be assigned to another detection in this sample.
- **55** Blend old and new coordinates with more weight on the current result and round to pixels.
- **56** Pair the two boxes’ corresponding `x`, `y`, width, and height values.
- **57** Create a detection with the newest name and score and the blended box.
- **58** Save it with a fresh timestamp and one more observation.
- **59** Keep current tracks and previously confirmed tracks that missed this sample. Unconfirmed misses drop away.
- **61** `visible` is called on each preview frame, including when the model did not run.
- **62** Return the detections rather than their internal track records.
- **63** Limit the return value to tracks observed at least twice and seen within the hold interval.

### Ask the model for predictions

- **66** `create_detector` loads the named-object model with the requested minimum score.
- **67** Import MediaPipe only in modes that need it.
- **69** Find the pinned model file and pass its local path to MediaPipe.
- **70** Set the confidence cutoff and cap the number of boxes at 12 per sample.
- **71** Open the detector in its default image mode.
- **74** `fit_for_model` prepares the image for the square model input.
- **75** Read the original image height and width in pixels.
- **76** Compute a scale that fits the longer dimension exactly into the input square.
- **77** Scale the width and keep at least one pixel after rounding.
- **78** Scale the height by the same factor so objects keep their proportions.
- **79** Compute the left padding that centers the resized image horizontally.
- **80** Compute the top padding that centers it vertically.
- **81** Use area-based shrinking or linear interpolation for enlarging the image.
- **82** Resize to those dimensions before adding the border.
- **83** Start the OpenCV call that pads the resized image.
- **84** Supply the top, bottom, left, and right border widths. The far edge gets any extra pixel from rounding.
- **85** Fill the border with a constant middle gray across all three channels.
- **86** Finish the padding call.
- **87** Return the square image, its padding offsets, and the scale factors for mapping model coordinates back to preview pixels.
- **90** `infer_objects` turns one current color frame into simple detection records.
- **91** Fit the input image and retain the values needed to undo the transformation.
- **92** Convert the padded image for MediaPipe and run EfficientDet on it.
- **93** Start the output list.
- **94** Read each prediction from the model result.
- **95** Get the best category for the predicted region.
- **96** Extract the rectangle supplied by MediaPipe.
- **97** Start building a four-value box tuple in preview pixels.
- **98** Remove the padding from the top-left coordinates and scale them back to the original preview dimensions.
- **99** Scale the model width and height back to preview pixels and round to whole numbers.
- **100** Finish the box tuple after all four values are converted.
- **101** Append the category, score, and box as a `Detection`.
- **102** Return the completed list to the tracker.

### Draw named rectangles and confidence labels

- **105** `draw_objects` renders confirmed records onto the same color image.
- **106** Read the image dimensions so boxes can be clipped to the preview.
- **107** Select the built-in OpenCV font used by the labels.
- **108** Draw one prediction at a time.
- **109** Unpack its box record.
- **110** Clamp left and top positions to at least zero.
- **111** Clamp right and bottom endpoints to the image’s last valid column and row.
- **112** Detect a box that has no visible interior after clipping.
- **113** Skip that unusable rectangle before calling the OpenCV drawing functions.
- **114** Map the name to a stable palette color using the sum of its character codes.
- **115** Format the name and confidence, such as `cat 92%`.
- **116** Measure the text and allow ten extra pixels of horizontal padding.
- **117** Keep the label near its box while shifting it left when it would extend past the right edge.
- **118** Place the label above the outline if there is space or on top of the box otherwise.
- **119** Draw the colored two-pixel outline.
- **120** Fill a colored background behind the label for contrast.
- **121** Draw dark antialiased lettering on that background.

## `test_object_detection.py`

- **1** Import Python’s built-in test framework.
- **3** Import NumPy so the geometry test can make a small image array.
- **5** Import the same records, tracker, overlap, and image preparation functions used by the live app.
- **8** Group the tracker regression tests in one `TestCase` class.
- **9** Define a test that checks when a new box appears, settles, and clears.
- **10** Start with an empty tracker.
- **11** Make a cat prediction with a known rectangle and confidence.
- **12** Make a second prediction for a dog in a different place.
- **13** Submit the first model sample at time zero.
- **14** Check that one sample has produced no visible boxes.
- **16** Submit a second, slightly shifted cat detection 0.2 seconds later, with no dog.
- **17** Check that only the cat appears and that smoothing puts it between the earlier and later coordinates.
- **18** Submit a sample with no predictions to simulate a brief miss.
- **19** Check that the cat remains visible during the hold interval.
- **20** Check that the cat expires after the hold interval.
- **22** Define a test for two predictions with the same category in one frame.
- **23** Create a fresh tracker for this test.
- **24** Place the first cat on the left.
- **25** Place the second cat well to the right.
- **26** Confirm that their rectangles have zero overlap.
- **27** Submit the first model sample with both detections.
- **28** Submit both detections again in the opposite input order.
- **29** Check that the tracker still confirms both rectangles, ordered by confidence.
- **31** Define a test for preparing a wide camera image for the square model.
- **32** Create a 480 × 240 source image with the same known value in all three channels.
- **33** Prepare the image and unpack its padding and scale metadata.
- **34** Check that the model input has the required square dimensions and three color channels.
- **35** Check for no left padding and 112 rows of top padding.
- **36** Confirm that the inverse scale factors recover the original frame width and height.
- **37** Verify that a pixel in the border is middle gray.
- **38** Verify that a pixel on the resized image still has its original channel value.

## `test_motion_detector.py`

These tests generate two small images in memory. They run without opening a webcam.

- **1** `unittest` is Python's built-in framework for writing and running tests.
- **2** Import the mock helper so the mode-switching test can stand in for the model.
- **4** `numpy` is imported as `np` so the test can create image arrays directly.
- **6** Import the shared session and the low-level motion functions under test.
- **7** Import the record type used for a predictable object prediction.
- **10** `MotionDetectorTest` inherits from `unittest.TestCase`, which provides assertions and lets the test runner discover its test methods.
- **11** Names beginning with `test_` tell `unittest` which methods to run. This test follows a still scene, a change, and a still scene again.
- **12** `np.zeros` creates a black frame with 160 rows, 240 columns, and three color channels. `uint8` stores each channel in the range `0` through `255`.
- **13** `copy()` creates a separate frame to edit while preserving the original black frame.
- **14** Array slicing sets rows 40 through 99 and columns 70 through 149 to `255` on all three channels. That creates a white rectangle 80 pixels wide and 60 pixels high.
- **15** A second slice sets a 2×2 patch near the top-left corner to white to simulate a small change that should be too small for a box.
- **17** Preparing the black frame gives the test the previous grayscale image.
- **18** Preparing the changed frame applies the same grayscale conversion and blur to the test rectangle and speck.
- **20** Comparing the previous image with itself simulates an unchanged camera feed.
- **21** A mask with no changed pixels contains only zeros, so `mask.any()` must be false.
- **22** No contours should be accepted, which yields an empty box list.
- **24** Comparing the prepared black and changed images simulates something appearing in the frame.
- **25** The expected result is one box. The big rectangle counts as motion and the tiny patch falls below the area threshold.
- **26** The test unpacks the first box so it can check its position and size.
- **27** The box's upper-left corner must land close to the original coordinates. The range allows the blur and threshold to extend the changed region slightly.
- **28** The width and height are also expected to be close to the original dimensions, with a small margin for the processing.
- **29** The sample in the middle of the rectangle must be white in the mask. Array indexing uses row before column, so `[70, 110]` means `y=70`, `x=110`.
- **30** The speck also appears as white in the mask. The single accepted box from line 25 shows how the contour-area filter controls the drawn results after the mask is built.
- **32** Comparing the changed frame with itself simulates the rectangle staying where it is for the next frame.
- **33** The repeated image must yield an all-black mask.
- **34** The detector should draw zero boxes once the image stops changing.

### Switch modes without reopening the camera

- **36** Test that mode changes work within a single camera session.
- **37** Create the first blank color image.
- **38** Copy the image before modifying it.
- **39** Add one large white rectangle, which is enough to trigger motion.
- **40** Define the named prediction the fake detector will produce.
- **41** Start a block with the mocked detector, inference function, and motion session.
- **42** Replace detector setup with a mock that records when a model would have opened.
- **43** Replace real inference with the predetermined person prediction.
- **44** Start the shared processor in motion-only mode with masks enabled.
- **45** Open all three contexts before running the assertions.
- **46** Confirm the first frame serves as the baseline, yielding no movement.
- **47** Confirm the changed image produces one motion box.
- **48** Verify the object model has not been opened.
- **49** Switch the session to object-only mode.
- **50** Check that a previously enabled mask is absent when motion is disabled.
- **51** Submit the second object sample to confirm the track.
- **52** Expect the JSON-ready prediction with four pixel coordinates.
- **53** Finish the expected object list.
- **54** Switch on both analyses.
- **55** Verify the motion branch establishes its baseline again instead of using stale pixels.
- **56** Check that the lazily opened detector closed exactly once.
