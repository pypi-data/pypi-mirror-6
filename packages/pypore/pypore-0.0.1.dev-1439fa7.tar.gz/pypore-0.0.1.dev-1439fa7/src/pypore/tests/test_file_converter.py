"""

"""

import unittest
import os
from pypore.io import get_reader_from_filename
from pypore.file_converter import convert_file

import numpy as np
from pypore.io.data_file_reader import DataFileReader


class TestFileConverter(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_convert_file_set_output_filename(self):
        """
        Tests that the output filename can be set correctly.
        """
        filename = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(filename, 'testDataFiles', 'chimera_1event.log')

        output_filename_set = "test_convert_file_set_output_filename.h5"

        output_filename = convert_file(filename, output_filename=output_filename_set)

        # Test that we can set the output filename
        self.assertEqual(output_filename, output_filename_set, "output_filename not correct")

        os.remove(output_filename)

    def test_convert_chimera_file_equality(self):
        """
        Test that the original/converted matrices and sample rates are the same for one-channel data.
        """
        filename = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(filename, 'testDataFiles', 'chimera_1event.log')

        output_filename_set = "test_convert_chimera_file_equality.h5"

        output_filename = convert_file(filename, output_filename=output_filename_set)

        orig_reader = get_reader_from_filename(filename)
        orig_data_all = orig_reader.get_all_data()
        orig_sample_rate = orig_reader.get_sample_rate()

        self.assertEqual(len(orig_data_all), 1)

        out_reader = DataFileReader(output_filename)
        out_data_all = out_reader.get_all_data()
        out_sample_rate = out_reader.get_sample_rate()

        self.assertEqual(len(out_data_all), 1)

        orig_data = orig_data_all[0]
        out_data = out_data_all[0]

        # assert sample rates are equal
        self.assertAlmostEqual(1.0 * orig_sample_rate / out_sample_rate, 1, 4)

        # assert the two arrays are equal
        np.testing.assert_array_equal(orig_data, out_data)

        orig_reader.close()
        out_reader.close()

        os.remove(output_filename)


from pypore.file_converter import filter_file


class TestFilterFile(unittest.TestCase):
    def setUp(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))

    def test_default_output_name(self):
        """
        Tests that the default output filename of :func:`filter_file <pypore.file_converter.filter_file>` is correct.
        """
        filename = os.path.join(self.directory, 'testDataFiles', 'chimera_1event.log')

        output_filename_should_be = os.path.join(self.directory, 'testDataFiles', 'chimera_1event_filtered.h5')

        if os.path.exists(output_filename_should_be):
            os.remove(output_filename_should_be)

        out_filename = filter_file(filename, 10.e4, 100.e4)

        self.assertEqual(out_filename, output_filename_should_be,
                         msg="Default filename incorrect. Was {0}, should be {1}.".format(out_filename,
                                                                                          output_filename_should_be))

        # Make sure the file actually exists. Try opening it.
        f = open(out_filename)
        f.close()

        os.remove(out_filename)

    def test_set_output_name(self):
        """
        Tests that setting the output filename of :func:`filter_file <pypore.file_converter.filter_file>` is correct.
        """
        filename = os.path.join(self.directory, 'testDataFiles', 'chimera_1event.log')

        set_out_filename = os.path.join(self.directory, 'testDataFiles', 'test_set_output_name.h5')

        #remove if exists
        if os.path.exists(set_out_filename):
            os.remove(set_out_filename)

        out_filename = filter_file(filename, 10.e4, 100.e4, output_filename=set_out_filename)

        self.assertEqual(set_out_filename, out_filename,
                         "Output filename not set correctly. Was {0}, should be {1}".format(set_out_filename,
                                                                                            out_filename))

        # Make sure the file actually exists. Try opening it.
        f = open(out_filename)
        f.close()

        os.remove(out_filename)

    def _test_out_sample_rate_data_len_equality(self, orig_data, orig_sample_rate, out_filename, sample_rate):
        out_reader = get_reader_from_filename(out_filename)
        out_sample_rate = out_reader.get_sample_rate()
        out_data = out_reader.get_all_data()
        out_reader.close()
        self.assertAlmostEqual(orig_sample_rate, out_sample_rate, 2,
                               msg="Sampling rate changed during filter_file, "
                                   "when it should not. Was {0}, wanted {1}, got {2}".format(
                                   orig_sample_rate, sample_rate, out_sample_rate))
        self.assertEqual(len(orig_data), len(orig_data),
                         msg="Filtering changed the number of channels. Was {0}, output {1}".format(len(orig_data),
                                                                                                    len(out_data)))
        self.assertEqual(orig_data[0].size, out_data[0].size,
                         msg="Output data size doesn't match the original. Was {0}, output {1}.".format(
                             orig_data[0].size, out_data[0].size))
        return out_data

    def test_same_sample_rate_no_change(self):
        """
        Tests that if we set the output sample rate to < 0, the sampling doesn't change, but the file is filtered.
        """
        filename = os.path.join(self.directory, 'testDataFiles', 'chimera_1event.log')

        set_out_filename = os.path.join(self.directory, 'testDataFiles', 'test_same_sample_rate_no_change.h5')

        if os.path.exists(set_out_filename):
            os.remove(set_out_filename)

        # Open a reader and read the original sample rate
        orig_reader = get_reader_from_filename(filename)
        orig_sample_rate = orig_reader.get_sample_rate()
        orig_data = orig_reader.get_all_data()
        orig_reader.close()

        for sample_rate in (-1, 0., orig_sample_rate, orig_sample_rate + 100.):
            # filter the file, with negative sample rate
            out_filename = filter_file(filename, 10.e4, sample_rate, output_filename=set_out_filename)

            self._test_out_sample_rate_data_len_equality(orig_data, orig_sample_rate, out_filename, sample_rate)

            os.remove(out_filename)

    def test_set_output_sample_rate(self):
        """
        Tests that we can successfully set the output sample rate, and the number of data points changes correctly.
        """
        file_names = [os.path.join(self.directory, 'testDataFiles', 'chimera_1event.log'),
                      os.path.join(self.directory, 'testDataFiles', 'chimera_1event_2levels.log')]

        set_out_filename = os.path.join(self.directory, 'testDataFiles', 'test_set_output_sample_rate.h5')

        if os.path.exists(set_out_filename):
            os.remove(set_out_filename)

        for filename in file_names:
            # Open a reader and read the original sample rate
            orig_reader = get_reader_from_filename(filename)
            orig_sample_rate = orig_reader.get_sample_rate()
            orig_data = orig_reader.get_all_data()
            n_orig = orig_data[0].size
            orig_reader.close()

            for out_sample_rate in (100.e4, 1.e6, 5.e5):
                out_filename = filter_file(filename, 10.e4, out_sample_rate, output_filename=set_out_filename)

                # The output number of data points should be int(np.ceil(n_orig * out_sample_rate / orig_sample_rate))
                n_out = int(np.ceil(n_orig * out_sample_rate / orig_sample_rate))
                # The output sample rate should be set by n_out
                out_sample_rate = orig_sample_rate * (1.0 * n_out) / n_orig

                # Get the params from the output file
                out_reader = get_reader_from_filename(out_filename)
                o_s_r = out_reader.get_sample_rate()
                out_data = out_reader.get_all_data()
                n_o = out_data[0].size
                out_reader.close()

                self.assertEqual(n_out, n_o,
                                 "Number of re-sample points not correct. "
                                 "Original data {0}, output {1}, should be {2}.".format(n_orig, n_o, n_out))
                self.assertAlmostEqual(o_s_r, out_sample_rate, 2,
                                       "Sample rate not set correctly. Was {0}, should be {1}".format(o_s_r,
                                                                                                      out_sample_rate))

                os.remove(out_filename)


if __name__ == "__main__":
    unittest.main()

