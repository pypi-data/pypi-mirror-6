import unittest
import os

from ipuin import Ipuin


class TestIpuin(unittest.TestCase):

    def setUp(self):
        samplefile = os.path.join(os.path.dirname(__file__), 'sample.ipuin')
        self.ipuin = Ipuin(ipuinfile=samplefile)

    def test_ipuin_metadata(self):
        self.assertEqual(self.ipuin.title, 'Sample title')
        self.assertEqual('.png', self.ipuin.cover[-4:])
        self.assertIn('Sample description', self.ipuin.info)
        self.assertIn('Sample author', self.ipuin.info)
        self.assertEqual('step1', self.ipuin.start)

    def test_steps(self):
        self.assertEqual('Step 1', self.ipuin.get_step_title('step1'))
        step = self.ipuin.steps['step1']
        self.assertIn('Text for step1', self.ipuin.get_step_text(step))
        self.assertTrue(self.ipuin.step_has_image(step))
        targets = self.ipuin.get_step_targets('step1')
        self.assertEqual(2, len(targets))
        self.assertFalse(self.ipuin.is_end_step('step1'))

        self.assertEqual('Step 2', self.ipuin.get_step_title('step2'))
        step = self.ipuin.steps['step2']
        self.assertIn('Text for step2', self.ipuin.get_step_text(step))
        self.assertFalse(self.ipuin.step_has_image(step))
        targets = self.ipuin.get_step_targets('step2')
        self.assertEqual(1, len(targets))

        self.assertTrue(self.ipuin.is_end_step('step5'))

    def test_get_step_image(self):
        "Getting the image of a step always returns the same temporary file"
        step = self.ipuin.steps['step1']
        img1 = self.ipuin.get_step_image(step)
        img2 = self.ipuin.get_step_image(step)
        self.assertEqual(img1, img2)

    def test_set_cover(self):
        cover = self.ipuin.cover
        raw_cover = self.ipuin.data['cover']
        self.ipuin.cover = cover
        self.assertEqual(self.ipuin.data['cover'], raw_cover)


class TestIpuinCreation(unittest.TestCase):
    def setUp(self):
        self.newfile = os.path.join(os.path.dirname(__file__), 'newipuin.ipuin')
        self.ipuin = Ipuin(self.newfile)

    def test_new_ipuin(self):
        self.assertEqual(self.ipuin.data, Ipuin.IPUIN_DATA_TEMPLATE)

    def test_save_ipuin(self):
        self.assertFalse(os.path.exists(self.newfile))
        self.ipuin.title = 'sample new title'
        self.ipuin.save()
        self.assertTrue(os.path.exists(self.newfile))

        self.ipuin.close()
        self.ipuin = Ipuin(self.newfile)
        self.assertEqual(self.ipuin.title, 'sample new title')

    def tearDown(self):
        if os.path.exists(self.newfile):
            os.remove(self.newfile)

if __name__ == '__main__':
        unittest.main()
