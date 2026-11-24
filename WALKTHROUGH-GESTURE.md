# Gesture Voice Lab, line by line

Run `.venv/bin/python gesture_voice.py` from the project folder. You can replay a clip with `--video FILE`. Keep one hand in view for 1.5 seconds to add an entry, then lower your hands for at least 350 ms before the next pose. To speak the assembled sequence, press **S** or hold both palms open for 2 seconds. **C** clears the transcript and **Q** or **Esc** closes the camera. Start with `--speak-each` to hear each entry as soon as it is added.

The app recognizes seven static hand shapes from a fixed vocabulary. Each shape maps to the word or phrase below.

| Hand shape | Entry |
| --- | --- |
| Index and middle fingers raised in a V | Use |
| One open palm | Technology |
| Index finger pointing up | For |
| Thumbs up | Help |
| Thumbs down | Not |
| Closed fist | War |
| Thumb, index finger, and pinky extended | I love you |

MediaPipe finds each hand and estimates 21 landmark coordinates. Its gesture classifier assigns a category and score. The app looks for a reliable category over time, adds the configured word, and calls the operating system's speech engine. [MediaPipe Gesture Recognizer](https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer?tab=Python)

## `gesture_voice.py`

### Imports and vocabulary

- **1** Import `pairwise` to turn a chain of joint indexes into neighboring pairs.
- **3** Import OpenCV to draw the hand skeleton over the video.
- **4** Import MediaPipe as `mp` to load the pretrained gesture recognizer.
- **6** Import the shared camera loop, argument helpers, overlay drawing, model lookup, error handling, and OpenCV-to-MediaPipe conversion.
- **7** Import the shared speech player.
- **10** Define the window title.
- **11** Define the action used when two open palms request speech.
- **12** Open the dictionary that maps category names to phrases.
- **13** A victory or V pose adds **Use**.
- **14** One open palm adds **Technology**.
- **15** A pointing-up index finger adds **For**.
- **16** Thumbs up adds **Help**.
- **17** Thumbs down adds **Not**.
- **18** A closed fist adds **War**.
- **19** MediaPipe's I-love-you hand shape adds **I love you**.
- **20** Close the dictionary.
- **21** Start the landmark paths with the thumb, index finger, and middle finger. Each integer is MediaPipe's index for a joint or fingertip.
- **22** Complete the paths for the ring finger, pinky, and outside edge of the palm.

### Read the model output

- **25** Define a function that turns one model result into a hand count and a possible action.
- **26** Count hands by the number of landmark groups.
- **27** For each hand, use its top category when the classifier score is at least 0.60. Use `None` for missing or weak predictions.
- **28** Iterate over each hand's gesture prediction group to build the list of category names.
- **29** Check whether two visible hands both show open palms.
- **30** Return the speech action for the two-palm pose.
- **31** Check whether there is one hand and a candidate classification.
- **32** Look up the category in the vocabulary. `dict.get` returns `None` for an unlisted category.
- **33** Return the hand count without a candidate when neither case applies.

### Require a stable hold and release

- **36** Define the state object that remembers a gesture across multiple frames.
- **37** Initialize a fresh instance at the start of a session.
- **38** Start with no pending candidate.
- **39** Set the initial hold start time in milliseconds.
- **40** Start without a hand-release timestamp.
- **41** Start without a prior sample timestamp.
- **42** Let the first supported pose start a hold immediately.
- **44** Update the state with a hand count, a candidate, and the current source time in milliseconds.
- **45** Check for more than half a second between two samples.
- **46** Discard hold progress across that interruption.
- **47** Discard release progress too because the intermediate frames were unseen.
- **48** Remember this sample's timestamp for the next update.
- **50** Check whether any hands are visible.
- **51** Clear release progress when a hand is visible.
- **52** Handle a frame without a detected hand.
- **53** Check whether this is the first sample in the current release.
- **54** Record when the release began.
- **55** Wait until at least 350 ms have passed with no hands in view.
- **56** Unlock the next pose so the same word can be entered again deliberately.
- **58** Check whether a release is still required or there is no candidate to count.
- **59** Drop any previous candidate.
- **60** Return zero progress and no accepted action.
- **61** Check whether the candidate has just changed.
- **62** Store the new candidate.
- **63** Start timing that candidate from the current frame.
- **64** Require two seconds for the speech shortcut and one and a half seconds for individual words.
- **65** Divide elapsed time by the required duration and cap the fraction at 1.
- **66** Check whether the user has met the full duration.
- **67** Lock further actions until a deliberate release.
- **68** Return the completed progress and the accepted action exactly once.
- **69** Return the incomplete progress with no accepted action.

### Draw the native landmarks

- **72** Define a function that paints the landmarks on the preview in place.
- **73** Get the preview height and width from its first two array dimensions.
- **74** Draw each detected hand.
- **75** Convert normalized horizontal and vertical coordinates to pixel positions in the displayed frame.
- **76** Select each continuous path through the joints.
- **77** Walk through successive index pairs along that path.
- **78** Draw a gold antialiased line between those joints. OpenCV uses BGR channel order.
- **79** Visit every estimated joint and fingertip position.
- **80** Draw a small filled white marker at each point.

### Shared gesture session

- **83** Define the session both the desktop and browser adapters use for recognition.
- **84** Accept the initial preference for speaking every new entry.
- **85** Store that preference so it can be updated during a session.
- **86** Start the transcript as a private list for this webcam.
- **87** Create the timed hold-and-release logic for this session.
- **88** Start before the first valid model timestamp.
- **90** Define what happens when a runner enters the session context.
- **91** Shorten access to the MediaPipe vision API.
- **92** Begin specifying how the recognizer should be created.
- **93** Find the pinned model on disk and give its path to MediaPipe.
- **94** Use VIDEO mode so the model can follow a hand across a sequence.
- **95** Allow up to two hands so two palms can trigger speech.
- **96** Finish the recognizer options.
- **97** Open the model with those options.
- **98** Return the active session to the caller.
- **100** Define cleanup when a camera or browser connection closes.
- **101** Release the recognizer and its native resources.
- **103** Expose the clear action used by the C key and the browser button.
- **104** Remove all recognized words from this session.
- **106** Define the action that reads the entire current transcript.
- **107** Join entries with spaces so the speech engine receives a single string.
- **109** Accept the current image and its capture time in seconds.
- **110** Convert to integer milliseconds and enforce an increasing timestamp for MediaPipe.
- **111** Convert the frame to MediaPipe's format and detect poses and hand landmarks.
- **112** Count hands and map the recognizer prediction to a candidate word or action.
- **113** Advance the hold state to see whether this frame completes a selection.
- **114** Start with no new word or requested speech.
- **115** Detect the accepted two-palms action.
- **116** Request the transcript as speech only if there is text.
- **117** Handle a newly accepted vocabulary entry.
- **118** Save the word in this session's transcript.
- **119** Report the entry added on this particular frame for the Terminal log.
- **120** Check the setting that speaks each word immediately.
- **121** Request playback of the current word.
- **123** Use a general hint while waiting for a recognizable pose.
- **124** Check whether the state requires the hands to leave the frame before accepting another pose.
- **125** Instruct the user to release the pose.
- **126** If a candidate is being held, display progress toward acceptance.
- **127** Format the current word and hold progress percentage.
- **128** Strip each landmark down to the normalized x and y that either renderer can use.
- **129** Return the key points, a copy of the current words, and the displayed status.
- **130** Include the event for the latest added word or requested speech, if any.

### Run the desktop preview

- **133** Define the native Terminal entry point.
- **134** Create the parser with the shared camera and video options.
- **135** Add an opt-in flag for speaking words as they are accepted.
- **136** Parse the command and validate the selected camera or file.
- **137** Open the device, operating system speech player, and the shared gesture session together.
- **138** Read one original color frame at a time.
- **139** Run the same gesture processing the web route uses.
- **140** Check whether this frame added a word.
- **141** Print the accepted word promptly to the Terminal.
- **142** Check whether this frame requested speech.
- **143** Ask the operating system to speak the requested text.
- **144** Read the current transcript from the result.
- **145** Keep the preview compact by showing the last six entries.
- **146** Draw the hand landmarks returned by the processor over the frame.
- **147** Paint the status, transcript, and keys on the native preview.
- **148** Show the frame and collect a key press.
- **149** Check for the quit signal from the shared preview helper.
- **150** Leave the loop and close the camera, model, and speech process.
- **151** Allow S to read a transcript that contains words.
- **152** Speak the entire sequence on the Mac.
- **153** Recognize the C shortcut.
- **154** Clear this session's word entries.
- **157** Decide whether the module was invoked directly.
- **158** Start the app and return its status to the shell.

## `test_gesture_voice.py`

- **1** Import `SimpleNamespace` to build lightweight objects with named fields.
- **2** Import Python's built-in unit testing framework.
- **3** Import the mock helper to test the shared session without loading a video model.
- **5** Import the pose helpers, action name, and the session they belong to.
- **8** Define a fixture builder that accepts one category name per hand and a configurable score.
- **9** Start the synthetic result object.
- **10** Build one placeholder landmark group per hand. The result reader uses the count.
- **11** Build one top classification with the supplied label and score per hand.
- **12** Finish the result object.
- **15** Define the test case.
- **16** Test how gesture categories and classifier scores map to actions.
- **17** Check that a confident thumbs-up pose maps to **Help**.
- **18** Check that a low-score thumbs up yields no action.
- **19** Check that two open palms request speech.
- **20** Check that two different poses yield no action.
- **22** Test the timing of a single word and its release.
- **23** Create a new hold tracker.
- **24** Feed a sequence of samples at quarter-second intervals.
- **25** Assert that the tracker accepts nothing before the hold reaches 1.5 seconds.
- **26** Assert that the word is accepted at exactly 1.5 seconds.
- **27** Assert that holding the same pose longer generates no duplicate word.
- **28** Start a brief release.
- **29** Bring the hand back before the release completes.
- **30** Assert that the action is still locked.
- **31** Start a second release.
- **32** Provide another no-hand frame exactly 350 ms later.
- **33** Assert that the next action is now unlocked.
- **34** Confirm that putting the hand back starts a new hold with zero progress.
- **36** Test that a missing span of video cannot satisfy the hold.
- **37** Create another hold tracker.
- **38** Start timing the two-palm shortcut.
- **39** Verify a visible increase in progress after a second sample.
- **40** Simulate a long sample delay and verify that the candidate starts over.
- **41** Feed more samples at regular 300 ms intervals.
- **42** Verify no acceptance before the required two seconds have passed.
- **43** Verify that sustained samples complete the shortcut after exactly two seconds.

### Verify the result and release the model

- **45** Define a test for the result sent to the browser or desktop.
- **46** Create a high-confidence thumbs-up prediction.
- **47** Add a single sample landmark to the prediction.
- **48** Start replacing the relevant MediaPipe operations and opening a test session.
- **49** Pretend the model file exists so this test does not use disk assets.
- **50** Skip the conversion of actual input pixels.
- **51** Replace recognizer creation and retain the mock so the test can inspect it.
- **52** Start the gesture session with automatic speech enabled.
- **53** Enter all the test contexts.
- **54** Return the same known pose from each model call.
- **55** Submit six samples up to 1.25 seconds.
- **56** Confirm the transcript stays empty while the hold runs.
- **57** Submit the frame that completes a 1.5-second hold.
- **58** Verify the returned landmark is a pair of normalized coordinates.
- **59** Check that the same frame adds the word Help and requests it for speech.
- **60** Check that continuing to hold the pose produces no repeated speech.
- **61** Confirm the current transcript can be read out.
- **62** Clear the transcript through the session method.
- **63** Verify that no words remain.
- **64** Confirm that the recognizer is released exactly once.
