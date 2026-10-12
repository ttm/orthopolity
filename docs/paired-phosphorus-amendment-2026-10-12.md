# Pre-response amendment: remove an unavailable volume comparator

**12 October 2026; revision 2.** The original local freeze is `83a8c36`.
Its first execution stopped at a missing `Volume_um3` field while building the
High-P calibration sample. The implementation had computed its phosphorus mean
internally, but no numerical quota, volume, bulk stock or cell-count value was
returned to the analyst. Neither population count was converted to a number,
no prediction was made, and no output result file was produced. The traceback
and stop are recorded in
`data/paired-phosphorus/2026-10-12/initial-attempt-stop.json`.

The initial protocol's stop condition was followed. The source audit had checked
phosphorus completeness and identities but had not checked completeness of the
optional volume comparator before freezing. This is a design oversight, not
evidence about the phosphorus prediction. Future source audits must check every
required predictor before freezing a runnable design.

This separately committed amendment removes the constant-phosphorus-density
volume comparator and its volume input. It retains the **same two cultures,
same identity/completeness gate, same quota and stock variables, same fixed-cost
and measured-cost predictions, same raw accounting diagnostic, same accuracy
target, and same limited inference scope**. No mean is computed from just the
cells with measured volume, and metadata biovolume constants are not substituted.
Thus the two cost predictions do not acquire an additional assumption or target
fit to bypass the volume problem. This decision precedes exposure of any count
result. The first protocol remains in place to document the stopped design;
this amendment governs the second execution, whose commit is recorded separately.
