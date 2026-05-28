import unittest

import main


DRILL = {
    "id": "sample",
    "_pack": "python_basic",
    "times_required": 3,
}


class WeakRecoveryTests(unittest.TestCase):
    def test_recall_wrong_marks_weak_and_resets_streak(self):
        progress = {
            "python_basic:sample": {
                "recall_wrong_attempts": 1,
                "weak_correct_streak": 2,
            }
        }

        main.record_recall_wrong(progress, DRILL, "bad answer")

        record = main.get_progress_record(progress, "sample", "python_basic")
        self.assertEqual(record["recall_wrong_attempts"], 2)
        self.assertEqual(record["weak_correct_streak"], 0)
        self.assertEqual(record["wrong_attempts"], 1)

    def test_three_weak_correct_attempts_clear_weak_status(self):
        progress = {
            "python_basic:sample": {
                "recall_wrong_attempts": 1,
                "weak_correct_streak": 0,
            }
        }

        main.record_weak_correct(progress, DRILL)
        main.record_weak_correct(progress, DRILL)
        record = main.get_progress_record(progress, "sample", "python_basic")
        self.assertEqual(record["recall_wrong_attempts"], 1)
        self.assertEqual(record["weak_correct_streak"], 2)

        main.record_weak_correct(progress, DRILL)
        self.assertEqual(record["recall_wrong_attempts"], 0)
        self.assertEqual(record["weak_correct_streak"], 0)

    def test_weak_wrong_resets_streak(self):
        progress = {
            "python_basic:sample": {
                "recall_wrong_attempts": 1,
                "weak_correct_streak": 2,
            }
        }

        main.record_weak_wrong(progress, DRILL, "still wrong")

        record = main.get_progress_record(progress, "sample", "python_basic")
        self.assertEqual(record["recall_wrong_attempts"], 1)
        self.assertEqual(record["weak_correct_streak"], 0)
        self.assertEqual(record["wrong_attempts"], 1)

    def test_old_weak_correct_attempts_field_is_migrated(self):
        progress = {
            "python_basic:sample": {
                "weak_correct_attempts": 2,
            }
        }

        record = main.get_progress_record(progress, "sample", "python_basic")

        self.assertEqual(record["weak_correct_streak"], 2)


if __name__ == "__main__":
    unittest.main()
