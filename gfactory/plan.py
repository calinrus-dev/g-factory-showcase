"""Validate a cut-only timeline using integer microseconds."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


class PlanError(ValueError):
    """A manifest does not satisfy the timeline contract."""


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise PlanError(f"{name} must be an integer >= {minimum}")
    return value


def keys(value, expected, name):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise PlanError(f"{name} must contain exactly: {', '.join(expected)}")


@dataclass(frozen=True)
class Cut:
    start_us: int
    end_us: int


@dataclass(frozen=True)
class ClipPlan:
    source_duration_us: int
    cuts: tuple[Cut, ...]
    intro_us: int = 0
    outro_us: int = 0
    max_duration_us: int = 900_000_000

    def __post_init__(self):
        integer(self.source_duration_us, "source_duration_us", 1)
        integer(self.intro_us, "intro_us")
        integer(self.outro_us, "outro_us")
        integer(self.max_duration_us, "max_duration_us", 1)
        if type(self.cuts) is not tuple or not self.cuts:
            raise PlanError("cuts must be a non-empty tuple")
        for cut in self.cuts:
            if not isinstance(cut, Cut):
                raise PlanError("each cut must be a Cut")
            integer(cut.start_us, "start_us")
            integer(cut.end_us, "end_us", 1)
            if not cut.start_us < cut.end_us <= self.source_duration_us:
                raise PlanError("cut must satisfy 0 <= start < end <= source duration")
        if self.duration_us > self.max_duration_us:
            raise PlanError("timeline exceeds maximum duration including intro/outro")

    @property
    def duration_us(self):
        return self.intro_us + sum(c.end_us - c.start_us for c in self.cuts) + self.outro_us

    @classmethod
    def from_dict(cls, data):
        keys(
            data,
            ["version", "source_duration_us", "cuts", "intro_us", "outro_us", "max_duration_us"],
            "manifest",
        )
        if type(data["version"]) is not int or data["version"] != 1:
            raise PlanError("unsupported manifest version")
        if not isinstance(data["cuts"], list):
            raise PlanError("cuts must be an array")
        cuts = []
        for cut in data["cuts"]:
            keys(cut, ["start_us", "end_us"], "cut")
            cuts.append(Cut(cut["start_us"], cut["end_us"]))
        return cls(
            data["source_duration_us"],
            tuple(cuts),
            data["intro_us"],
            data["outro_us"],
            data["max_duration_us"],
        )

    def report(self):
        cursor = self.intro_us
        mapped = []
        for cut in self.cuts:
            end = cursor + cut.end_us - cut.start_us
            mapped.append(
                {
                    "source_start_us": cut.start_us,
                    "source_end_us": cut.end_us,
                    "timeline_start_us": cursor,
                    "timeline_end_us": end,
                }
            )
            cursor = end
        return {
            "kind": "plan-only",
            "duration_us": self.duration_us,
            "cuts": mapped,
            "intro_us": self.intro_us,
            "outro_us": self.outro_us,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        plan = ClipPlan.from_dict(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"Invalid plan: {exc}\n")
    print(json.dumps(plan.report(), indent=2))


if __name__ == "__main__":
    main()
