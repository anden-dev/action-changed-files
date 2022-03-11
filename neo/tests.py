#!/usr/bin/env python3

import unittest
import neo


class TestChangedFiles(unittest.TestCase):
    def test_no_changes(self):
        self.assertFalse(
            neo.generate_matrix(
                include_regex="clusters/.*",
                payload={
                    "files": [
                        {"filename": "clusters", "status": "modified"},
                        {"filename": "blah", "status": "modified"},
                    ]
                },
            )
        )

    def test_changes_groups_level1(self):
        self.assertCountEqual(
            neo.generate_matrix(
                include_regex="clusters/(?P<environment>\w+)/.*",
                payload={
                    "files": [
                        {"filename": "clusters/staging/app", "status": "modified"},
                        {"filename": "clusters/staging/demo", "status": "modified"},
                        {"filename": "clusters/live/app", "status": "modified"},
                    ]
                },
            ),
            [
                {"environment": "staging", "reason": "modified"},
                {"environment": "live", "reason": "modified"},
            ],
        )

    def test_changes_groups_level2(self):
        self.assertCountEqual(
            neo.generate_matrix(
                include_regex="clusters/(?P<environment>\w+)/(?P<namespace>\w+)",
                payload={
                    "files": [
                        {"filename": "clusters/staging/app", "status": "modified"},
                        {"filename": "clusters/live/app", "status": "modified"},
                        {"filename": "clusters/staging/demo", "status": "modified"},
                    ]
                },
            ),
            [
                {"environment": "staging", "namespace": "app", "reason": "modified"},
                {"environment": "staging", "namespace": "demo", "reason": "modified"},
                {"environment": "live", "namespace": "app", "reason": "modified"},
            ],
        )

    def test_changes_no_group(self):
        self.assertCountEqual(
            neo.generate_matrix(
                include_regex="clusters/.*",
                payload={
                    "files": [
                        {"filename": "clusters/staging/app", "status": "modified"},
                        {"filename": "clusters/live/app", "status": "modified"},
                        {"filename": "clusters/staging/demo", "status": "modified"},
                        {"filename": "my_other_file/hello", "status": "modified"},
                    ]
                },
            ),
            [
                {"path": "clusters/staging/app", "reason": "modified"},
                {"path": "clusters/staging/demo", "reason": "modified"},
                {"path": "clusters/live/app", "reason": "modified"},
            ],
        )

    def test_changes_sorted(self):
        self.assertListEqual(
            neo.generate_matrix(
                include_regex="clusters/.*",
                payload={
                    "files": [
                        {"filename": "my_other_file/hello", "status": "modified"},
                        {"filename": "clusters/live/app", "status": "modified"},
                        {"filename": "clusters/staging/app", "status": "modified"},
                        {"filename": "clusters/staging/demo", "status": "modified"},
                    ]
                },
            ),
            [
                {"path": "clusters/live/app", "reason": "modified"},
                {"path": "clusters/staging/app", "reason": "modified"},
                {"path": "clusters/staging/demo", "reason": "modified"},
            ],
        )

    def test_all_matches_removed(self):
        self.assertCountEqual(
            neo.generate_matrix(
                include_regex="clusters/(?P<environment>\w+)/.*",
                payload={
                    "files": [
                        {"filename": "clusters/staging/app", "status": "removed"},
                        {"filename": "clusters/staging/demo", "status": "removed"},
                        {"filename": "clusters/live/app", "status": "modified"},
                    ]
                },
            ),
            [
                {"environment": "staging", "reason": "removed"},
                {"environment": "live", "reason": "modified"},
            ],
        )

    def test_one_match_removed(self):
        self.assertCountEqual(
            neo.generate_matrix(
                include_regex="clusters/(?P<environment>\w+)/.*",
                payload={
                    "files": [
                        {"filename": "clusters/staging/app", "status": "removed"},
                        {"filename": "clusters/staging/demo", "status": "modified"},
                        {"filename": "clusters/live/app", "status": "modified"},
                    ]
                },
            ),
            [
                {"environment": "staging", "reason": "?"},
                {"environment": "live", "reason": "modified"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
