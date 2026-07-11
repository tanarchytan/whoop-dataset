# Data dictionary

What the columns in a WHOOP export mean. **Column names and units can vary slightly between export
versions** — treat this as a guide, not a rigid schema. Times are typically ISO‑8601 with the
account's timezone; a `Cycle timezone` / offset column usually accompanies them.

> The `journal_entries.csv` file is intentionally **not** part of this dataset and is not documented
> here — it holds free‑text behaviour data and must never be contributed.

## `physiological_cycles.csv`

One row per WHOOP "cycle" (roughly a day, wake‑to‑wake). Combines recovery, strain, and a sleep summary.

| Column (typical) | Meaning |
|---|---|
| `Cycle start time`, `Cycle end time` | Cycle bounds |
| `Cycle timezone` | Timezone/offset for the timestamps |
| `Recovery score %` | Daily recovery (0–100) |
| `Resting heart rate (bpm)` | RHR for the cycle |
| `Heart rate variability (ms)` | HRV (RMSSD), milliseconds |
| `Skin temp (celsius)` | Skin temperature |
| `Blood oxygen %` | SpO₂ (4.0/5.0/MG) |
| `Day Strain` | Cardiovascular strain (0–21) |
| `Energy burned (cal)` | Calories |
| `Max HR (bpm)`, `Average HR (bpm)` | Heart‑rate extremes/mean |
| `Sleep onset`, `Wake onset` | Sleep bounds for the cycle |
| `Sleep performance %` | Sleep vs. need |
| `Respiratory rate (rpm)` | Breaths per minute during sleep |
| `Asleep duration (min)`, `In bed duration (min)` | Sleep/time‑in‑bed |
| `Light sleep duration (min)`, `Deep (SWS) duration (min)`, `REM duration (min)`, `Awake duration (min)` | Sleep stages |
| `Sleep need (min)`, `Sleep debt (min)` | Need / accumulated debt |
| `Sleep efficiency %`, `Sleep consistency %` | Sleep quality metrics |

## `sleeps.csv`

One row per sleep (including naps). Same sleep fields as above, at the per‑sleep grain.

| Column (typical) | Meaning |
|---|---|
| `Cycle start time`, `Cycle end time`, `Cycle timezone` | Owning cycle |
| `Sleep onset`, `Wake onset` | Sleep bounds |
| `Sleep performance %`, `Sleep efficiency %`, `Sleep consistency %` | Quality metrics |
| `Respiratory rate (rpm)` | Breaths/min |
| `Asleep duration (min)`, `In bed duration (min)` | Durations |
| `Light sleep duration (min)`, `Deep (SWS) duration (min)`, `REM duration (min)`, `Awake duration (min)` | Stages |
| `Sleep need (min)`, `Sleep debt (min)` | Need / debt |
| `Nap` | Whether this sleep was a nap (boolean) |

## `workouts.csv`

One row per logged workout/activity.

| Column (typical) | Meaning |
|---|---|
| `Cycle start time`, `Cycle end time`, `Cycle timezone` | Owning cycle |
| `Workout start time`, `Workout end time` | Activity bounds |
| `Duration (min)` | Length |
| `Activity name` | Sport/activity label |
| `Activity Strain` | Strain for the activity (0–21) |
| `Energy burned (cal)` | Calories |
| `Max HR (bpm)`, `Average HR (bpm)` | HR extremes/mean |
| `HR Zone 1–5 %` (or minutes) | Time distribution across HR zones |
| `GPS enabled` | Whether GPS was on |
| `Distance (meters)` | Distance (GPS activities) |
| `Altitude gain (meters)`, `Altitude change (meters)` | Elevation |

## Device context

Which WHOOP generation produced the data is the **device folder** the contribution lives in
(`contributions/<device>/…`) and is mirrored in `metadata.yml` (`device:`), not in the CSVs. Some
columns only appear on newer straps (e.g. `Blood oxygen %`, `Skin temp` from 4.0 onward), so expect
blanks where a generation didn't measure something.
