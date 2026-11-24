# Python web server, line by line

The four app URLs serve the same page. A WebSocket keeps the Python session alive between frames so the processor can compare a frame with its predecessor or remember which word was just added. Each connection has its own session. The caption model is loaded once per server process and shared because it generates each caption from just one frame.

Follow [web_server.py](web_server.py) while the app is running. In Chrome DevTools, open Network, select the WebSocket, and inspect the messages. The browser sends binary JPEGs and JSON control messages. Python replies with dimensions and coordinates, text, or encoded artwork. None of those messages goes into a database.

## `web_server.py`

### Dependencies

- **1** Import the async event loop, timeout, and synchronization tools.
- **2** Import Base64 so binary images can be included in a JSON response.
- **3** Import JSON parsing for text controls such as changing modes.
- **4** Import logging for terminal diagnostics on processing errors.
- **5** Import a helper for startup and shutdown and a helper that ignores expected close errors.
- **6** Import BytesIO to read a JPEG from memory as if it were a file.
- **7** Import Path so the static directory can be found regardless of the working directory.
- **8** Import a clock that increases steadily for motion and gesture timing.
- **10** Import OpenCV for color conversion, resizing, and response images.
- **11** Import NumPy to turn a decoded picture into a pixel array.
- **12** Import the ASGI server that runs the application.
- **13** Import FastAPI, its HTTP and WebSocket interfaces, and the disconnect exception.
- **14** Import FileResponse to return the same HTML file for each app.
- **15** Import StaticFiles to serve the browser stylesheet and script.
- **16** Import Pillow's image reader for size and type checks before decoding pixels.
- **17** Import the helper that runs CPU-bound or blocking functions off the event loop.
- **19** Import the gesture session also used by the desktop command.
- **20** Import the silhouette session, including the Python particle renderer.
- **21** Import the combined object and motion processor used by both adapters.
- **22** Import the Python caption generator from the desktop caption module.

### Routes and shared resources

- **25** Find the web folder alongside this server file.
- **26** Name the route and socket mode for Object Motion Lab.
- **27** Name the route for Gesture Voice Lab.
- **28** Name the caption mode, which processes individual snapshots.
- **29** Name the silhouette mode.
- **30** Associate the modes that need per-camera history with their class constructors.
- **31** Form the complete set of valid routes by including captioning.
- **32** Set 512 KiB as the largest incoming WebSocket message.
- **33** Send server exceptions to the normal Uvicorn log.
- **36** Mark the next function as an asynchronous context manager used by FastAPI.
- **37** Define what should be created once when the application starts.
- **38** Create a captioner that loads its weights when first used.
- **39** Allow a single caption inference at once, including during the first model load.
- **40** Reserve at most four active sessions, limiting simultaneous model work on this server.
- **41** Let FastAPI serve requests while those resources are in scope.
- **44** Create the web app with its startup hook and a small surface of HTTP routes.
- **45** Make the single browser interface's files available under /static.
- **48** Register the home route, which opens object detection by default.
- **49** Also register a route that takes the mode name from the URL.
- **50** Define the handler for both kinds of requests.
- **51** Check that the requested mode is a supported app.
- **52** Return a 404 when the path names an unknown app.
- **53** Send the same index.html. Its script uses the URL to choose the panel.

### Images and control messages

- **56** Define how an incoming frame is read.
- **57** Reject missing data and messages larger than the server limit.
- **58** Signal that the client should send a single frame inside the limit.
- **59** Start decoding with errors handled by the block below.
- **60** Open an in-memory stream and tell Pillow to accept JPEG input.
- **61** Check width and height from the image header before reading its pixels.
- **62** Explain the maximum accepted dimensions.
- **63** Decode the image in RGB and expose its pixels as a NumPy array.
- **64** Treat unreadable data and oversized image headers as invalid frames.
- **65** Convert those library errors into a short client-facing frame error.
- **66** Convert RGB to BGR because the shared OpenCV pipelines use BGR.
- **69** Define how a returned mask or artwork becomes an image URL.
- **70** Encode the pixels into the requested compressed image format.
- **71** Check OpenCV's status before using the compressed buffer.
- **72** Raise a processing error if OpenCV did not produce an image.
- **73** Encode the compressed bytes as text the browser can assign to an image source.
- **76** Run the vision session and prepare its result for the wire.
- **77** Run the same frame processor as the desktop app.
- **78** Check whether object motion produced a mask for display.
- **79** Preserve the mask's black-and-white pixels with a lossless PNG.
- **80** Check whether the result includes a rendered silhouette scene.
- **81** Reduce the image dimensions for transport, keeping the 16:9 aspect ratio.
- **82** Compress the artwork as a JPEG so it can update repeatedly.
- **83** Return the result with image strings in place of raw arrays.
- **86** Define how to interpret an incoming text command.
- **87** Parse the message into a Python value.
- **88** Require a JSON object with named fields.
- **89** Reject strings, arrays, and other unsupported command structures.
- **90** Read the action field to decide what the visitor requested.
- **91** Handle configuration changes without processing an image.
- **92** Apply this group only to the object and motion app.
- **93** Use the supplied mode or keep the current mode if omitted.
- **94** Check that the new view is one of the three supported choices.
- **95** Return a useful error before changing the session on invalid input.
- **96** Update the session's processing mode.
- **97** Update the mask setting using a JSON Boolean.
- **98** Check whether the active app is Gesture Voice Lab.
- **99** Change whether the next accepted word should be spoken automatically.
- **100** Check whether the active app is Kinetic Silhouette.
- **101** Switch its renderer between the particles and segmentation mask.
- **102** Read the silhouette mirror setting as a Boolean and preserve the previous choice when the field is absent.
- **103** Indicate that changing a setting needs no separate acknowledgment.
- **104** Recognize the gesture transcript's Clear and Speak actions.
- **105** Decide whether the action removes words.
- **106** Clear only the connected session's transcript.
- **107** Return an event with a copy of the current words.
- **108** Include the phrase to say only for the Speak action.
- **109** Reject an unsupported action with a recoverable error.

### Open a session and process a frame

- **112** Define how a new socket gets its processor.
- **113** Find the constructor for this mode if it owns state.
- **114** Open that session. Captions use the shared model instead.
- **117** Define the camera JPEG to response path.
- **118** Decode JPEG bytes in a worker thread so other tabs stay responsive.
- **119** Choose the snapshot path for captions.
- **120** Serialize the use of the shared caption model.
- **121** Generate the caption in a worker thread.
- **122** Put the resulting text into the response.
- **123** For the three live modes, use the per-tab processor instead.
- **124** Process and encode the result in a worker thread with a sample time.
- **125** Read the real dimensions so the browser can align its overlay.
- **126** Combine the response type, dimensions, and output fields.

### The connection loop

- **129** Register one WebSocket endpoint that selects an app by route name.
- **130** Define what the server will do for that connection.
- **131** Read the host the client connected to.
- **132** Read the origin of the page that opened the connection.
- **133** Allow the known modes on pages served from the same host.
- **134** Reject unexpected modes and page origins before processing images.
- **135** Stop handling rejected connections.
- **137** Accept the valid WebSocket handshake.
- **138** Read application resources created at startup.
- **139** Get the limiter shared by all connections.
- **140** Check whether the server already has its allowed number of active sessions.
- **141** Send a clear error if that capacity is in use.
- **142** Close the extra connection with a retry-later protocol code.
- **143** Return without creating a model session.
- **145** Reserve a slot until this connection finishes.
- **146** Start without any opened per-connection resources.
- **147** Start a block that will clean up even if startup or frame processing fails.
- **148** Create the vision session in a worker thread, where model loading can block safely.
- **149** Tell the browser it can start sending frames and controls.
- **150** Reuse this connection for as long as the visitor's camera session is active.
- **151** Wait for a browser message and stop the session after three idle minutes.
- **152** Check whether the visitor closed the connection.
- **153** Return through cleanup when the connection ends.
- **154** Keep recoverable invalid-input handling local to one incoming message.
- **155** If the message carries bytes, treat it as one camera snapshot.
- **156** Remove the raw JPEG from the packet and process it into the browser response.
- **157** Use the other route for text messages.
- **158** Apply the requested control to this visitor's session.
- **159** Some controls change state without returning a message.
- **160** Send the processed result or the requested gesture transcript update.
- **161** Handle invalid input without closing the camera.
- **162** Use a readable message if parsing failed, or explain the specific input problem.
- **163** Return an error the browser can show while allowing a retry.
- **164** Catch a disconnect raised while interacting with the socket.
- **165** Let normal disconnects go straight to cleanup.
- **166** Handle the idle timeout separately.
- **167** Ignore send errors if the connection has already been closed.
- **168** Tell a still-connected visitor to restart the camera when returning.
- **169** Handle unexpected server and model errors.
- **170** Log the exception and app name for troubleshooting.
- **171** Avoid a second error if the connection disappeared while inference was running.
- **172** Return a fatal processing message that makes the client stop the camera.
- **173** Begin the cleanup that runs for every exit path.
- **174** Ensure socket closure still happens if closing the model raises an error.
- **175** Check whether this mode actually opened a session.
- **176** Release its native model and let frame history go out of scope.
- **177** Close the WebSocket after the session cleanup.
- **178** Ignore close errors for an already disconnected visitor.
- **179** Send the WebSocket close message if the connection can still receive it.
- **182** Run this entry point when launching the script directly.
- **183** Bind to loopback port 8894 and cap WebSocket message size and the receive queue.

## `test_web_server.py`

- **1** Import Python's built-in unit test framework.
- **3** Import OpenCV to encode test images as JPEGs.
- **4** Import NumPy so the tests can generate predictable pixel arrays.
- **5** Import FastAPI's in-process client for HTTP and WebSocket testing.
- **6** Import the exception raised when a WebSocket is closed.
- **8** Import the production app, decoder, object route name, and byte limit.
- **11** Use the matching origin that a request to the test app would carry.
- **12** Build the WebSocket path for Object Motion Lab.
- **15** Define a helper for sending generated frames through the real protocol.
- **16** Encode one image as a JPEG using OpenCV.
- **17** Confirm that test encoding succeeded before using the output.
- **18** Return the JPEG as raw bytes.
- **21** Group browser transport tests that run without a camera.
- **22** Verify the decoder's shape, colors, and validation.
- **23** Create a frame where the blue channel has a known strong value.
- **24** Use the real decoder on the encoded frame.
- **25** Check that the output has the expected height, width, and color channels.
- **26** Confirm that the decoded blue remains in OpenCV's first channel after compression.
- **27** Expect a decoding error for an image with invalid dimensions.
- **28** Submit a JPEG one row taller than the protocol allows.
- **29** Expect a decoding error for a message that is too big.
- **30** Submit enough bytes to exceed the transport cap.
- **32** Verify that two separate connections get distinct motion histories and can handle malformed input.
- **33** Allocate a plain black image as a motion baseline.
- **34** Make a second frame independently of the first image.
- **35** Fill a white rectangle to create a substantial brightness change.
- **36** Start the app and open its first same-origin WebSocket.
- **37** Check that the server reports the session is ready.
- **38** Select motion-only mode with mask output, which uses no AI model.
- **39** Send invalid image bytes to exercise a recovery path.
- **40** Verify that the error is recoverable.
- **41** Send the first proper baseline frame.
- **42** Verify that the first frame produces zero motion.
- **44** Open a second simultaneous WebSocket.
- **45** Verify that the new connection has a fresh ready event.
- **46** Select the motion-only mode on the second connection.
- **47** Send the image containing the white rectangle to this fresh session.
- **48** Confirm the second session treats it as its own baseline.
- **50** Send the same white rectangle to the first session, which previously saw black.
- **51** Read the real WebSocket response.
- **52** Verify the output dimensions match the frame.
- **53** Confirm that the first history produces one motion region.
- **54** Confirm its optional binary mask arrives as a PNG data URL.
- **56** Check that the server refuses to accept a socket from another website.
- **57** Start the app and expect a WebSocket disconnect.
- **58** Try to connect using an unrelated page origin.
- **59** Fail the test if the connection establishes successfully.
- **60** Check the close code used for invalid protocol policy.
