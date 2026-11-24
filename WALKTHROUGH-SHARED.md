# Shared camera and speech code, line by line

The apps read frames and show their previews through `camera.py`. The gesture and caption apps pass text to the operating system's voice command through `speech.py`. Keeping these operations in shared files lets each app focus on what it does with a frame.

## `camera.py`

### Imports and source selection

- **1** Import `argparse` to define and validate command-line options.
- **2** Import `sys` for its standard error stream.
- **3** Import `Path` to check local files and construct model paths.
- **4** Import a steady elapsed-time clock that keeps going forward if the system clock is adjusted.
- **6** Import OpenCV as `cv2` for video capture, resizing, drawing, and windows.
- **9** Resolve the location of this file and locate its sibling `models` directory. Model lookup then works regardless of the current terminal directory.
- **12** Define a parser builder that accepts each app's description.
- **13** Create the parser, passing the description to its help output.
- **14** Make a group that accepts at most one explicit input source.
- **15** Define an integer camera index and default to the first camera, index 0.
- **16** Accept an optional local video path. In help, `FILE` is the placeholder for that value.
- **17** Return the parser so each app can add its own flags.
- **20** Define the shared argument parsing and validation step.
- **21** Read the chosen options into an object accessible by attribute name.
- **22** Check for a negative camera index.
- **23** Print a validation message with usage and exit if the camera index is invalid.
- **24** When a video path is supplied, check that it points to a file.
- **25** Print the requested path in the error message if the check fails.
- **26** Return the parsed options that passed both checks.

### Resize, open, and read frames

- **29** Define the preview-size limit shared by the webcam apps.
- **30** Get height and width from the first two dimensions of the frame's array.
- **31** Use the smaller of the width and height scale limits and 1. The resulting scale fits the frame within 960 × 640 without enlargement.
- **32** Check whether the current frame already fits.
- **33** Return the original frame in that case.
- **34** Scale both dimensions by the same factor, round each pixel count, and keep both dimensions positive. The size tuple places width first for OpenCV.
- **35** Downsample with `INTER_AREA`, which accounts for each output pixel's area in the original.
- **38** Define a camera object that is both a frame iterator and a context manager.
- **39** Initialize it from the previously parsed arguments.
- **40** Keep the video path, if any, to choose file playback behavior later.
- **41** Give OpenCV a string for a file or an integer for a camera device.
- **42** Initialize the elapsed source time in seconds.
- **43** Start counting frames at zero.
- **44** Track whether the preview has been visible so a window still opening can finish its first display.
- **46** Define the setup that Python runs when entering `with Camera(...) as camera`.
- **47** Open the camera or video with OpenCV's capture interface.
- **48** Check that OpenCV opened the source successfully.
- **49** Release a failed capture before leaving setup. Python calls the context's exit method only after setup succeeds.
- **50** Raise a readable error so the app can report which source failed and suggest common fixes.
- **51** Read the reported frame rate for a video file. The camera path uses elapsed live time directly.
- **52** Compute seconds between file frames, with a 30 FPS fallback when a file provides no usable rate.
- **53** Record when this capture started.
- **54** Return the object that `with ... as camera` exposes to the app.
- **56** Define how `for frame in camera` retrieves successive frames.
- **57** Loop until a return or error ends the iterator, or the calling app stops iterating.
- **58** Ask OpenCV for the next frame and its success flag.
- **59** Handle a failed read before passing the frame to image processing.
- **60** Treat a failed read after at least one successful video frame as the end of playback.
- **61** End the iterator after the file finishes.
- **62** Report a camera read failure or a video that never yielded a frame.
- **63** Get the elapsed time of this read relative to capture setup.
- **64** Use frame count and frame period for a file, or elapsed time for the camera. This gives timed gestures and motion effects a useful source clock.
- **65** Advance the frame index for the next read.
- **66** Yield the resized frame and pause the iterator until the next loop iteration.

### Display, release, and draw

- **68** Define the method that displays a processed frame and reads window input.
- **69** Show the frame in the named OpenCV window.
- **70** Use a short GUI poll for live capture, whose pace is set by reading the camera.
- **71** For a local video, pace the preview to the file instead.
- **72** Compute the remaining time before the next frame's planned display time.
- **73** Convert seconds to milliseconds and wait for at least one millisecond. Frames processed late move on after that minimum delay.
- **74** Let OpenCV process desktop events and collect a key code.
- **75** Check for **Esc** or the `q` key.
- **76** Signal an exit to the calling app with `None`.
- **77** Ask OpenCV whether the preview is currently visible.
- **78** Treat a missing window as a close only after the preview has appeared.
- **79** Signal that the app should quit when the previously visible window closes.
- **80** Save the current visibility for the next preview update.
- **81** Return the key code for any app-specific action.
- **83** Define the cleanup Python runs as it leaves the managed capture.
- **84** Release the capture device or video file.
- **85** Close the OpenCV windows.
- **88** Define a lookup function for files the vision models need.
- **89** Join a model filename to the project model directory.
- **90** Check that the model file is present.
- **91** Report the missing filename and the command that fetches the project's models.
- **92** Return the ready-to-use path.
- **95** Define the conversion from an OpenCV frame to a MediaPipe image.
- **96** Import MediaPipe only when an app needs this conversion. The plain motion detector can use the camera helpers independently.
- **98** Swap the BGR channels of the OpenCV frame into RGB order.
- **99** Wrap the RGB array in a MediaPipe image with its pixel format specified.
- **102** Define an in-place overlay for controls, confidence, and other status strings.
- **103** Get the frame width so the overlay spans the image.
- **104** Fill a dark header whose height grows with the number of text rows.
- **105** Iterate over the rows and count them from zero.
- **106** Use OpenCV's built-in Simplex font.
- **107** Measure the text at the default size and stroke width.
- **108** Decrease the scale if the line is wider than the available space, keeping the margins and size calculation positive.
- **109** Draw light text into the row with antialiasing.
- **112** Define the entry-point wrapper used by each app.
- **113** Start the block that handles anticipated runtime errors.
- **114** Run the app and use zero for a successful return with no explicit exit status.
- **115** Handle a deliberate interruption from the terminal.
- **116** Return a successful exit code after that interruption.
- **117** Catch system and runtime errors, such as a permission failure or missing model file.
- **118** Print the error to standard error.
- **119** Return exit status 1 to signal that the run failed.

## `speech.py`

- **1** Import `shutil` to look up commands available on the system path.
- **2** Import `subprocess` to start and control the voice command.
- **5** Define the speech player used by gesture and scene captioning.
- **6** Initialize a player at app startup.
- **7** Select the first installed engine, checking macOS `say` and then the two eSpeak command names.
- **8** Start without a playback process.
- **10** Make the player usable in a `with` statement.
- **11** Give the running app this player.
- **13** Define the operation that speaks a string.
- **14** Check whether the text is empty or only whitespace.
- **15** Return immediately for empty input.
- **16** Check that a voice command was found.
- **17** Raise an error with the supported voice commands if none is available.
- **18** Stop any ongoing playback before starting the new utterance.
- **19** Launch the voice command asynchronously, with the text as an argument after `--` and with standard input disconnected. The camera can keep updating during playback.
- **21** Define the operation that stops ongoing playback.
- **22** Check that a process exists and `poll()` reports it is still running.
- **23** Ask the process to terminate.
- **24** Start the block that waits for the process to finish.
- **25** Allow up to one second for termination.
- **26** Handle a process that is still running after that wait.
- **27** Force the process to stop.
- **28** Wait for the stopped process so its resources are reclaimed.
- **30** Define the cleanup that Python runs at the end of the player's `with` block.
- **31** Stop any remaining speech when the app closes.

## `test_camera.py`

- **1** Import `SimpleNamespace` to make a small object with named arguments for the test.
- **2** Import the built-in test framework.
- **3** Import `patch` to substitute predictable results for native window APIs during the test.
- **5** Import the same `Camera` class all four apps use.
- **8** Group the native-window behavior test in a `TestCase` class.
- **9** Define a test for a window that starts hidden, then becomes visible, then closes.
- **10** Construct the camera settings. This test skips entering its context, so actual capture stays closed.
- **11** Open a multi-line context for the three temporary replacements.
- **12** Replace `imshow` so the test opens no window.
- **13** Set the keyboard poll to return `-1`, meaning no key was pressed.
- **14** Simulate a window that is hidden, becomes visible, then closes.
- **15** Start running the test with all three replacements active.
- **16** Confirm that a window still opening keeps the loop running.
- **17** Check that the newly visible window also keeps the loop running.
- **18** Check that the preview signals quit after the visible window closes.
