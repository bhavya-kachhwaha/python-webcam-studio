import unittest

import numpy as np

from scene_caption import END_OF_TEXT, PAST_NAMES, generate_tokens, image_tensor


class CaptionTests(unittest.TestCase):
    def test_image_tensor_is_rgb_normalized_and_channels_first(self):
        blue_bgr = np.full((10, 20, 3), (255, 0, 0), dtype=np.uint8)
        tensor = image_tensor(blue_bgr)
        self.assertEqual(tensor.shape, (1, 3, 224, 224))
        self.assertEqual(tensor.dtype, np.float32)
        np.testing.assert_array_equal(tensor[0, :, 0, 0], [-1.0, -1.0, 1.0])

    def test_decoder_reuses_its_cache_until_the_end_token(self):
        calls = []

        class Decoder:
            def run(self, _, inputs):
                token = inputs["input_ids"].item()
                uses_cache = inputs["use_cache_branch"].item()
                cache_length = inputs[PAST_NAMES[0]].shape[2]
                calls.append((token, uses_cache, cache_length))
                winner = (42, 8, END_OF_TEXT)[len(calls) - 1]
                logits = np.zeros((1, 1, END_OF_TEXT + 1), dtype=np.float32)
                logits[0, 0, winner] = 1.0
                cache = np.empty((1, 12, len(calls), 64), dtype=np.float32)
                return [logits, *([cache] * len(PAST_NAMES))]

        self.assertEqual(generate_tokens(Decoder(), np.zeros((1, 197, 768))), [42, 8])
        self.assertEqual(calls, [(END_OF_TEXT, False, 0), (42, True, 1), (8, True, 2)])
