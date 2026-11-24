# Browser interface, line by line

The page has one video preview and four control panels. The selected URL decides which panel is visible. The browser captures and displays video, packages snapshots, and shows the answers from Python. The landmark links and box styles here describe how to draw a result. The Python chapters explain how the app calculates that result.

Try [Object Motion Lab](http://127.0.0.1:8894/object-motion-lab/) while the server is running. In DevTools, inspect the video, canvas, and WebSocket separately. The visible video plays directly from the camera at its normal rate. An invisible canvas creates a smaller JPEG only when the previous request has finished.

## How the mirror setting travels

**Mirror camera** defaults to on and follows you between modes in the same tab. The browser keeps the JPEG samples in their original orientation. CSS flips the live video and the diagnostic mask. JavaScript uses the matching horizontal reflection for boxes and hand landmarks and redraws the most recent overlay as soon as the setting changes. Labels are drawn normally at their new coordinates. For Kinetic Silhouette, the browser sends a setting to Python. Python reflects the subject and its movement mask at render time, which keeps the motion history and scenery fixed.

## `web/index.html`

### Page setup

- **1** Select standards mode so the browser uses modern HTML and CSS layout rules.
- **2** Set the document language for assistive technology and identify the page as a software interface.
- **3** Open the metadata section.
- **4** Read the source as UTF-8 so punctuation and indicators render consistently.
- **5** Size the viewport to the actual device width for responsive layout.
- **6** Tell the browser that native controls should use a dark palette.
- **7** Give the browser's surrounding chrome a matching dark color where supported.
- **8** Describe the application in document metadata.
- **9** Record the software classification for design review tooling.
- **10** Provide the equivalent site classification metadata.
- **11** Start with the default page title, which JavaScript updates for each mode.
- **12** Use an empty favicon to avoid a separate icon request.
- **13** Load the one stylesheet used on all four pages.
- **14** Load the shared JavaScript as a module, which runs after the page is parsed.
- **15** Ends this `head` element. Following elements are outside it.
- **16** Start the visible document.

### Navigation and camera

- **17** Provide a keyboard shortcut link to skip repeated navigation.
- **18** Start the top site bar.
- **19** Center its contents using the common wrapper.
- **20** Link the brand to the home page and hide its decorative symbol from screen readers.
- **21** Ends this `div` element. Following elements are outside it.
- **22** Ends this `header` element. Following elements are outside it.
- **23** Open the main keyboard target and start with the object mode theme.
- **24** Group the title and description at the top of the mode page.
- **25** Provide the visible title that JavaScript replaces with the selected app title.
- **26** Provide the default explanation of the object mode.
- **27** Ends this `header` element. Following elements are outside it.
- **28** Start a labeled navigation area for the four app modes.
- **29** Open Object Motion Lab and mark it as current for the default page.
- **30** Link to the Gesture Voice Lab mode.
- **31** Link to scene captioning.
- **32** Link to Kinetic Silhouette.
- **33** Ends this `nav` element. Following elements are outside it.
- **34** Start the container for the preview and the selected settings panel.
- **35** Give the live camera region the name of its visible heading.
- **36** Open the panel header that contains the title and camera status.
- **37** Name the preview; the art route changes the text to Particle landscape.
- **38** Display the camera status in a region that assistive technology can announce.
- **39** Ends this `header` element. Following elements are outside it.
- **40** Open the space where video, artwork, or the inactive state appear.
- **41** Create a muted inline video that JavaScript connects to the webcam after permission.
- **42** Reserve the image position for the Python-rendered artwork.
- **43** Create the decorative canvas that draws boxes or hand joints over the video.
- **44** Show instructions until a camera preview becomes visible.
- **45** Add the small camera-shaped marker as a decorative element.
- **46** Explain where the camera appears before the visitor starts it.
- **47** Ends this `div` element. Following elements are outside it.
- **48** Ends this `div` element. Following elements are outside it.
- **49** Group the main camera control and the explanation of frame processing.
- **50** Group the camera button and mirror checkbox so both remain close to the preview.
- **51** Start and stop the live session with a camera button described by the nearby privacy notice.
- **52** Provide a native checkbox, initially checked, for flipping the preview from left to right.
- **53** End the group of camera controls.
- **54** Explain when the browser sends frames and how the session data is handled.
- **55** Ends this `div` element. Following elements are outside it.
- **56** Provide a hidden alert that becomes visible when an error needs attention.
- **57** Ends this `section` element. Following elements are outside it.

### Object and motion controls

- **58** Start the object controls panel that appears on the default route.
- **59** Name the object controls with their displayed heading.
- **60** Start the panel's consistently padded contents.
- **61** Label the control that chooses the kind of detection.
- **62** Open the select element whose value is sent to Python.
- **63** Offer simultaneous object labels and region-based motion.
- **64** Offer named object detection by itself.
- **65** Offer frame differencing without loading the object model.
- **66** Ends this `select` element. Following elements are outside it.
- **67** Ends this `label` element. Following elements are outside it.
- **68** Add the preference for receiving and displaying the motion mask.
- **69** Set aside an initially hidden image for the mask from Python.
- **70** Group the named predictions so the browser can hide them in motion-only mode.
- **71** Label the detected objects readout.
- **72** Show the inactive state until the app begins providing results.
- **73** Give the browser an accessible list to fill with each label and score.
- **74** Ends this `div` element. Following elements are outside it.
- **75** Place the region count in an output named by the surrounding text.
- **76** Ends this `div` element. Following elements are outside it.
- **77** Ends this `section` element. Following elements are outside it.

### Gesture and speech controls

- **78** Start the gesture panel, hidden until its route is selected.
- **79** Name the transcript card.
- **80** Open the body of the gesture panel.
- **81** Explain the hold and release actions needed to add a word.
- **82** Reserve a status line for the recognition hints returned by Python.
- **83** Announce transcript changes politely after a new word is accepted or the sequence clears.
- **84** Group the two transcript action buttons.
- **85** Offer speech once the transcript contains something to read.
- **86** Offer clearing an existing transcript.
- **87** Ends this `div` element. Following elements are outside it.
- **88** Allow the visitor to ask for speech after each accepted word.
- **89** Start a disclosure so the full gesture reference stays accessible without always occupying space.
- **90** Label the disclosure control with the reference it opens.
- **91** Start a list of gesture names and their meanings.
- **92** Displays Peace sign with its vocabulary entry or action, Use.
- **93** Displays One open palm with its vocabulary entry or action, Technology.
- **94** Displays Index finger up with its vocabulary entry or action, For.
- **95** Displays Thumbs up with its vocabulary entry or action, Help.
- **96** Displays Thumbs down with its vocabulary entry or action, Not.
- **97** Displays Closed fist with its vocabulary entry or action, War.
- **98** Displays Index, pinky, and thumb extended with its vocabulary entry or action, I love you.
- **99** Displays Two open palms for 2 seconds with its vocabulary entry or action, Speak sequence.
- **100** Ends this `dl` element. Following elements are outside it.
- **101** Ends this `details` element. Following elements are outside it.
- **102** Ends this `div` element. Following elements are outside it.
- **103** Ends this `section` element. Following elements are outside it.

### Caption controls

- **104** Start the panel for the caption route.
- **105** Give the caption panel its visible name.
- **106** Wrap the caption controls and text.
- **107** Reserve an announced text area for the model output.
- **108** Group the caption buttons.
- **109** Offer capture when the camera connection is ready.
- **110** Offer speech when there is a caption.
- **111** Ends this `div` element. Following elements are outside it.
- **112** Allow repeated captions as an explicit opt-in.
- **113** Give the visitor a status for capture and captioning.
- **114** Ends this `div` element. Following elements are outside it.
- **115** Ends this `section` element. Following elements are outside it.

### Silhouette controls

- **116** Start the silhouette controls, initially hidden.
- **117** Name the silhouette motion panel.
- **118** Open the panel body.
- **119** Explain how movement changes the displayed particle color.
- **120** Reserve the readout that says whether the segmenter found someone.
- **121** Name the measurement and provide a formatted percentage alongside it.
- **122** Set up a visual gauge that accepts the full percentage range.
- **123** Ends this `label` element. Following elements are outside it.
- **124** Allow switching from the particles to the segmentation mask.
- **125** Ends this `div` element. Following elements are outside it.
- **126** Ends this `section` element. Following elements are outside it.
- **127** Ends this `div` element. Following elements are outside it.
- **128** Ends this `main` element. Following elements are outside it.
- **129** Ends this `body` element. Following elements are outside it.
- **130** Ends this `html` element. Following elements are outside it.

## `web/studio.css`

### Theme and base styles

- **1** Open global theme settings on the root HTML element.
- **2** Match the browser's native form controls to the page's dark theme.
- **3** Set a readable base size, line height, and font fallback list.
- **4** Choose a light foreground for the dark page.
- **5** Fill the page behind the interface with its base background.
- **6** Save the panel background as a shared color.
- **7** Save the lighter surface for buttons and controls.
- **8** Save the border and divider color.
- **9** Keep secondary text readable while giving main labels more emphasis.
- **10** Define the green used in the main detection mode.
- **11** Set green as the default accent, which other modes override.
- **12** Closes the current block or expression so execution continues in its enclosing scope.
- **14** Include border and padding in element size calculations.
- **15** Keep hidden elements off the page even when another selector sets their display style.
- **16** Remove default margins so spacing is set deliberately by the interface.
- **17** Make controls inherit the studio's typography.
- **18** Use a pointing cursor on common interactive elements.
- **19** Keep links in the surrounding palette with room under any underline.
- **20** Draw a visible outline when someone reaches a control by keyboard.
- **21** Use the current mode's color when highlighting selected text.
- **22** Center the layout and give it both an upper width and page gutters.
- **23** Place the keyboard skip link above the top bar when shown.
- **24** Hide the link visually until keyboard focus reaches it.

### Navigation

- **26** Delimit the top bar with a divider.
- **27** Vertically align the bar contents in a consistent height.
- **28** Align the logo and name and present them as one navigation target.
- **29** Shape a small rounded camera outline for the brand mark.
- **30** Draw its lens as a centered CSS pseudo-element.
- **32** Give the main content vertical space beneath the bar.
- **33** Assign the warm accent to gesture controls.
- **34** Assign the lavender accent to captioning.
- **35** Assign the cool blue accent to silhouette art.
- **36** Leave space between the introduction and navigation.
- **37** Define the prominent title's size and compact letter spacing.
- **38** Space the short description below the title and mute its color.
- **39** Lay the mode links out in a wrapping row.
- **40** Start styles shared by links, buttons, and the select control.
- **41** Keep targets tall enough to click or tap.
- **42** Add vertical and horizontal spacing inside the controls.
- **43** Outline each target using the standard border color.
- **44** Give the controls small rounded corners.
- **45** Fill controls with the raised surface color.
- **46** Reuse the current foreground color.
- **47** Set control labels slightly smaller than body text.
- **48** Keep the labels easy to scan with a stronger weight.
- **49** Closes the current block or expression so execution continues in its enclosing scope.
- **50** Center the nav text and use a quieter treatment for inactive modes.
- **51** Highlight the current mode using the accent and raised surface.
- **52** Give interactive targets visible hover feedback.
- **53** Make Start camera prominent and keep its label on one line.
- **54** Use a quieter style for the same control while it says Stop camera.
- **55** Dim disabled controls and show the regular cursor.

### Camera and results

- **57** Give most of the desktop width to the preview and a narrower column to controls.
- **58** Style panels consistently and clip their contents to the rounded edges.
- **59** Arrange each panel's title and status with a divider underneath.
- **60** Style compact panel titles consistently.
- **61** Align the camera state text with its indicator.
- **62** Draw a small neutral status dot without adding a separate HTML element.
- **63** Turn the dot green while capture and processing are active.
- **64** Use amber while camera startup or connection setup is pending.
- **66** Reserve a wide preview area before there is any camera image.
- **67** Stack video, boxes, and artwork over the same area, fitting images without distortion.
- **68** Keep the overlay canvas from blocking input events.
- **69** Reflect the video and the motion-mask image around their centers when the page marks mirroring active. Canvas labels are drawn separately.
- **70** Use the particle scene's darker background after the art view appears.
- **71** Move live video to the corner as a small reference preview over the artwork.
- **72** Center and style the inactive-camera prompt.
- **73** Render a simple rounded camera body for that prompt.
- **74** Add the circular lens with CSS.
- **75** Place the camera button and notice below the preview.
- **76** Align the Start and Mirror controls and allow them to wrap on narrow screens.
- **77** Show an error below the toolbar in a distinguishable text color.
- **79** Pad the right-hand panel and space its controls vertically.
- **80** Give hints muted color and readable line spacing.
- **81** Stack field names above their inputs.
- **82** Align a checkbox and its label as one generous touch target.
- **83** Dim the usable area of a disabled checkbox.
- **84** Set checkbox dimensions and use the current app color.
- **85** Constrain the mask image to a compact preview without distorting it.
- **86** Emphasize current results and allow long output to wrap.
- **87** Set panel subsection headings and disclosures apart from supporting text.
- **88** Add a small gap before the text below the object list heading.
- **89** Make a long list of predictions scroll within the panel.
- **90** Align each object row into a color chip, label, and right-hand score.
- **91** Draw the color chip using the same category color as the canvas box.
- **92** Align the motion label and count at opposite ends of their row.
- **93** Give numeric output steady widths so changing values move less.
- **94** Keep the transcript readable, with light separators and wrapping.
- **95** Let adjacent action buttons wrap on narrow panels.
- **96** Give the expandable gesture reference a reachable target.
- **97** Space the entries in the gesture dictionary.
- **98** Lay each gesture and its word out next to one another.
- **99** Mute the gesture description relative to the output word.
- **100** Size the body movement gauge to use the panel's available width.
- **101** Use the art color for the meter fill in compatible browsers.

### Motion preferences and smaller screens

- **103** Only add these transitions when motion preferences allow them.
- **104** Give short transitions to hover and press feedback.
- **105** Shift the pressed target down slightly without moving the layout.
- **106** Closes the current block or expression so execution continues in its enclosing scope.
- **108** Apply a single-column layout at tablet and smaller widths.
- **109** Reduce the side margins to leave more room for the content.
- **110** Put the controls panel below the camera preview.
- **111** Closes the current block or expression so execution continues in its enclosing scope.
- **113** Apply additional compact spacing on phones.
- **114** Reduce margins further to preserve the preview's width.
- **115** Shorten the top bar slightly.
- **116** Move the page contents closer to the header.
- **117** Reduce the title size so headings fit on phones.
- **118** Tighten the vertical space below the introduction.
- **119** Keep the description comfortable at the smaller size.
- **120** Arrange the four app links as a two-column grid.
- **121** Allow each link to shrink within its grid cell and center wrapped labels.
- **122** Keep the preview useful even at narrow widths.
- **123** Stack the camera notice below the Start button.
- **124** Closes the current block or expression so execution continues in its enclosing scope.

## `web/studio.js`

- **1** Import the shared coordinate transforms, which the browser uses for drawing and Node.js uses for tests.

### Choose a mode

- **3** Start the route metadata shared by all app pages.
- **4** Map the object route to its panel, title, and brief instructions.
- **5** Map the gesture route to its word-sequence panel.
- **6** Map the caption route to the snapshot view.
- **7** Map the silhouette route to the particle scene.
- **8** Closes the current block or expression so execution continues in its enclosing scope.
- **9** Read the last URL segment and default to the object route on the home page.
- **10** Unpack the metadata the route controls.
- **11** Define a small helper to look up elements by their IDs.
- **12** Keep the root of the interactive interface for theme and navigation changes.
- **13** Reference the video that will receive the live browser stream.
- **14** Find the canvas that appears above the live preview.
- **15** Get a drawing context for the visible canvas.
- **16** Create a separate off-page canvas for sampling images.
- **17** Use an opaque drawing surface for JPEGs.
- **18** Keep the camera indicator available for live status updates.
- **19** Find the button that starts and stops a session.
- **20** Find the camera mirror checkbox in the shared toolbar.
- **21** Find the image used for the motion-mask preview.
- **22** Find the image that will show Python's artwork.
- **23** Find the list that receives object predictions.
- **24** Find the gesture transcript in the layout.
- **25** Find the readout for the most recent caption.
- **26** Find the checkbox that enables repeated captions.
- **27** Name the per-tab storage key that carries camera orientation between routes.
- **28** Define a stable palette for object categories.
- **29** Define which MediaPipe joint indexes to connect while drawing.
- **30** Finish the display paths along the remaining fingers and palm.
- **31** Start with no active camera or WebSocket session.
- **32** Start without text available to speak.
- **33** Start without a cached overlay result.
- **35** Attempt to restore the camera preference before building the first preview.
- **36** Use the saved choice, with mirroring enabled by default.
- **37** Catch cases where browser policy blocks session storage.
- **38** Explain why the checkbox keeps its local behavior without storage.
- **39** Close the optional preference restore.
- **41** Apply the mode name for CSS accent styling.
- **42** Set the browser tab title.
- **43** Show the selected app's title in the page header.
- **44** Show the matching description in the introduction.
- **45** Give the art stage a different title because its main content is rendered art.
- **46** Check each of the app navigation links.
- **47** Mark the matching route so keyboard and screen-reader users can identify the current page.
- **48** Clear the current-page marker on the other links.
- **49** Closes the current block or expression so execution continues in its enclosing scope.
- **50** Show just the selected controls panel.

### Status and cleanup

- **52** Define a helper that displays or clears an error.
- **53** Set alert content as text so an error message is just text.
- **54** Hide the empty alert.
- **55** Closes the current block or expression so execution continues in its enclosing scope.
- **57** Define a helper for status text and its indicator color.
- **58** Set the state that the stylesheet reads.
- **59** Show the human-readable status label.
- **60** Closes the current block or expression so execution continues in its enclosing scope.
- **62** Define when to enable snapshot and speech controls.
- **63** Allow capture only on a ready connection with no snapshot pending.
- **64** Allow caption playback when there is text to read.
- **65** Closes the current block or expression so execution continues in its enclosing scope.
- **67** Define the shared renderer for gesture transcript updates.
- **68** Join the words with spaces or prepare the empty-state message.
- **69** Update the announced text only when it changes to avoid repeated announcements.
- **70** Enable clearing if the transcript has words.
- **71** Enable speech for the same condition.
- **72** Closes the current block or expression so execution continues in its enclosing scope.
- **74** Define how to return the view to its inactive state.
- **75** Forget the old drawing data so a mirror change cannot resurrect a stopped camera session.
- **76** Hide the live video.
- **77** Hide the annotations along with it.
- **78** Hide the silhouette image.
- **79** Remove the old artwork source so it is not carried into the next session.
- **80** Hide the diagnostic image.
- **81** Remove the old mask source.
- **82** Return the stage to its normal preview layout.
- **83** Show the prompt before the camera starts.
- **84** Clear the displayed object predictions.
- **85** Restore the inactive object status.
- **86** Reset the numeric motion readout.
- **87** Reset the gesture status.
- **88** Clear the transcript view and disable its actions.
- **89** Reset the art status.
- **90** Set the movement gauge to zero.
- **91** Set the visible percentage to match the gauge.
- **92** Forget the caption available for speech.
- **93** Clear the last caption from the display.
- **94** Restore the prompt for a new camera connection.
- **95** Refresh the caption controls after clearing their state.
- **96** Closes the current block or expression so execution continues in its enclosing scope.
- **98** Stop a session and optionally show a reason.
- **99** Keep a reference to the connection and camera that need closing.
- **100** Invalidate the session at once so late asynchronous callbacks cannot restart it.
- **101** Only close resources when a session object exists.
- **102** Cancel the pending frame timer.
- **103** Cancel the timer for a slow server connection.
- **104** Close the WebSocket if it has been created.
- **105** Stop every camera track if permission already returned a stream.
- **106** Closes the current block or expression so execution continues in its enclosing scope.
- **107** Detach the last stream from the video element.
- **108** Stop any queued browser speech.
- **109** Reset the preview and readouts.
- **110** Return the main button to the start action.
- **111** Restore its inactive styling.
- **112** Show the camera-off state with the appropriate error styling.
- **113** Show any failure or clear the alert on an ordinary stop.
- **114** Closes the current block or expression so execution continues in its enclosing scope.

### Settings, speech, and sampling

- **116** Define the shared path for sending a small JSON control message.
- **117** Confirm the active session and WebSocket are ready before sending.
- **118** Serialize the control separately from the image uploads.
- **119** Closes the current block or expression so execution continues in its enclosing scope.
- **120** Closes the current block or expression so execution continues in its enclosing scope.
- **122** Translate the selected controls into Python settings.
- **123** Read the currently selected object and motion mode.
- **124** Disable the mask control when motion processing is disabled.
- **125** Hide a currently visible mask when it is turned off.
- **126** Send detection mode and mask settings for Object Motion Lab.
- **127** Send the speech preference for Gesture Voice Lab.
- **128** Send the silhouette settings, including the preview orientation, so Python can reflect the drawn person.
- **129** Finish sending the current mode settings.
- **131** Apply the checkbox state to the current camera and results.
- **132** Switch the CSS state for the video and motion-mask images.
- **133** Redraw the last box or landmarks immediately so they move with the flipped preview.
- **134** For the silhouette, send the new orientation to the Python renderer.
- **135** End the shared mirror update.
- **137** Define how a returned phrase is spoken in the visitor's browser.
- **138** Skip empty speech requests.
- **139** Check that the browser exposes both parts of its speech API.
- **140** Show a readable message if the API is unavailable.
- **141** Return before attempting playback in that case.
- **142** Closes the current block or expression so execution continues in its enclosing scope.
- **143** Stop existing speech to avoid overlapping phrases.
- **144** Create and play a new utterance from the supplied text.
- **145** Closes the current block or expression so execution continues in its enclosing scope.
- **147** Schedule one future sample for this session.
- **148** Cancel any prior scheduled sample.
- **149** Create a timer to invoke the frame sender.
- **150** Closes the current block or expression so execution continues in its enclosing scope.
- **152** Decide when the app next needs a frame.
- **153** Give a streaming mode a short pause after a response.
- **154** For captions, schedule another snapshot only while auto is enabled.
- **155** Closes the current block or expression so execution continues in its enclosing scope.
- **157** Define the code that samples and sends one frame.
- **158** Ignore stale, unready, and already busy sessions.
- **159** Cancel the existing scheduled request before capturing now.
- **160** Check that the video has pixels and that earlier bytes have left the socket queue.
- **161** Try again shortly while video or transport is still becoming ready.
- **162** Skip the rest of the function until that retry.
- **163** Closes the current block or expression so execution continues in its enclosing scope.
- **164** Scale the uploaded image to fit within 640 by 480 while preserving its shape.
- **165** Set the sampling canvas width and keep it above the minimum dimension.
- **166** Set the matching height for the source image.
- **167** Copy a frame from the video into the sampling canvas.
- **168** Reserve the active request before starting asynchronous JPEG encoding.
- **169** Disable Describe while the caption request is pending.
- **170** Report when the caption job is about to be sent.
- **171** Ask the browser to produce the compressed image in the background.
- **172** Ignore a late JPEG after the visitor stops or the connection closes.
- **173** Send the JPEG as a binary WebSocket message.
- **174** Treat a failed encoding as an error and stop this capture session.
- **175** Choose JPEG and a quality that balances detail with transfer size.
- **176** Closes the current block or expression so execution continues in its enclosing scope.

### Display model results

- **178** Define a deterministic palette choice for a label.
- **179** Sum the category's character values.
- **180** Reduce that number into a valid palette index.
- **181** Closes the current block or expression so execution continues in its enclosing scope.
- **183** Draw an already detected box and a title on the overlay.
- **184** Extract its position and size in frame coordinates.
- **185** Reflect and clip both horizontal box edges using the current checkbox state. The returned edges keep the outline and label aligned.
- **186** Clip its top edge.
- **187** Clip its bottom edge to the sampled height.
- **188** Skip a rectangle whose visible area has disappeared.
- **189** Apply the selected outline color.
- **190** Choose a two-pixel outline.
- **191** Draw the clipped rectangle.
- **192** Scale the label text for the current video size while keeping a minimum size.
- **193** Measure the label and leave room for padding.
- **194** Keep the filled tag near the box without running over the right edge.
- **195** Place the tag above its box if there is room.
- **196** Match the tag background to the box outline.
- **197** Paint the tag background behind the label.
- **198** Choose dark text for contrast on the colored tag.
- **199** Center the label text vertically relative to its baseline.
- **200** Paint the label with its horizontal and vertical padding.
- **201** Closes the current block or expression so execution continues in its enclosing scope.
- **203** Draw the landmarks returned by the gesture session.
- **204** Choose the warm color for the skeleton.
- **205** Choose a lighter color for the joints.
- **206** Set consistent line weight.
- **207** Process each recognized hand independently.
- **208** Scale each landmark into canvas pixels and apply the same horizontal reflection as the camera.
- **209** Follow each predefined visual connection path.
- **210** Start a canvas path for a connected group of joints.
- **211** Begin at the path's first joint.
- **212** Join the remaining joints with straight segments.
- **213** Paint the connected line.
- **214** Closes the current block or expression so execution continues in its enclosing scope.
- **215** Draw one marker for each of the model's points.
- **216** Start a fresh shape for the point marker.
- **217** Make a small circle centered on the landmark.
- **218** Fill the marker.
- **219** Closes the current block or expression so execution continues in its enclosing scope.
- **220** Closes the current block or expression so execution continues in its enclosing scope.
- **221** Closes the current block or expression so execution continues in its enclosing scope.
- **223** Draw the returned boxes and update the object panel.
- **224** Draw motion areas with a green outline and the Motion label.
- **225** Build one accessible list row for each confirmed object.
- **226** Find the category's display color.
- **227** Convert confidence on a zero-to-one scale to a rounded percentage.
- **228** Paint the matching box and label over the video.
- **229** Create the list row for the sidebar.
- **230** Add an element for the name.
- **231** Add an element for the score.
- **232** Set the category as text.
- **233** Set the percentage as text.
- **234** Share the box color with the list row's CSS marker.
- **235** Insert the two values into the row.
- **236** Return the row from the mapping operation.
- **237** Closes the current block or expression so execution continues in its enclosing scope.
- **238** Replace old list rows with the current result.
- **239** Check the requested detection mode in the interface.
- **240** Hide the object list in Motion only.
- **241** Hide the motion statistic in Objects only.
- **242** Distinguish between a visible result and a frame with no confirmed object.
- **243** Show how many motion boxes Python returned.
- **244** Show the mask only if it exists and the current controls request it.
- **245** Assign the server's image URL when the mask is visible.
- **246** Closes the current block or expression so execution continues in its enclosing scope.
- **248** Draw a result onto the video overlay. The mirror toggle can invoke this drawing without replaying speech or other result side effects.
- **249** Set the result width, which also clears the previous drawing.
- **250** Match the vertical canvas dimension to the input image.
- **251** Show the canvas above the video once a result is available.
- **252** Draw returned boxes when presenting the object and motion app.
- **253** Draw returned hand landmarks when presenting the gesture app.
- **254** Finish drawing the overlay.
- **256** Route one processed frame to the selected app renderer.
- **257** Check whether this mode draws annotations over the camera.
- **258** Save the latest result so a change in orientation can redraw it immediately.
- **259** Draw the result with the current mirror preference.
- **260** End the overlay branch.
- **261** Select the gesture renderer on its route.
- **262** Display the recognition or hold-progress message.
- **263** Update the transcript from the session's response.
- **264** Speak a returned automatic or two-palms request.
- **265** Closes the current block or expression so execution continues in its enclosing scope.
- **266** Select the caption display on its route.
- **267** Keep the returned caption for the Speak button.
- **268** Put the caption text on screen.
- **269** Confirm the request is complete.
- **270** Re-enable capture and make caption speech available.
- **271** Closes the current block or expression so execution continues in its enclosing scope.
- **272** Select the silhouette display on its route.
- **273** Set the Python-rendered image as the artwork source.
- **274** Reveal the scene once the first result arrives.
- **275** Switch the stage style to the composition with a small camera preview.
- **276** Use the model's presence flag to guide the visitor.
- **277** Update the motion gauge.
- **278** Show the percentage rounded to one decimal place.
- **279** Closes the current block or expression so execution continues in its enclosing scope.
- **280** Closes the current block or expression so execution continues in its enclosing scope.

### Handle messages from Python

- **282** Interpret one message received on the camera connection.
- **283** Ignore callbacks belonging to an older session.
- **284** Read the JSON event from the Python app.
- **285** Handle the signal that processing can begin.
- **286** Cancel the connection startup timeout.
- **287** Mark this socket ready for messages.
- **288** Report that the app has an active camera and processor.
- **289** Apply the visible preferences before the first processed frame.
- **290** Update the snapshot and speech buttons for the active connection.
- **291** Set up the caption mode separately from continuous sampling.
- **292** Tell the visitor they may request a caption.
- **293** Capture immediately if automatic captions were already selected.
- **294** Handle every continuous mode in the other branch.
- **295** Send the initial video snapshot.
- **296** Closes the current block or expression so execution continues in its enclosing scope.
- **297** Handle the response for an earlier JPEG.
- **298** Allow another frame to be sent.
- **299** Display the result appropriate to the current route.
- **300** Schedule the next sample if the mode needs one.
- **301** Handle a response to the gesture Clear or Speak controls.
- **302** Apply the returned transcript.
- **303** Speak any text requested by the control.
- **304** Handle a reported Python error.
- **305** Clear the pending flag so an unsuccessful request does not block forever.
- **306** Release the camera and show the server's error if it cannot recover.
- **307** Use the following branch for errors after which the connection can keep working.
- **308** Show the recovery message.
- **309** Refresh buttons after clearing the outstanding request.
- **310** Give caption users a chance to take another snapshot.
- **311** Resume the sampling schedule under the current mode and settings.
- **312** Closes the current block or expression so execution continues in its enclosing scope.
- **313** Closes the current block or expression so execution continues in its enclosing scope.
- **314** Closes the current block or expression so execution continues in its enclosing scope.

### Start and stop capture

- **316** Start the asynchronous camera permission and WebSocket setup.
- **317** Make a fresh object to identify this startup and its readiness.
- **318** Register it as the currently active session.
- **319** Clear any error from the previous attempt.
- **320** Let the user cancel during startup using the same button.
- **321** Change the button's visual state.
- **322** Report that camera startup is underway.
- **323** Start handling late permission outcomes and startup failures.
- **324** Check that the browser's camera API is present.
- **325** Explain the HTTPS or loopback requirement when it is missing.
- **326** Closes the current block or expression so execution continues in its enclosing scope.
- **327** Ask the browser for webcam permission and wait for the stream.
- **328** Request video only.
- **329** Request the front camera and give preferred dimensions for capture.
- **330** Closes the current block or expression so execution continues in its enclosing scope.
- **331** Check whether the user stopped while the permission request was pending.
- **332** Release a late stream immediately.
- **333** Exit startup for the session that was already cancelled.
- **334** Closes the current block or expression so execution continues in its enclosing scope.
- **335** Record the stream so Stop camera can release it later.
- **336** Watch each camera track for an external stop such as a disconnected device.
- **337** Stop this session and tell the visitor how to reconnect if that track ends.
- **338** Closes the current block or expression so execution continues in its enclosing scope.
- **339** Connect the local stream directly to the video element.
- **340** Ask the video to start playing and wait until it can render.
- **341** Discard the result if the session ended while playback was starting.
- **342** Reveal the camera in the stage.
- **343** Hide the inactive-camera prompt.
- **344** Report that the local preview is available and the Python connection is starting.
- **345** Use encrypted WebSockets when the app itself is served over HTTPS.
- **346** Connect to the same host and the selected mode's WebSocket path.
- **347** Pass the server's messages to the handler with this session's identity.
- **348** Watch for the socket closing unexpectedly.
- **349** Release the camera and advise reconnecting if this is still the active session.
- **350** Closes the current block or expression so execution continues in its enclosing scope.
- **351** Start a connection timeout so startup cannot hang indefinitely.
- **352** Handle a server that fails to become ready in time.
- **353** Give model and connection startup up to 45 seconds.
- **354** Handle camera access or video startup failures.
- **355** Ignore errors from a session that already ended.
- **356** Explain permission denial and preserve the browser's message for other failures.
- **357** Stop camera resources and show either the available error or a generic fallback.
- **358** Closes the current block or expression so execution continues in its enclosing scope.
- **359** Closes the current block or expression so execution continues in its enclosing scope.
- **361** Bind the main button to Start or Stop according to the current session.
- **362** Listen for user changes to the mirror checkbox.
- **363** Apply the new orientation before storing it.
- **364** Attempt to persist this choice within the current browser tab.
- **365** Store the checked state as text for the next mode loaded in this tab.
- **366** Tolerate browsers that restrict session storage.
- **367** Explain that the active page still supports mirroring in restricted browsers.
- **368** End the optional preference save.
- **369** Finish attaching the mirror event.
- **370** Apply the restored or default mirror state as the page initializes.
- **371** Locate each control that changes an option in Python.
- **372** Send updated settings whenever a listed control changes.
- **373** Closes the current block or expression so execution continues in its enclosing scope.
- **374** Sample a frame for a manual caption request.
- **375** Speak the last received caption when requested.
- **376** Ask this gesture session to clear its transcript.
- **377** Ask this gesture session for the text to speak.
- **378** Respond to enabling or disabling automatic descriptions.
- **379** Wait for Start camera if there is no session to manage.
- **380** Clear any sample scheduled under the earlier settings.
- **381** Capture immediately when enabling automatic captions on an active session.
- **382** Closes the current block or expression so execution continues in its enclosing scope.
- **383** Release the camera and WebSocket when the visitor navigates away.

## `web/mirror.mjs`

The browser reuses these pure functions for its canvas. The Node.js tests import the same file.

- **1** Define a horizontal projection that can be reused for individual landmark coordinates or box edges.
- **2** Keep a coordinate as-is when mirroring is off. When on, subtract its position from the full frame width.
- **3** End the coordinate projection.
- **5** Define the helper that returns a box’s visible left and right sides in preview coordinates.
- **6** Project the original left edge using the same reflection as a landmark.
- **7** Project the original right edge. Reflection reverses the order of the two edges.
- **8** Order the reflected edges and clamp them to the visible frame. Keeping the edges ordered lets the canvas draw left to right even while the video is mirrored.
- **9** End the bounds helper.

## `test_mirror.test.mjs`

Run these focused checks with `node --test test_mirror.test.mjs`.

- **1** Import Node.js strict assertions for numbers and arrays.
- **2** Import the built-in Node.js test runner.
- **3** Import the exact geometry helpers used by the browser overlay.
- **5** Start a test for an isolated horizontal point, such as a hand joint.
- **6** Check the mirrored location of a known point in a 640-pixel image.
- **7** Check that disabling the mirror preserves the source coordinate.
- **8** End the point test.
- **10** Test how both edges of a box move in the preview.
- **11** Verify that the reflected bounds remain sorted and keep the original width.
- **12** Verify that unmirrored bounds match the original position.
- **13** End the rectangle test.
- **15** Test a rectangle that extends beyond the left edge before reflection.
- **16** Confirm that reflection moves the overflow to the right and clips it.
- **17** Confirm that normal orientation clips the overflow on the left.
- **18** End the clipping test.
