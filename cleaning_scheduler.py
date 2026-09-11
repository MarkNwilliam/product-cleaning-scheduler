"""Product cleaning scheduler for granulation changeovers.

Component scrubbing times, Teepol and water quantities are taken from the
facility cleaning parameters guide. Validated scrubbing times are never
shortened. Adding people only parallelises the work, so the finish time falls
while every task keeps its strict validated duration.

Pure python, no dependencies. Mirror of the dashboard at
https://marknwilliam.github.io/product-cleaning-scheduler/
"""

# name, qty, potable 1st wash kg, 0.1 percent Teepol ml, scrubbing min,
# potable 2nd wash kg, purified final rinse kg
EQUIPMENT = {
    "Saizoner Mixer Granulator (SMG)": {
        "sop": "OI-04",
        "models": {
            "SMG-1300L": [
                ("Discharge port assembly", 1, 45, 280, 20, 30, 30),
                ("Platform, guards, staircase, machine base, CIP system, Impeller, vacuum transfer pipes, SS wire conduits", 1, 89, 180, 40, 68, 56),
                ("Chopper assembly", 1, 15, 180, 15, 12, 12),
                ("Agitator", 1, 35, 500, 20, 25, 20),
                ("Cone and wing bolt", 1, 16, 210, 20, 10, 10),
                ("Gaskets (lid inflatable, view window, charging valves)", 1, 15, 140, 13.5, 9, 9),
                ("Main body, Bowl, vacuum transfer pipes, CIP nozzles, chopper motor housing", 1, 100, 1950, 70, 100, 100),
                ("Co-mill assembly (wing nut, blade, cone hub, screen, motor housing, discharge hopper)", 1, 15, 350, 32, 15, 15),
                ("Lid (charging valves, vent filter, view window glass assembly)", 1, 100, 6000, 35, 100, 50),
                ("Spray gun assembly (binder transfer pipe, peristaltic pump)", 1, 30, 800, 35, 20, 20),
                ("Clamps, bolts, nuts", 1, 10, 1500, 8, 10, 10),
            ],
            "SMG-1000L": [
                ("Discharge port assembly", 1, 40, 2500, 15, 30, 25),
                ("Agitator", 1, 45, 1200, 40, 30, 15),
                ("Platform, guards, staircase, machine base, CIP system, Impeller, vacuum transfer pipes, SS wire conduits", 1, 75, 1800, 40, 75, 40),
                ("Chopper", 1, 15, 1600, 15, 12, 8),
                ("Cone and wing bolt", 1, 15, 2000, 20, 12, 10),
                ("Gaskets (lid gasket, view window gasket, charging valve gasket)", 1, 15, 1200, 13, 15, 7),
                ("Main body, bowl, vacuum transfer pipes, CIP nozzles, chopper motor housing, hose pipes", 1, 150, 1700, 60, 150, 75),
                ("Elevator assembly", 1, 20, 1500, 10, 15, 10),
                ("Co-mill assembly (wing nut, blade, cone hub, screen, motor housing, discharge hopper)", 1, 10, 3000, 30, 19, 10),
                ("Lid (charging valves, vent filter, view window glass assembly)", 1, 75, 5000, 32, 75, 45),
                ("Clamps, bolts, nuts", 1, 10, 1500, 10, 8, 8),
            ],
            "SMG-150L": [
                ("Discharge port assembly", 1, 20, 1500, 20, 20, 20),
                ("Platform, guards, staircase, machine base, CIP system, Impeller, vacuum transfer pipes, SS wire conduits", 1, 20, 2000, 30, 20, 20),
                ("Chopper blade and hub cone", 1, 10, 1000, 10, 10, 10),
                ("Agitator blade, Cone and wing bolt", 1, 10, 1000, 25, 10, 10),
                ("Lid (lid, lid gasket and product charging valve gasket)", 1, 15, 1000, 30, 15, 15),
                ("Main body, bowl, CIP nozzles, and chopper motor housing", 1, 100, 1500, 60, 120, 100),
                ("Co-mill assembly (wing nut, comill blade, cone hub, screen, motor housing, discharge hopper)", 1, 15, 1600, 40, 15, 15),
                ("Lid (charging valves, vent filter, view window glass assembly)", 1, 20, 2000, 30, 20, 20),
                ("Spray gun assembly (binder transfer pipe, peristaltic pump)", 1, 10, 500, 25, 10, 10),
                ("Clamps, bolts, nuts", 1, 10, 1000, 25, 10, 10),
            ],
        },
    },
    "Fluid Bed Equipment (FBE)": {
        "sop": "OI-05",
        "models": {
            "FBE-1300L": [
                ("External surface of Retarding Chamber, explosion duct, actuators, air inlet, charging valve, outlet ducts", 1, 150, 2000, 20, 150, 120),
                ("Inside surface of expansion chamber and filter housing unit", 1, 140, 2500, 20, 86, 60),
                ("Lower plenum (inlet air duct along with damper, gasket)", 1, 85, 1000, 10, 78, 80),
                ("Product Bowl, product container mesh, dutch woven sieve, discharge valve assembly, trolley", 1, 70, 1000, 20, 68, 45),
                ("Gaskets", 1, 10, 500, 2, 10, 10),
                ("Spraying gun assembly", 1, 34, 100, 5, 34, 20),
                ("Filter frame, filter suspending ring, lock, flap and carbine hooks", 1, 56, 500, 10, 38, 38),
                ("View window glass, product temperature probe, sampling port, ring, sieve plate, nuts and screws", 1, 80, 500, 15, 60, 42),
                ("Hose pipe assembly", 1, 5, 200, 5, 5, 5),
            ],
            "FBE-800L": [
                ("External surface of Retarding Chamber, explosion duct, actuators, air inlet", 1, 100, 1000, 10, 100, 50),
                ("Inside surface of expansion chamber and filter housing unit", 1, 100, 750, 10, 60, 40),
                ("Lower plenum (inlet air duct along with damper, gasket)", 1, 40, 100, 2, 35, 35),
                ("Product Bowl, product container mesh, dutch woven sieve and trolley", 1, 40, 100, 2, 35, 35),
                ("Gaskets", 1, 5, 75, 1, 5, 5),
                ("Spraying gun assembly", 1, 20, 50, 2, 20, 15),
                ("Filter frame, filter suspending ring, lock and carbine hooks", 1, 20, 200, 2, 15, 15),
                ("View window glass, product temperature probe, sampling port, ring, sieve plate, nuts and screws", 1, 20, 200, 4, 15, 12),
            ],
            "FBE-125L (MFBE-05)": [
                ("Inside surface of expansion chamber and filter housing unit", 1, 40, 300, 40, 40, 35),
            ],
        },
    },
    "Gerteis Roll Compactor (Macro-Pactor)": {
        "sop": "OI-30",
        "models": {
            "Macro-Pactor": [
                ("Inlet hopper", 1, 10, 2000, 15, 5, 3),
                ("Telescopic agitator", 1, 5, 1000, 10, 3, 2),
                ("Feed hopper", 1, 10, 2000, 15, 5, 3),
                ("Small quantity funnel assembly", 1, 5, 1000, 15, 3, 2),
                ("Feed auger", 1, 5, 1000, 10, 3, 2),
                ("Tamp auger", 2, 10, 2000, 20, 5, 3),
                ("Diverter tube assembly and filter element", 1, 5, 1000, 10, 3, 2),
                ("Side seal assembly, SS shoulders, Teflon strips, silicon rods, POM side plates, sintered metal filter", 1, 5, 1000, 25, 3, 2),
                ("Scrappers and scrapper accessories", 2, 10, 2000, 30, 5, 3),
                ("Press rollers and roller accessories", 2, 20, 4000, 30, 10, 10),
                ("Deflector plate of granulator", 2, 5, 1000, 10, 5, 3),
                ("Screen", 1, 10, 2000, 10, 5, 3),
                ("Screen support and accessories", 1, 10, 2000, 10, 5, 3),
                ("Positioning tube", 1, 5, 1000, 10, 3, 2),
                ("Granules sample drawer", 1, 5, 1000, 5, 3, 2),
                ("Granulator and accessories", 2, 10, 2000, 15, 5, 5),
                ("POM filters and accessories", 1, 5, 1000, 10, 5, 2),
                ("Outlet funnel / discharge hopper and accessories", 1, 10, 2000, 20, 5, 2),
                ("Front door and accessories", 1, 10, 2000, 10, 5, 3),
                ("Process housing", 1, 40, 8000, 40, 20, 15),
                ("Air circulation pipes", 1, 10, 2000, 10, 5, 5),
                ("Lip seals, Teflon rods, silicon strips", 1, 5, 1000, 15, 5, 5),
                ("Beneath the equipment", 1, 20, 4000, 20, 10, 10),
            ],
        },
    },
    "Conical Sieve Mill": {
        "sop": "OI-36",
        "models": {
            "Conical Sieve Mill": [
                ("In feed chute and its clamp / Frewitt Charging Cone", 1, 34, 500, 20, 30, 28),
                ("Impeller / rotor and screw", 1, 28, 450, 15, 26, 25),
                ("Impeller shaft", 1, 16, 300, 10, 15, 12),
                ("Screen", 1, 3, 300, 10, 3, 2),
                ("O-ring", 1, 12, 200, 10, 12, 10),
                ("Clamps", 1, 7, 200, 20, 7, 5),
            ],
        },
    },
    "Quadro Co-Mill U 20": {
        "sop": "OI-32",
        "models": {
            "Quadro U 20": [
                ("Gearbox and grid mesh", 1, 0, 0, 20, 0, 0),
                ("Housing body", 1, 0, 0, 15, 0, 0),
                ("Screen", 1, 0, 0, 10, 0, 0),
                ("Impeller and screw", 1, 0, 0, 6, 0, 0),
            ],
        },
    },
}


def components(model_key):
    """Return the component dicts for a model key like 'SMG-1300L'."""
    for group in EQUIPMENT.values():
        if model_key in group["models"]:
            out = []
            for (name, qty, p1, teepol, scrub, p2, pure) in group["models"][model_key]:
                out.append({"name": name, "qty": qty, "p1": p1, "teepol": teepol,
                            "scrub": scrub, "p2": p2, "pure": pure})
            return out
    raise KeyError(model_key)


def to_hhmm(minutes):
    m = int(round(minutes)) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def schedule(tasks, people=1, start_min=0):
    """Assign tasks to people and lay them out from start_min.

    Longest validated scrubbing time first, each task goes to the person with
    the least load. Every task keeps its validated duration, so more people
    only shortens the overall finish.
    """
    if not tasks:
        return {"assignments": [], "makespan": 0, "finish": to_hhmm(start_min),
                "people": 0, "total_min": 0}
    people = max(1, min(int(people), len(tasks)))
    loads = [0] * people
    owner = {}
    for i in sorted(range(len(tasks)), key=lambda k: -tasks[k]["scrub"]):
        p = min(range(people), key=lambda j: loads[j])
        owner[i] = p
        loads[p] += tasks[i]["scrub"]

    assignments = []
    cursor = [start_min] * people
    for i in sorted(range(len(tasks))):
        p = owner[i]
        dur = tasks[i]["scrub"]
        assignments.append({"index": i, "name": tasks[i]["name"], "person": p + 1,
                            "start": to_hhmm(cursor[p]), "end": to_hhmm(cursor[p] + dur),
                            "duration": dur})
        cursor[p] += dur
    makespan = max(loads) if loads else 0
    return {"assignments": assignments, "makespan": makespan,
            "finish": to_hhmm(start_min + makespan), "people": people,
            "total_min": sum(t["scrub"] for t in tasks)}


def water_totals(tasks):
    return {
        "potable1_kg": round(sum(t["p1"] for t in tasks), 1),
        "teepol_ml": round(sum(t["teepol"] for t in tasks), 1),
        "potable2_kg": round(sum(t["p2"] for t in tasks), 1),
        "purified_kg": round(sum(t["pure"] for t in tasks), 1),
    }