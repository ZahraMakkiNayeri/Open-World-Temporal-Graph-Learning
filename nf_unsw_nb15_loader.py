# ============================================================================
# NF-UNSW-NB15-v2  data loader  —  drop-in replacement for the
# "Section 2 – Data Loading & Preprocessing" CSV-load cell (cell ~6/7) of
# TGN_ULTRA_ZeroDay_v3_fixed.ipynb
#
# The NF-UNSW-NB15-v2 schema already matches the model's expected columns
# (DetectTime, FlowCount, SourceIP, TargetIP, Category, Proto, Port), so the
# entire downstream pipeline (preprocess -> get_data -> model -> evaluate)
# works UNCHANGED. Paste this cell in place of the original file-loading cell,
# then continue from "Section 3" as normal.
#
# Run AFTER the imports cell (needs pandas as pd, numpy as np).
# ============================================================================

# ---- Configuration -----------------------------------------------------------
NF_PATH        = '/content/drive/My Drive/NF-UNSW-NB15-v2.csv'  # adjust if needed
INCLUDE_BENIGN = True        # keep 'Benign' as a known class (realistic IDS setting)
BENIGN_CAP     = 100_000     # subsample benign (2.3M total) to keep training tractable
ATTACK_CAP     = None        # optional cap per attack category (None = keep all)
ZERO_DAY_CATEGORY = 'DoS'    # held-out unseen attack; try 'Backdoor','Shellcode','Worms'
RANDOM_STATE   = 42

# ---- Load --------------------------------------------------------------------
df = pd.read_csv(NF_PATH)
# DetectTime may load as string; ensure datetime (preprocess calls .timestamp())
if not np.issubdtype(df['DetectTime'].dtype, np.datetime64):
    df['DetectTime'] = pd.to_datetime(df['DetectTime'])

print("Raw class distribution:")
print(df['Category'].value_counts())

# ---- Subsample to a manageable, balanced-ish stream --------------------------
parts = []
for cat, grp in df.groupby('Category'):
    if cat == 'Benign':
        if not INCLUDE_BENIGN:
            continue
        n = min(BENIGN_CAP, len(grp))
        parts.append(grp.sample(n=n, random_state=RANDOM_STATE))
    else:
        if ATTACK_CAP is not None and len(grp) > ATTACK_CAP:
            parts.append(grp.sample(n=ATTACK_CAP, random_state=RANDOM_STATE))
        else:
            parts.append(grp)

df = (pd.concat(parts)
        .sort_values('DetectTime')       # chronological — required by TGN memory
        .reset_index(drop=True))

# ---- Sanity checks -----------------------------------------------------------
assert ZERO_DAY_CATEGORY in df['Category'].unique(), \
    f"'{ZERO_DAY_CATEGORY}' not present after subsampling"
n_zd = int((df['Category'] == ZERO_DAY_CATEGORY).sum())

print("\nAfter subsampling:")
print(df['Category'].value_counts())
print(f"\nTotal interactions : {len(df):,}")
print(f"Unique hosts       : {pd.concat([df.SourceIP, df.TargetIP]).nunique():,}")
print(f"Held-out zero-day  : '{ZERO_DAY_CATEGORY}'  ({n_zd:,} interactions)")
print(f"Known categories   : "
      f"{[c for c in df['Category'].unique() if c != ZERO_DAY_CATEGORY]}")

# NOTE:
#  - The next cell in the notebook sets ZERO_DAY_CATEGORY from value_counts()[-1].
#    DELETE / comment that line so the explicit ZERO_DAY_CATEGORY above is used.
#  - Everything from "Section 3 – Data Class & Train/Val/Test Splits" onward
#    (preprocess, run_pipeline, get_data, MotifDescriptor, model, training,
#    evaluation, ablations, metrics summary) runs without modification.
