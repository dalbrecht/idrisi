# Coordinates NaN/Infinity Explicit Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Coordinates validation explicitly reject NaN and Infinity values with clear error messages, rather than relying on accidental comparison semantics.

**Architecture:** Add `math.isnan` and `math.isinf` checks to `Coordinates.__post_init__` before the range checks. Existing tests from PR2 already verify this behavior passes — this change makes the rejection intentional and improves error messages.

**Tech Stack:** Python stdlib `math` module

**Spec:** `docs/superpowers/specs/2026-04-07-test-hardening-design.md` (domain edge cases section)

---

**Important context:**
- Current behavior: `Coordinates(float('nan'), 0)` raises `ValueError("Latitude must be between -90 and 90, got nan")` because `not (-90 <= nan <= 90)` evaluates to `True` (NaN comparisons always return False). This is accidental — it works but the error message is misleading.
- Tests in `tests/domain/test_value_objects.py` already verify NaN/Infinity rejection (added in PR2 Task 1). Those tests match on `"Latitude"` or `"Longitude"` in the error message, so the new explicit messages must still contain those words.
- `Coordinates` is a frozen dataclass, so `__post_init__` is the only place to validate.

---

### Task 1: Add explicit NaN/Infinity validation (TDD)

**Files:**
- Modify: `src/voyages/domain/value_objects.py`
- Modify: `tests/domain/test_value_objects.py`

- [ ] **Step 1: Write a failing test that checks the error message for NaN**

The existing `test_nan_latitude_raises` matches on `"Latitude"` which already passes. Add a more specific test that verifies the error message explicitly mentions NaN. Append to `TestCoordinates` in `tests/domain/test_value_objects.py`:

```python
    def test_nan_latitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="NaN"):
            Coordinates(latitude=float("nan"), longitude=0.0)

    def test_inf_latitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="infinite"):
            Coordinates(latitude=float("inf"), longitude=0.0)

    def test_nan_longitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="NaN"):
            Coordinates(latitude=0.0, longitude=float("nan"))

    def test_inf_longitude_error_message_is_explicit(self) -> None:
        with pytest.raises(ValueError, match="infinite"):
            Coordinates(latitude=0.0, longitude=float("inf"))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/domain/test_value_objects.py::TestCoordinates::test_nan_latitude_error_message_is_explicit -v
```

Expected: FAIL — current error message says "must be between -90 and 90" not "NaN".

- [ ] **Step 3: Add explicit NaN/Infinity checks to Coordinates**

In `src/voyages/domain/value_objects.py`, add `import math` at the top and update `__post_init__`:

```python
import math

# ... (existing constants) ...

@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if math.isnan(self.latitude) or math.isinf(self.latitude):
            msg = f"Latitude must be a finite number, got {'NaN' if math.isnan(self.latitude) else 'infinite'}"
            raise ValueError(msg)
        if math.isnan(self.longitude) or math.isinf(self.longitude):
            msg = f"Longitude must be a finite number, got {'NaN' if math.isnan(self.longitude) else 'infinite'}"
            raise ValueError(msg)
        if not _LAT_MIN <= self.latitude <= _LAT_MAX:
            msg = f"Latitude must be between -90 and 90, got {self.latitude}"
            raise ValueError(msg)
        if not _LON_MIN <= self.longitude <= _LON_MAX:
            msg = f"Longitude must be between -180 and 180, got {self.longitude}"
            raise ValueError(msg)
```

- [ ] **Step 4: Update existing NaN/Infinity tests to match new messages**

The existing tests from PR2 use `match="Latitude"` and `match="Longitude"`. The new messages still contain those words ("Latitude must be a finite number"), so they should still pass. Verify:

```bash
uv run pytest tests/domain/test_value_objects.py -v
```

Expected: ALL tests pass — both old and new.

- [ ] **Step 5: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests pass. No regressions.

- [ ] **Step 6: Commit**

```bash
git add src/voyages/domain/value_objects.py tests/domain/test_value_objects.py
git commit -m "fix(domain): explicitly reject NaN and Infinity in Coordinates

Previously NaN/Infinity were rejected accidentally by comparison
semantics. Now explicitly checked with math.isnan/isinf for clear
error messages."
```

---

### Task 2: Push and create PR

- [ ] **Step 1: Push and create PR**

```bash
git push -u origin <branch-name>
gh pr create \
  --title "fix(domain): explicitly reject NaN/Infinity in Coordinates validation" \
  --body "$(cat <<'EOF'
## Summary

- Add explicit `math.isnan()` and `math.isinf()` checks to `Coordinates.__post_init__`
- Clearer error messages: "Latitude must be a finite number, got NaN" instead of "Latitude must be between -90 and 90, got nan"
- NaN/Infinity checks run before range checks
- 4 new tests verify explicit error messages
- All existing tests still pass (error messages still contain "Latitude"/"Longitude")

## Context

The adversarial test review (#4) identified that NaN/Infinity rejection in Coordinates was accidental — relying on `not (-90 <= nan <= 90)` evaluating to True because NaN comparisons return False. This works but produces misleading error messages.

## Test plan

- [x] New tests verify NaN/Infinity error messages are explicit
- [x] All existing Coordinates tests still pass
- [x] Full suite passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
