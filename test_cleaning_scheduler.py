import unittest

import cleaning_scheduler as c


class Data(unittest.TestCase):
    def test_smg_1300_count(self):
        comps = c.components("SMG-1300L")
        self.assertEqual(len(comps), 11)
        self.assertEqual(comps[0]["name"], "Discharge port assembly")
        self.assertEqual(comps[0]["scrub"], 20)

    def test_smg_1000_count(self):
        self.assertEqual(len(c.components("SMG-1000L")), 11)

    def test_smg_150_count(self):
        self.assertEqual(len(c.components("SMG-150L")), 10)

    def test_fbe_1300_count(self):
        self.assertEqual(len(c.components("FBE-1300L")), 9)

    def test_fbe_800_count(self):
        self.assertEqual(len(c.components("FBE-800L")), 8)

    def test_fbe_125_single(self):
        self.assertEqual(len(c.components("FBE-125L (MFBE-05)")), 1)

    def test_gerteis_count(self):
        self.assertEqual(len(c.components("Macro-Pactor")), 23)

    def test_sieve_mill_count(self):
        self.assertEqual(len(c.components("Conical Sieve Mill")), 6)

    def test_quadro_scrub_only(self):
        comps = c.components("Quadro U 20")
        self.assertEqual(len(comps), 4)
        self.assertEqual(comps[0]["scrub"], 20)
        self.assertEqual(comps[0]["p1"], 0)

    def test_unknown_model(self):
        with self.assertRaises(KeyError):
            c.components("Nope")


class Scheduling(unittest.TestCase):
    def setUp(self):
        self.tasks = [{"name": "A", "scrub": 20}, {"name": "B", "scrub": 40},
                      {"name": "C", "scrub": 15}]

    def test_one_person_sequential(self):
        r = c.schedule(self.tasks, people=1, start_min=360)
        self.assertEqual(r["makespan"], 75)
        self.assertEqual(r["total_min"], 75)
        self.assertEqual(r["finish"], "07:15")
        self.assertEqual([a["start"] for a in r["assignments"]], ["06:00", "06:20", "07:00"])
        self.assertEqual([a["end"] for a in r["assignments"]], ["06:20", "07:00", "07:15"])

    def test_two_people_shortens_finish(self):
        r = c.schedule(self.tasks, people=2, start_min=360)
        self.assertEqual(r["makespan"], 40)
        self.assertEqual(r["finish"], "06:40")

    def test_longest_task_first(self):
        r = c.schedule(self.tasks, people=2, start_min=360)
        by_name = {a["name"]: a for a in r["assignments"]}
        self.assertEqual(by_name["B"]["person"], 1)

    def test_more_people_never_longer(self):
        one = c.schedule(self.tasks, people=1)["makespan"]
        two = c.schedule(self.tasks, people=2)["makespan"]
        three = c.schedule(self.tasks, people=3)["makespan"]
        self.assertLessEqual(two, one)
        self.assertLessEqual(three, two)
        self.assertEqual(three, 40)

    def test_people_capped_at_task_count(self):
        r = c.schedule(self.tasks, people=9)
        self.assertEqual(r["people"], 3)

    def test_validated_durations_unchanged(self):
        r = c.schedule(self.tasks, people=3)
        durations = sorted(a["duration"] for a in r["assignments"])
        self.assertEqual(durations, [15, 20, 40])

    def test_empty(self):
        r = c.schedule([])
        self.assertEqual(r["makespan"], 0)
        self.assertEqual(r["people"], 0)

    def test_midnight_roll(self):
        r = c.schedule([{"name": "A", "scrub": 120}], people=1, start_min=1380)
        self.assertEqual(r["finish"], "01:00")


class Water(unittest.TestCase):
    def test_totals(self):
        comps = c.components("SMG-150L")
        w = c.water_totals(comps)
        self.assertEqual(w["potable1_kg"], 230.0)
        self.assertEqual(w["teepol_ml"], 13100.0)
        self.assertEqual(w["purified_kg"], 230.0)

    def test_hhmm(self):
        self.assertEqual(c.to_hhmm(0), "00:00")
        self.assertEqual(c.to_hhmm(1439), "23:59")
        self.assertEqual(c.to_hhmm(1440), "00:00")


class Remark(unittest.TestCase):
    def test_cleaning_remark(self):
        comps = c.components("SMG-150L")
        r1 = c.schedule(comps, people=1, start_min=360)
        r2 = c.schedule(comps, people=2, start_min=360)
        w = c.water_totals(comps)
        text = c.cleaning_remark("Saizoner Mixer Granulator (SMG)", "SMG-150L", "OI-04",
                                 "11.09.2026", "8841", "06:00", r2, w,
                                 one_person_makespan=r1["makespan"])
        for t in ["PRODUCT CHANGE CLEANING RECORD", "SMG-150L", "SOP: OI-04",
                  "crew of 2 persons", "Total validated scrubbing time",
                  "saved", "Teepol", "Quality Assurance"]:
            self.assertIn(t, text)


if __name__ == "__main__":
    unittest.main()