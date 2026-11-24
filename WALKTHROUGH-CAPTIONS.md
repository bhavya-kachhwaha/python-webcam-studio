# Scene Caption Camera, line by line

OpenCV provides a color frame. A Vision Transformer converts the picture into numerical features. GPT-2 reads those features and generates the caption one token at a time. The tokenizer combines the tokens into words. The app draws the caption over the live view and can pass the same text to the operating system’s speech engine. [Quantized model and configuration](https://huggingface.co/Xenova/vit-gpt2-image-captioning/tree/077550ae0729f9af280c9d885ea9b0380fc8e815)

Follow [scene_caption.py](scene_caption.py) alongside these notes. Gaps in the numbering are blank lines.

## Imports and model names

- **1** `ThreadPoolExecutor` lets a background thread run the model while the main thread keeps showing video.
- **2** `sys` gives us `sys.stderr` for writing details about failures to the terminal.
- **3** `wrap` splits a long caption into lines before OpenCV paints it on the frame.
- **5** `cv2` is OpenCV. Here it resizes images and changes their color order.
- **6** `numpy`, imported as `np`, holds images and model inputs as numerical arrays.
- **8** The shared camera module provides capture and display, command-line parsing, overlay rendering, model paths, and application error handling.
- **9** `Speech` runs the platform’s local text-to-speech command.
- **12** `TITLE` supplies the window title and the visible heading.
- **13** The pinned GPT-2 model uses token ID `50256` as both the first decoder input and the end-of-caption marker.
- **14** `tuple(` starts an ordered, immutable list of the decoder’s cache input names.
- **15** The f-string inserts the attention layer number and the name of the key or value tensor.
- **16** The model has 12 decoder attention layers, numbered 0 through 11.
- **17** Each layer has two cache tensors, a key array and a value array.
- **18** This parenthesis finishes the tuple construction.
- **19** The decoder returns vocabulary scores called logits and updated attention state. The returned tensor names replace `past_key_values.` with `present.`. The star adds these names to the output list after `logits`.

## Prepare the image

- **22** `image_tensor` transforms an OpenCV frame into the single-image array the model expects.
- **23** `resize` gives the image the model’s required size of 224 × 224 pixels. Bilinear interpolation computes each new pixel from nearby source pixels.
- **24** OpenCV supplies blue, green, red channels. The model expects red, green, blue. `astype` converts channel values to 32-bit floating point for the model.
- **25** Dividing by 127.5 and subtracting 1 maps channel values from 0–255 to −1–1, as required by the model configuration.
- **26** `transpose` moves channels to the front. `[None]` adds a batch dimension, making the shape `[1, 3, 224, 224]`. `ascontiguousarray` arranges the values consecutively in memory for inference.

## Generate tokens one at a time

- **29** `generate_tokens` takes the decoder session and the image features already produced by the encoder.
- **30** The initial cache has one image, 12 attention heads, zero past tokens, and 64 values per head. The zero-length axis makes this a valid empty input.
- **31** The dictionary gives each cache input the same empty tensor to begin with. Later steps replace the entries with the actual state from each layer.
- **32** Image features are available at every decoding step through `encoder_hidden_states`.
- **33** The first step disables the cache branch. The decoder establishes its attention state from the initial token.
- **34** Set the initial token to the model’s start marker.
- **35** Start a list of generated token IDs.
- **36** Limit generation to 30 tokens. `_` indicates that the counter itself is unused.
- **37** Put the most recent token into a 64-bit integer array with shape `[1, 1]`, meaning one image and one input token.
- **38** Run the decoder. The first result is the logits, and starred unpacking collects the updated cache tensors.
- **39** Select the highest-scoring vocabulary token for the latest position in this batch. Choosing the winner at every step is known as greedy decoding.
- **40** Check whether the winner is the model’s stop marker.
- **41** Leave the loop as soon as the model emits that marker.
- **42** Save a regular token so the tokenizer can turn it into text later.
- **43** Pair each cache input name with the corresponding updated tensor. The next decoder call can reuse attention state computed on previous steps.
- **44** Enable the cache branch for subsequent steps.
- **45** Return the generated IDs from the list.

## Load the models and decode text

- **48** `load_model` builds the two inference sessions and the text tokenizer on first use.
- **49** Import ONNX Runtime when the model is needed. The rest of the app can start before it imports the inference engine.
- **50** Import the lightweight tokenizer that reads the published GPT-2 vocabulary and token rules.
- **51** Disable ONNX Runtime’s telemetry before opening either inference session.
- **52** Locate the quantized Vision Transformer encoder in the local model directory.
- **53** Locate the merged quantized GPT-2 decoder, which has branches for initial and cached decoding.
- **54** Locate the tokenizer JSON beside the model weights.
- **55** Create shared ONNX Runtime session options.
- **56** Allow four threads for each model operation so inference can parallelize without taking all the system’s cores by default.
- **57** Choose the local CPU provider for both sessions.
- **58** Read the image encoder from disk into a session.
- **59** Read the text decoder into a separate session with the same options.
- **60** Read the GPT-2 vocabulary and rules from the local tokenizer file.
- **61** Return all three loaded pieces so the same captioner can use them again.
- **64** The `Captioner` class stores shared model state and exposes a method for describing an image.
- **65** The constructor runs when the app creates a captioner.
- **66** `None` marks the model bundle as unloaded.
- **68** The `describe` method takes the color frame chosen for captioning.
- **69** Check whether this is the first successful model load.
- **70** Load and store the sessions and tokenizer when needed. Later frames use the same instances.
- **71** Give each of the three model components a local name.
- **72** Prepare the camera image as the encoder’s input tensor.
- **73** Run the encoder with that tensor as `pixel_values`. The trailing comma unpacks its single requested output, the image’s learned feature array.
- **74** Generate a sequence of text-token IDs using those image features.
- **75** Decode the IDs to text, skip tokenizer control symbols, and remove leading or trailing whitespace.
- **76** Check whether the resulting caption is blank.
- **77** Report empty output as an error so the app can explain the failure and let the user retry.
- **78** Return the finished caption.

## Keep the camera responsive

- **81** `main` runs the interactive camera app.
- **82** Build the parser with the shared camera and local-video options.
- **83** Add `--auto` to start with periodic captioning enabled.
- **84** Parse the command-line arguments and validate the video path or camera index.
- **85** Create a captioner with lazy model loading.
- **86** Copy the auto-caption setting into a variable the keyboard can toggle later.
- **87** Set the initial automatic caption to be eligible immediately.
- **88** `None` means there is no inference request in flight.
- **89** Start with an empty caption because the user has yet to describe a frame.
- **90** Set the initial prompt shown above the live view.
- **92** Open one worker thread, the camera, and the local speech engine. Context managers clean them up when the user quits or playback ends.
- **93** Read one color frame per loop iteration from the selected source.
- **94** Poll a pending request without blocking the camera loop. Enter this branch only after it completes.
- **95** Start a block that handles inference errors.
- **96** Extract the worker’s result and replace the currently displayed caption.
- **97** Also print the caption in the terminal. Flushing makes the result immediately available there.
- **98** Show that the caption is ready.
- **99** Catch a model or processing error raised by the worker so the camera can stay open.
- **100** Send the detailed error to the terminal.
- **101** Give the preview a shorter status message with a way to retry.
- **102** Switch off automatic retry after a failure. The user can request a new caption with **C**.
- **103** Clear the finished request so another can be started.
- **104** Schedule the next automatic attempt four seconds later, measured on the source timeline.
- **106** Check whether automatic captions are on, the worker is free, and the scheduled time has arrived.
- **107** Submit a copy of the unannotated frame to the worker. It can keep reading that image while the camera advances.
- **109** Use a separate frame copy for the preview so the drawn text stays out of the model’s input.
- **110** Choose the label for the current automatic-caption setting.
- **111** Show progress while inference is running. Otherwise show the last status.
- **112** Put the available keyboard controls together with the auto setting.
- **113** Draw the title, controls, status, and wrapped caption at the top of the live view.
- **114** Display the frame and read the next OpenCV keyboard event.
- **115** The shared camera returns `None` after **Q**, **Esc**, or closing the window.
- **116** Leave the loop and clean up the camera, speech, and worker.
- **117** Check for the **C** key with no active request.
- **118** Send the current frame to the worker for manual captioning.
- **119** Check for the **A** key.
- **120** Toggle automatic captioning between on and off.
- **121** Reset the schedule so newly enabled automatic captioning can start on the next frame.
- **122** Check for the **S** key and ensure there is a caption to speak.
- **123** Begin error handling around the speech operation.
- **124** Pass the latest caption to the operating system’s speech command.
- **125** Catch a speech engine or process-start failure so viewing and captioning remain available.
- **126** Print the detailed speech failure to the terminal.
- **127** Show a short speech error in the preview.
- **130** The module name equals `"__main__"` when this file is executed directly. Importing it from the tests skips the interactive launch.
- **131** Start the app with shared error handling and return its exit code to the shell.

## Test lines

The [caption tests](test_scene_caption.py) use generated arrays and a tiny fake decoder. They can run without loading the model weights or opening the webcam.

- **1** `unittest` provides Python’s test discovery and assertions.
- **3** NumPy is used to generate predictable input arrays and compare model input values.
- **5** Import the caption constants and the two processing functions under test.
- **8** `CaptionTests` inherits standard assertions and test runner behavior.
- **9** This test checks color conversion, normalization, and the image tensor’s shape.
- **10** Create a 10 × 20 image with blue at full strength in OpenCV’s BGR order.
- **11** Apply the real model preprocessing.
- **12** Expect one image, three channels, and the required 224 × 224 image size.
- **13** Make sure values use 32-bit floats.
- **14** After conversion to RGB and normalization, a blue pixel has the values −1, −1, and 1.
- **16** This test checks that tokens feed back into generation and that the stop marker ends the loop.
- **17** Record what the fake decoder receives on each call.
- **19** Define a minimal replacement for the model session in this test.
- **20** Match the real session’s `run` method. The fake uses the input values and ignores the requested output names.
- **21** Read the sole input token from its NumPy array.
- **22** Read the flag that selects the cache branch.
- **23** Read the number of cached token positions from the first cache input.
- **24** Keep the input token, flag, and cache length for later comparison.
- **25** Arrange for the decoder to emit token 42, then token 8, then the stop marker.
- **26** Create a row of scores with an entry for every possible token in this test vocabulary.
- **27** Give the chosen token the highest score.
- **28** Return a simulated cache that grows by one position for each decoded token.
- **29** Return the score array followed by one cache array per requested input.
- **31** Run the real token loop with dummy image features and verify it returns exactly the two regular tokens.
- **32** Verify the start marker, blank cache, cached branch, and subsequent feedback tokens across all three calls.

Try describing the same scene in front of a bright light and with light behind the camera. Press **C** each time and compare the captions. A caption describes what the model inferred from the pixels and can miss details or guess incorrectly.
