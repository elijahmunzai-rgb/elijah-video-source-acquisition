# Exact original source requirements

The October 19 list is frozen at 318 **repositories**, not necessarily 318 discrete self-contained agent skills. The next day the list changed, so pin the snapshot for repeatability.

The old ZIP-archive downloader (`engine/source_import_318.py`) is retained as a fast archive fetcher but does **not** prove complete Git LFS/submodule acquisition. Prefer `engine/source_import_full_318.py` and preserve all checked-out original source files and commit metadata. The new script explicitly enumerates sha256 for all files and checks for missing submodules or unresolved LFS pointer files.

Limitations: Git repositories may be deleted, private, large, or include copyrighted/contractually restricted materials. All code must remain provenance-tagged and no external dependencies, closed-source models or paid rendering engines are magically included with Git source. A verification report must distinguish every outcome.
